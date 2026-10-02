# QAYDH (القيظ) — Heat-risk intelligence for fast-growing Gulf cities

**Arab Youth Space Hackathon 2026 · Challenge 813 · Team T0049**
**Theme:** Sustainable Urban Planning & Smart Cities: *Urban Expansion, Land Use Change & Heat Risk* (SDG 3, 11, 13)

> QAYDH tells a city **where it grew**, **which districts run hottest at peak summer**, **which surface materials make them hot**, and **who is outside in that heat** (people walking to the mosque, waiting at bus stops, delivery riders and construction workers). It turns all of this into a ranked 300 m priority map that names a concrete action for each hotspot.

<!-- RESULTS_START -->
### Results: east Riyadh (Tanager scene 20250515_080954_16_4001, AOI 470 km², 1,091,324 residents)

| Claim | Metric | Validation method | Result |
|---|---|---|---|
| Our built-up map beats the official notebook-02 rule | Built-up F1 / IoU | 5-fold spatial-block CV (1 km) vs ESA WorldCover 2021 | **F1 0.89** vs 0.58 (IoU 0.81) |
| The map generalises to another year and reference | Built-up F1 | Independent: Impact Observatory LULC 2023, all pixels | **F1 0.86** vs 0.58 |
| Detected expansion is real change | precision / F1 | New urban 2017→2023 vs IO LULC | precision 0.64 · F1 0.29 (conservative) |
| Urban growth 2014→2025 | km² | Confident change only | **167 → 214 km² (+28%)**, 33 km² new |
| Heat differs between zones | Mean LST ± 95% CI | Block bootstrap (300) | established 52.2 °C (52.0–52.4) vs vegetation 50.4 °C |
| Tanager is co-registered | Pearson r (albedo) | Tanager vs Landsat after auto-shift | **r = 0.87** |
| Hyperspectral adds value | ΔR² for LST | Spatial-block CV, Landsat vs Landsat+Tanager | **+0.087** all · **+0.131** built-up |
| Cool roofs cool | °C per +0.10 albedo | OLS in built-up, block-bootstrap CI | **-0.70 °C** (-0.85 to -0.56) |
| Priorities are robust | Top-20 overlap | 4 alternative weightings | 60–100% |
| People change the answer | Top-20 changed | People-aware vs buildings-only index | **90%** of top-20 cells differ |
| Service gap in the hottest districts | OSM amenities per 10k residents | Hottest 20% of populated cells vs rest | bus stops 0.00 vs 0.63 · mosques 0.51 vs 1.74 · parks 0.13 vs 1.18 |

Also: Planet's *beta* cloud mask flagged **74%** of this clear scene as cloud (bright sand and concrete). Our physics test found 0.0%, so the beta mask was replaced.
<!-- RESULTS_END -->

---

## 1 · The problem and who has it

| | |
|---|---|
| **User** | Municipal planning departments and urban heat-resilience offices (e.g. Riyadh Municipality, Abu Dhabi DMT, Dubai Municipality) |
| **Decision** | Which neighbourhoods get cool-roof subsidies, shade trees, shaded bus shelters, mosque-walkway shading or rider cooling points first, and which design rules apply to new districts |
| **Today** | Heat mitigation is decided case by case. No routine, city-wide view links growth → heat → materials → people |
| **Why now** | Gulf cities grow fast, surface temperatures pass 50 °C, and every new district locks in its roofs, roads and greenery for decades |

## 2 · How it works (one notebook, open data only)

```
Tanager scene footprint ──► AOI + 30 m UTM grid (change TANAGER_ID to move city)
 │
 ├─ L1 Urban expansion   Landsat 8/9 SR 2014→2025 · Random Forest (6 bands + 6 indices + texture) trained on ESA WorldCover
 ├─ L2 Heat hazard       Landsat ST_B10, Jun–Aug 2025, cloud-masked median LST
 ├─ L3 Materials         Planet Tanager 426-band hyperspectral: solar-weighted albedo, 1730 nm hydrocarbon index (asphalt),
 │                       2200/2330 nm band depths (clay / carbonate-concrete), red-edge, PCA + k-means material clusters
 ├─ L4 People exposure   WorldPop 2025 residents + OpenStreetMap places where people are outdoors:
 │                       mosques · bus stops · delivery-rider hubs · construction sites · schools/clinics · parks
 └─ L5 Decision product  300 m Heat-Risk Priority Index = heat × people exposure × lack of greenery × new-district factor
                         → recommended action per cell + cool-roof what-if in °C
```

**Why hyperspectral:** Landsat has six broad bands and cannot tell a black asphalt roof from a shaded concrete one. Tanager resolves the **1730 nm hydrocarbon absorption** (asphalt, bitumen) and the **2330 nm carbonate feature** (concrete, limestone), and integrates albedo across the full solar spectrum. We **test** whether it adds value (ΔR² for LST under spatial cross-validation) rather than assuming it.

