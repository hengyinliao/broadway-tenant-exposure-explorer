# Broadway Tenant Redevelopment Exposure Explorer

Created by **Hengyin Liao** · [LinkedIn](https://www.linkedin.com/in/hengyin-liao-0aab05245/)

A serious, public-facing GIS research MVP asking where transit-oriented growth, observed redevelopment activity, existing renters and tenant protections intersect in Vancouver's Broadway Corridor. It intentionally leaves unsupported dimensions unavailable.

## Run

Double-click `Start.cmd`, then open http://127.0.0.1:5190. The production build is included. For development:

```powershell
powershell -ExecutionPolicy Bypass -File dev.ps1 build
powershell -ExecutionPolicy Bypass -File dev.ps1 test
```

## Rebuild data

```powershell
python -m pip install requests shapely pyproj numpy
python scripts/build_data.py
```

The workflow downloads current official City of Vancouver parcel polygons, zoning, issued building permits and 2025 Property Tax Report, records URL/timestamp/SHA-256 manifests, clips a contextual study extent, aggregates assessments, matches permit activity and builds the web GeoJSON.

## Current evidence

- **Real:** 27,841 City parcel geometries in the contextual extent; current zoning; 2025 assessment values/year built; issued building permits from 2017 onward; official future station locations; 232 parcels matched to City non-market housing records representing 11,332 listed units.
- **Derived:** station distance/buffers, land-to-total value ratio, age/land percentiles, permit activity score, available-data pressure model.
- **Proxy:** contextual study rectangle based on the City's textual boundary description.
- **Partial:** City non-market housing inventory. It does not cover the general private rental stock, so an unmatched parcel must remain `Unknown`.
- **Unavailable:** Census DA renter households/share, confirmed purpose-built rental inventory, parcel Broadway policy schedule, project application pipeline, verified project TRPP status, replacement units and VTU spatial records.

The requested default pressure weights are 30% activity, 25% policy potential, 20% land intensity, 15% age and 10% station proximity. Because policy potential is missing, the default composite is deliberately unavailable. The UI offers an “available-data model” with policy weight zero. Protection remains separate. Renter exposure and the renter × pressure matrix remain unavailable.

The app supports eight map lenses, station and radius filters, permit filters, adjustable weights, parcel details, source confidence, a six-scene guided story, shareable URLs and filtered CSV.

## Evidence claims

Supported: parcels can have higher measured pressure under selected indicators; a parcel is associated with a matched issued permit; areas are closer to future stations; spatial relationships can be explored descriptively.

Unsupported: Broadway Subway/Plan caused displacement; a building will be demolished; tenants will lose homes; enhanced protection definitely applies; renter exposure is high/low; the results are causal or predictive.

## Priority next improvements

1. Integrate 2021 Census DA renter households/share with exact DA geometry, without transferring households to parcels.
2. Obtain an official Broadway Plan boundary/policy schedule GIS layer and build a defensible policy-potential measure.
3. Manually verify active/approved development projects, rental units affected, replacement units and TRPP status from City reports/applications.

Best LinkedIn view after clicking **Use available-data model**: all stations, 800 m, redevelopment pressure, with the right panel explaining the components. It is strong enough to show a researcher as a transparent **MVP/data-gap audit**, but not yet as a tenant exposure result; renter Census data and verified projects should come first.

See [methodology](docs/methodology.md), [data dictionary](docs/data_dictionary.md), and [limitations](docs/limitations.md).

## Publish with private source

Keep this repository private and import it into Vercel. The included `vercel.json` runs the model tests, builds `frontend`, and publishes only `frontend/dist`. Raw downloads, analysis scripts, documentation source and Git history stay in the private repository.

The browser-ready JavaScript, CSS and GeoJSON are necessarily delivered to visitors and cannot be made secret in a static web application. Moving sensitive or proprietary calculations behind an authenticated server API would be required to conceal them.
