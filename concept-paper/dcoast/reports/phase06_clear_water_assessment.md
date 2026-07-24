# D'Coast Phase 0.6 Clear-Water Assessment

Assessment scope: 2021-2025 full years plus 2026 partial through 24 July

Verdict: **NO_GO_CILEGON_FOR_PHASE1**

Benchmark disposition: **RETAIN_TELUK_AWUR_AS_CONDITIONAL_TECHNICAL_BENCHMARK**

## What was measured

The CDSE Statistical API produced one daily Sentinel-2 L2A least-cloud mosaic
for each unique catalogue site-date. The final table contains 848
site-date rows representing 858
source acquisitions. The diagnostic grid is approximately 60 m over the
water-side screening AOIs.

This is an optical feasibility screen. SCL class 6 frequency is not a pollution
measurement, water-quality label, or source-attribution method. Low SCL6
support can also reflect turbid or shallow water, coastal mixing, glint,
adjacency, masking behaviour, or an unsuitable AOI.

## Frozen 70% gate

| Site | Median usable/month | Required | Average usable/full year | Required | Longest gap | Required | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Cilegon | 0.000 | >=1 | 0.000 | >=18 | no usable dates | <=60 days | FAIL 3/3 |
| Teluk Awur | 2.000 | >=1 | 29.000 | >=18 | 120 days | <=60 days | PASS 2/3 |

Cilegon has no observation reaching the preregistered 70% clear-water
threshold. It cannot be promoted by relaxing the threshold after seeing this
result. Teluk Awur has 167 quality-70 dates, but its
120-day maximum full-period gap exceeds the
60-day gate.

## Threshold sensitivity

| Site | Threshold | Usable dates, all period | Rejection | Full-year average | Median/month | Longest full-period gap |
|---|---:|---:|---:|---:|---:|---:|
| Cilegon | 50% | 108 | 74.468% | 17.200 | 1.000 | 170 days |
| Cilegon | 70% | 0 | 100.000% | 0.000 | 0.000 | no usable dates |
| Cilegon | 80% | 0 | 100.000% | 0.000 | 0.000 | no usable dates |
| Teluk Awur | 50% | 189 | 55.529% | 33.000 | 2.000 | 75 days |
| Teluk Awur | 70% | 167 | 60.706% | 29.000 | 2.000 | 120 days |
| Teluk Awur | 80% | 153 | 64.000% | 26.400 | 2.000 | 135 days |

Cilegon's 50% observations are concentrated seasonally; the largest pooled
full-year month count is month 7 with 17
dates across five years. Teluk Awur's strongest quality-70 month is month
8 with 25 dates across five years.

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

- Processing timestamp: `2026-07-24T19:04:42+00:00`
- API method: `CDSE Statistical API; sentinel-2-l2a; SCL; approx 60m (0.00054 degree WGS84); P1D; leastCC; clear=SCL6; cloud-shadow=SCL3,8,9,10,11; water-only AOI`
- Primary artifacts:
  `sentinel2_observation_quality.csv`,
  `sentinel2_monthly_availability.csv`,
  `phase06_site_quality_summary.csv`, and
  `phase06_monthly_seasonality.csv`.
