# D'Coast Phase 0.7 AOI-Coastline Review

Verdict scope: **GEOMETRY SCREEN ONLY - NOT PHASE 1 AUTHORIZATION**

## Method

The two endpoints of each provisional AOI's landward `coastline_reference`
were compared with the nearest line segment in BIG's official Peta Garis
Pantai Skala 1:25.000 feature service. Before measuring, the endpoint gate was
frozen at <= 1000 metres. The service's coastline type and
source-method codes are preserved; indicative lines are not relabelled as
definitive.

### cilegon-industrial-coast

- Extracted BIG features: 5
- Coastline types: `{"highest-tide": 3, "indicative": 2}`
- Source methods: `{"lidar": 3, "ortho-photo-imagery": 2}`
- Maximum endpoint distance: 6665.67 m
- Frozen <= 1000 m endpoint gate: FAIL

- north: 1569.45 m to BIG feature 2424 (highest-tide, lidar, source year 2020).
- south: 6665.67 m to BIG feature 2424 (highest-tide, lidar, source year 2020).
### teluk-awur-jepara

- Extracted BIG features: 62
- Coastline types: `{"highest-tide": 18, "indicative": 27, "other": 17}`
- Source methods: `{"ortho-photo-imagery": 42, "terrestrial-shoreline-transect": 20}`
- Maximum endpoint distance: 2788.00 m
- Frozen <= 1000 m endpoint gate: FAIL

- north: 2788.00 m to BIG feature 40418 (indicative, ortho-photo-imagery, source year 2020).
- south: 1004.50 m to BIG feature 40263 (indicative, ortho-photo-imagery, source year 2020).

## Interpretation

Passing this endpoint screen means only that the provisional landward
reference follows the same broad coastal corridor as the BIG extract. It does
not validate the offshore width, river-mouth segmentation, control-water
assumption, monitoring jurisdiction, published sampling stations, or water
quality model. Those require domain review and georeferenced validation data.

## Source

- BIG layer: `https://geoservices.big.go.id/rbi/rest/services/GARISPANTAI/GarisPantai_25K/MapServer/0`
- Layer publication: 2022; query/output CRS: EPSG:4326.
- Bounded extracts are stored under `data/big_coastline/`.
