"""Build the frozen D'Coast Phase 0.6 optical-quality gate assessment."""

from __future__ import annotations

import argparse
import csv
import statistics
from datetime import date
from pathlib import Path
from typing import Any

SITES = ("cilegon-industrial-coast", "teluk-awur-jepara")
THRESHOLDS = ((50, "quality_50"), (70, "quality_70"), (80, "quality_80"))
FULL_YEARS = tuple(range(2021, 2026))
FULL_START = date(2021, 1, 1)
FULL_END = date(2025, 12, 31)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def longest_gap_days(usable_dates: list[date]) -> int | None:
    if not usable_dates:
        return None
    points = [FULL_START, *sorted(set(usable_dates)), FULL_END]
    return max((second - first).days for first, second in zip(points, points[1:]))


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for site in SITES:
        site_rows = [row for row in rows if row["site"] == site]
        full_rows = [
            row
            for row in site_rows
            if int(row["observation_date"][:4]) in FULL_YEARS
        ]
        for threshold, flag in THRESHOLDS:
            annual = {
                year: sum(
                    int(row[flag])
                    for row in full_rows
                    if int(row["observation_date"][:4]) == year
                )
                for year in FULL_YEARS
            }
            monthly = [
                sum(
                    int(row[flag])
                    for row in full_rows
                    if row["observation_date"].startswith(f"{year}-{month:02d}")
                )
                for year in FULL_YEARS
                for month in range(1, 13)
            ]
            usable_dates = [
                date.fromisoformat(row["observation_date"])
                for row in full_rows
                if int(row[flag])
            ]
            gap = longest_gap_days(usable_dates)
            all_usable = sum(int(row[flag]) for row in site_rows)
            average_annual = statistics.mean(annual.values())
            median_monthly = statistics.median(monthly)
            output.append(
                {
                    "site": site,
                    "threshold_pct": threshold,
                    "all_period_observations": len(site_rows),
                    "all_period_usable": all_usable,
                    "all_period_rejection_pct": f"{100 * (1 - all_usable / len(site_rows)):.3f}",
                    **{f"usable_{year}": annual[year] for year in FULL_YEARS},
                    "full_year_average_usable": f"{average_annual:.3f}",
                    "full_year_median_usable_per_month": f"{median_monthly:.3f}",
                    "full_year_longest_gap_days": "" if gap is None else gap,
                    "gate_median_month_pass": int(median_monthly >= 1),
                    "gate_average_year_pass": int(average_annual >= 18),
                    "gate_max_gap_pass": int(gap is not None and gap <= 60),
                }
            )
    return output


