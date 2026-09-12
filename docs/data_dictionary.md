# Data dictionary

## Added rental evidence

- `non_market_housing_projects`: matched official City project records, with name, status, occupancy year, operator, listed units and source URL.
- `rental_status`: `Confirmed non-market housing` only where an official point matches the parcel; otherwise `Unknown`.
- `existing_rental_units`: listed project units for confirmed matches; null elsewhere. Null must not be read as zero.
- `renter_exposure_score`: remains null until Census DA tenure data is integrated with its own geography and uncertainty.

| Field | Meaning / precision |
|---|---|
| parcel_id, pid, geometry | City parcel identifiers and polygon |
| year_built | 2025 Property Tax Report; median across aggregated assessment records |
| land_value, improvement_value | 2025 values summed by land coordinate |
| land_improvement_ratio | Derived land / total assessed value; not redevelopment probability |
| current_zoning | Current City zoning at parcel representative point |
| distance_station_m | Straight-line projected distance to nearest future station |
| permits | Matched relevant issued permits since 2017; administrative activity |
| development_activity_score | Derived capped evidence score |
| land_value_score | Derived winsorized percentile score |
| building_age_score | Derived winsorized percentile score |
| station_proximity_score | Derived exponential-distance score |
| policy_potential_score | Null: verified parcel policy schedule unavailable |
| redevelopment_pressure_score | Null under requested default; available when missing policy weight is zero |
| rental_status | Unknown in current MVP |
| existing_rental_units | Null in current MVP |
| renter_exposure_score | Null in current MVP |
| trpp_status | Unknown at project level |
| data_status | Real administrative source or transparent derivation status |
