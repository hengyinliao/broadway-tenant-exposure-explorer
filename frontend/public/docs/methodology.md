# Methodology

This prototype joins official City of Vancouver parcel polygons, 2025 assessment records, zoning districts and issued building permits. It calculates parcel-to-station distance in UTM Zone 10N. Permit points are associated with parcels using a small spatial tolerance and require manual verification before case-level use.

The requested pressure model weights development activity 30%, Broadway policy potential 25%, land-to-total assessed value 20%, building age 15% and station proximity 10%. Verified parcel-level Broadway policy schedules are not integrated, so the requested composite is unavailable. The optional available-data model sets the policy weight to zero and re-normalizes the remaining observed components.

The City non-market housing inventory is spatially matched as a partial, positive-evidence layer. The current extract finds 232 parcels representing 11,332 listed units. It excludes much of the private rental stock, so unmatched parcels remain Unknown. Census renter households/share, a complete purpose-built rental inventory and project-level protection applicability remain unavailable. The renter exposure score and renter-by-pressure matrix consequently remain unavailable.

The contextual rectangle follows the City's plain-language Broadway Plan extent (approximately Vine Street to Clark Drive and 1st Avenue to 16th Avenue). It is a study proxy, not a legal or policy boundary.

This tool supports descriptive spatial exploration. It does not establish that transit or planning caused displacement, predict demolition, or determine that a tenant protection policy applies to an individual property.

Created by Hengyin Liao — [LinkedIn](https://www.linkedin.com/in/hengyin-liao-0aab05245/)