def build_seasonality(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for site in SITES:
        for month in range(1, 13):
            values = [
                row
                for row in rows
                if row["site"] == site
                and int(row["observation_date"][:4]) in FULL_YEARS
                and int(row["observation_date"][5:7]) == month
            ]
            output.append(
                {
                    "site": site,
                    "month": month,
                    "observations": len(values),
                    "usable_50": sum(int(row["quality_50"]) for row in values),
                    "usable_70": sum(int(row["quality_70"]) for row in values),
                    "usable_80": sum(int(row["quality_80"]) for row in values),
                    "median_clear_water_fraction": (
                        f"{statistics.median(float(row['clear_water_fraction']) for row in values):.6f}"
                        if values
                        else ""
                    ),
                }
            )
    return output


def summary_row(summary: list[dict[str, Any]], site: str, threshold: int) -> dict[str, Any]:
    return next(
        row
        for row in summary
        if row["site"] == site and row["threshold_pct"] == threshold
    )


def build_report(
    rows: list[dict[str, str]],
    summary: list[dict[str, Any]],
    seasonality: list[dict[str, Any]],
) -> str:
    c50 = summary_row(summary, SITES[0], 50)
    c70 = summary_row(summary, SITES[0], 70)
    c80 = summary_row(summary, SITES[0], 80)
    t50 = summary_row(summary, SITES[1], 50)
    t70 = summary_row(summary, SITES[1], 70)
    t80 = summary_row(summary, SITES[1], 80)
    c_months = [row for row in seasonality if row["site"] == SITES[0]]
    t_months = [row for row in seasonality if row["site"] == SITES[1]]
    c_peak = max(c_months, key=lambda row: row["usable_50"])
    t_peak = max(t_months, key=lambda row: row["usable_70"])
    processed = sorted({row["processed_at_utc"] for row in rows})
    provenance = sorted({row["api_provenance"] for row in rows})
    return f"""# D'Coast Phase 0.6 Clear-Water Assessment

Assessment scope: 2021-2025 full years plus 2026 partial through 24 July

Verdict: **NO_GO_CILEGON_FOR_PHASE1**

Benchmark disposition: **RETAIN_TELUK_AWUR_AS_CONDITIONAL_TECHNICAL_BENCHMARK**

## What was measured

The CDSE Statistical API produced one daily Sentinel-2 L2A least-cloud mosaic
for each unique catalogue site-date. The final table contains {len(rows)}
site-date rows representing {sum(int(row["source_acquisition_count"]) for row in rows)}
source acquisitions. The diagnostic grid is approximately 60 m over the
water-side screening AOIs.

This is an optical feasibility screen. SCL class 6 frequency is not a pollution
measurement, water-quality label, or source-attribution method. Low SCL6
support can also reflect turbid or shallow water, coastal mixing, glint,
adjacency, masking behaviour, or an unsuitable AOI.

## Frozen 70% gate

| Site | Median usable/month | Required | Average usable/full year | Required | Longest gap | Required | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Cilegon | {c70["full_year_median_usable_per_month"]} | >=1 | {c70["full_year_average_usable"]} | >=18 | no usable dates | <=60 days | FAIL 3/3 |
| Teluk Awur | {t70["full_year_median_usable_per_month"]} | >=1 | {t70["full_year_average_usable"]} | >=18 | {t70["full_year_longest_gap_days"]} days | <=60 days | PASS 2/3 |

Cilegon has no observation reaching the preregistered 70% clear-water
threshold. It cannot be promoted by relaxing the threshold after seeing this
result. Teluk Awur has {t70["all_period_usable"]} quality-70 dates, but its
{t70["full_year_longest_gap_days"]}-day maximum full-period gap exceeds the
60-day gate.

## Threshold sensitivity

| Site | Threshold | Usable dates, all period | Rejection | Full-year average | Median/month | Longest full-period gap |
|---|---:|---:|---:|---:|---:|---:|
| Cilegon | 50% | {c50["all_period_usable"]} | {c50["all_period_rejection_pct"]}% | {c50["full_year_average_usable"]} | {c50["full_year_median_usable_per_month"]} | {c50["full_year_longest_gap_days"]} days |
| Cilegon | 70% | {c70["all_period_usable"]} | {c70["all_period_rejection_pct"]}% | {c70["full_year_average_usable"]} | {c70["full_year_median_usable_per_month"]} | no usable dates |
| Cilegon | 80% | {c80["all_period_usable"]} | {c80["all_period_rejection_pct"]}% | {c80["full_year_average_usable"]} | {c80["full_year_median_usable_per_month"]} | no usable dates |
| Teluk Awur | 50% | {t50["all_period_usable"]} | {t50["all_period_rejection_pct"]}% | {t50["full_year_average_usable"]} | {t50["full_year_median_usable_per_month"]} | {t50["full_year_longest_gap_days"]} days |
| Teluk Awur | 70% | {t70["all_period_usable"]} | {t70["all_period_rejection_pct"]}% | {t70["full_year_average_usable"]} | {t70["full_year_median_usable_per_month"]} | {t70["full_year_longest_gap_days"]} days |
| Teluk Awur | 80% | {t80["all_period_usable"]} | {t80["all_period_rejection_pct"]}% | {t80["full_year_average_usable"]} | {t80["full_year_median_usable_per_month"]} | {t80["full_year_longest_gap_days"]} days |

Cilegon's 50% observations are concentrated seasonally; the largest pooled
full-year month count is month {c_peak["month"]} with {c_peak["usable_50"]}
dates across five years. Teluk Awur's strongest quality-70 month is month
{t_peak["month"]} with {t_peak["usable_70"]} dates across five years.

## Decision

The Phase 0.5 conditional operational lock on Cilegon is not upgraded. It is
closed as **NO-GO for the current Phase 1 optical pipeline** because every
frozen 70% cadence gate fails and reusable georeferenced optical validation is
still unsecured.

Teluk Awur remains useful for method development because its median monthly
cadence and annual volume pass, and the published TSS study is the strongest
technical lead. It is not automatically promoted to the industrial
operational pilot: the 120-day gap fails the frozen cadence gate, the AOI is
provisional, and the georeferenced sample table/data permission is not in the
project.

## Next admissible action

1. Do not bulk-download imagery or train a model for Cilegon.
2. Review both polygons against BIG coastline data and inspect representative
   SCL/true-colour dates with a coastal-water expert.
3. Secure georeferenced, dated Teluk Awur TSS observations or author
   collaboration before quantitative validation.
4. Either redesign the optical-quality definition with a preregistered
   coastal/turbid-water mask or evaluate a different industrial pilot from
   scratch. Do not lower the 70% threshold on this same evidence.
5. Require a new human approval gate before Phase 1.

## Provenance

- Processing timestamp: `{", ".join(processed)}`
- API method: `{provenance[0] if len(provenance) == 1 else provenance}`
- Primary artifacts:
  `sentinel2_observation_quality.csv`,
  `sentinel2_monthly_availability.csv`,
  `phase06_site_quality_summary.csv`, and
  `phase06_monthly_seasonality.csv`.
"""


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--seasonality", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows = read_csv(args.quality)
    if len(rows) != 848 or {row["site"] for row in rows} != set(SITES):
        raise ValueError("Phase 0.6 quality input must contain both locked sites and 848 rows")
    if any(row["clear_water_fraction"] == "" for row in rows):
        raise ValueError("Phase 0.6 quality input is still blocked or incomplete")
    summary = build_summary(rows)
    seasonality = build_seasonality(rows)
    write_csv(args.summary, summary)
    write_csv(args.seasonality, seasonality)
    args.report.write_text(build_report(rows, summary, seasonality), encoding="utf-8")
    print(f"Wrote {len(summary)} summary rows, {len(seasonality)} seasonal rows, and {args.report}")


if __name__ == "__main__":
    main()
