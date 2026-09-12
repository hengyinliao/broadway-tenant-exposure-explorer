# Methodology

This project uses **redevelopment exposure**, not “displacement risk,” because the available data describe spatial conditions and administrative activity rather than tenant outcomes. Correlation and proximity do not establish that the Broadway Plan or subway caused redevelopment or displacement.

Three dimensions remain separate:

1. **Existing renter exposure** requires Census DA tenure and a confirmed rental inventory. It is currently unavailable. Unknown rental status and units remain null.
2. **Redevelopment pressure** combines observed issued-permit activity, land-value intensity, building age, policy development potential and station proximity. The parcel policy layer is unavailable; the requested default composite therefore remains null. Users can set its weight to zero to run an explicitly available-data model.
3. **Tenant protection context** is not subtracted from exposure. The study extent provides context, while parcel/project TRPP applicability remains Unknown until verified case-by-case.

Land-to-improvement ratio is `land / (land + improvement)`. Strata assessment rows are summed by land coordinate before joining parcels. Ratio and building age use winsorized 5th–95th percentile scaling. Station proximity is `100 × exp(-distance/600)`. Activity is capped at 100: 40 points per issued demolition permit, 25 per new construction permit and 10 per major alteration. These are exploratory weights, not estimated causal coefficients or redevelopment probabilities.

The contextual extent uses the City's published description—Vine Street to Clark Drive, 1st Avenue to 16th Avenue—but is a rectangular proxy, not an official Broadway Plan GIS boundary. Subway station points are sourced to the official Broadway Subway project; 400/800/1200 m circles are straight-line analytical buffers and do not claim walking catchments or future travel-time savings.

Permits are point-matched to parcels with a small tolerance. “No known matched permit” does not mean no rezoning, application, demolition intent, construction or completion. Current zoning is not historical zoning or policy uplift. Missing inputs remain missing and are never converted to zero.

The project contains no individual tenant information. It supports descriptive spatial questions and transparent hypothesis formation. It does not support claims that transit/upzoning causes displacement, that a building will be demolished, or that specific tenants will move.