**Validity safeguards:** QA_PIXEL cloud/shadow/cirrus masking · water-vapour bands (1350–1450, 1800–1950 nm) and >2450 nm removed · Tanager *beta* cloud mask checked against a physics test (on Riyadh it flags bright sand and concrete as cloud, so we replace it) · automatic Tanager→Landsat co-registration with a ±4 px shift search · every train/test split uses ~1 km spatial blocks, so no neighbour leakage.

## 3 · Run it

**Google Colab:** open `QAYDH_T0049_urban_heat_risk.ipynb` → *Runtime → Run all*.
**Locally:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute QAYDH_T0049_urban_heat_risk.ipynb --output QAYDH_executed.ipynb
```
- ~15–30 min the first time (downloads: Tanager cube ≈0.9 GB, Landsat via Planetary Computer, WorldPop ≈56 MB, OSM via Overpass). Raw data is cached in `data/` and **never committed**.
- No credentials are needed. Planetary Computer signs URLs anonymously.
- **Change city:** set `TANAGER_ID` (and `COUNTRY_ISO3` for WorldPop) in the configuration cell. Everything else follows the scene footprint.

## 4 · Repository

| Path | What |
|---|---|
| `QAYDH_T0049_urban_heat_risk.ipynb` | The full pipeline, executed, with all outputs visible |
| `requirements.txt` | Pinned dependencies |
| `qaydh_outputs/results.json` | Every validation number (source of the results card) |
| `qaydh_outputs/data_provenance.json` | Every scene ID, date and licence used |
| `qaydh_outputs/qaydh_heat_risk_cells.geojson` | **Example output**: 300 m decision cells, ready for ArcGIS/QGIS or an API |
| `qaydh_outputs/qaydh_interactive_map.html` | **Dashboard prototype**: open in a browser |
| `qaydh_outputs/top_hotspots.csv` | Ranked hotspots with drivers, action, est. cooling and map link |
| `qaydh_outputs/0*.png` | Figures used in the pitch deck |
| `pitch/` | Pitch deck (PDF + HTML) and `build_deck.py`, which regenerates it from `results.json` |
| `example_input/` | Small example inputs: Tanager STAC item + thumbnail, OSM places extract |

## 5 · How users get the value

1. **Heat-risk dashboard**: cells coloured by priority, top-10 hotspots pinned, toggle layers for mosques, bus stops, rider hubs and construction sites. Hovering shows LST, residents, greenery and the action. (`qaydh_interactive_map.html`, to move to **gIQ** in incubation.)
2. **GeoJSON / REST API**: `qaydh_heat_risk_cells.geojson` loads straight into municipal GIS or permitting tools (e.g. `GET /cells?min_hrpi=80&action=bus_shelter`).
3. **Annual heat brief + alerts**: after each summer, a scheduled re-run produces a one-page brief per municipality. It flags new districts entering the top decile, and projects that moved a cell out of it.

## 6 · Data and licences

| Dataset | Access | Licence |
|---|---|---|
| Planet Tanager surface reflectance (urban open archive) | Planet open STAC | CC-BY-4.0 © Planet Labs PBC |
| Landsat 8/9 Collection 2 Level-2 (SR + ST) | Microsoft Planetary Computer | Public domain (USGS) |
| ESA WorldCover 2021 | Planetary Computer | CC-BY-4.0 © ESA WorldCover project |
| Impact Observatory LULC 2017 / 2023 | Planetary Computer | CC-BY-4.0 |
| WorldPop 2025 constrained population (100 m, R2025A) | data.worldpop.org | CC-BY-4.0 © WorldPop |
| OpenStreetMap POIs | Overpass API | ODbL © OpenStreetMap contributors |

No commercial, gIQ, 813 or MBZ-SAT data is used in the PoC. No raw imagery is in this repository.

## 7 · Limitations (we know where the edges are)

- LST is **surface** temperature from a ~10:30 local overpass, not afternoon air temperature. It ranks places well. Calibration against weather stations is planned for incubation.
- WorldCover / IO LULC are reference maps, not field truth. Low-density suburbs on sand are the hardest case.
- OSM under-maps labour accommodation and delivery waiting spots in the Gulf. Municipal and delivery-platform data would fill this.
- The cooling what-if is a statistical slope with a CI, not a physical simulation. It ranks options and does not guarantee degrees.
- Tanager is a single May acquisition. Materials are stable, but shade and seasonal greenery are not.

## 8 · Incubation plan (PoC → MVP)

1. Run on UAE cities (Abu Dhabi, Dubai, Al Ain) with **Satellite 813 / MBZ-SAT / commercial Tanager** data.
2. Add vulnerable-site and worker layers (labour accommodation, delivery hubs) from municipal and platform partners.
3. Calibrate LST against air temperature from NCM / municipal stations. Field-check material classes on 200–300 points.
4. Deploy the dashboard on **gIQ** with a per-district what-if slider (roof albedo, tree cover, shaded stops).

---
Team T0049: انتصار الحبسي (lead) · نورة الهاجري · مريم البني
