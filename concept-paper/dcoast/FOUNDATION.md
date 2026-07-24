# D'Coast - Foundation Brief

Status: initial concept foundation, not an implemented or validated product.

## 1. Product in one sentence

D'Coast helps environmental inspectors turn repeated coastal observations into
explainable inspection priorities and initial sampling recommendations, while
leaving pollution confirmation and source attribution to field and laboratory
verification.

## 2. Problem being solved

Coastal industrial areas are too wide and dynamic to inspect continuously using
field sampling alone. Satellite imagery can screen a larger area, but a raw
change map is not yet an operational decision. Inspectors still need to know:

- whether a change is unusual for that location and season;
- whether it persists across valid observations;
- whether natural conditions may explain it;
- where field verification should begin.

D'Coast is positioned between wide-area observation and official verification.
It does not replace either inspection or laboratory analysis.

## 3. Primary users

- environmental-agency analysts who review coastal conditions;
- inspectors who decide which alerts require follow-up;
- field teams who need an initial sampling plan;
- laboratories and supervisors who need one traceable case record.

The first user to design for is the inspector reviewing a new observation.

## 4. Smallest credible MVP

The first version should cover only one coastal industrial pilot area and use:

1. Sentinel-2 observations as the main imagery source;
2. rainfall as the minimum environmental context;
3. a historical and seasonal baseline for each grid or zone;
4. explainable anomaly polygons and a Coastal Anomaly Score;
5. three sampling roles:
   - anomaly core;
   - boundary or down-current point;
   - reference point;
6. a map-based review screen with human approval and a simple case record.

Sentinel-3, Landsat, buoy data, official outfall data, detailed current models,
and additional agency datasets are useful extensions, not MVP dependencies.

## 5. Initial system flow

```text
valid observation
    -> quality control and water preprocessing
    -> optical features
    -> comparison with local historical baseline
    -> environmental-context adjustment
    -> grouped anomaly area
    -> priority score and sampling suggestions
    -> human review
    -> field and laboratory verification
    -> feedback stored with the case
```

## 6. First model baseline

Start with an explainable statistical anomaly baseline rather than a complex
model:

- historical median for the same location and comparable season;
- interquartile range or another robust scale estimate;
- normalized deviation for selected optical indicators;
- neighboring abnormal pixels grouped into one candidate area;
- persistence treated as additional evidence, not as proof of pollution.

Isolation Forest can be a later comparison. It should not become the default
until the statistical baseline, data quality, and validation data are stable.

## 7. Product output

One alert package should contain:

- observation date and quality;
- anomaly location, boundary, and affected area;
- comparison with the historical baseline;
- optical indicators that changed;
- environmental context considered;
- score components and priority level;
- proposed sampling roles and inspection window;
- reviewer decision and later verification result.

The Coastal Anomaly Score represents inspection priority. It is not a pollution
probability, legal standard, or attribution of responsibility.

## 8. First validation questions

Before expanding the product, the pilot must answer:

1. Are there enough cloud-free, usable observations for the selected area?
2. Can the pipeline reproduce a stable seasonal baseline?
3. Do known or expert-reviewed events appear as meaningful anomalies?
4. How often do rainfall, shallow water, sediment, or processing artifacts
   create false alerts?
5. Are the suggested sampling points useful to an inspector?
6. Does D'Coast reduce the area and time needed to prepare an inspection brief?

No accuracy, cost-saving, detection-rate, or six-hour processing claim should be
presented as achieved until it is measured in the pilot.

## 9. Non-negotiable boundaries

- Never describe an alert as proof of pollution.
- Never infer a responsible company from satellite imagery alone.
- Withhold or visibly downgrade alerts when observation quality is insufficient.
- Keep score components and natural-context adjustments visible to reviewers.
- Require human approval before an alert becomes an inspection recommendation.
- Preserve the reviewer decision, sampling changes, and verification outcome.

## 10. Next smallest useful step

Choose one candidate pilot area and perform a data-feasibility check only:

- available Sentinel-2 history;
- seasonal cloud and valid-observation coverage;
- coastline and monitoring boundary;
- available rainfall context;
- at least one source of field, laboratory, inspection, or expert validation.

Do not build the full model or dashboard until this feasibility check identifies
a pilot area with enough usable history and a realistic validation source.
