# QAYDH (القيظ) — Heat-risk intelligence for fast-growing Gulf cities

**Arab Youth Space Hackathon 2026 · Challenge 813 · Team T0049**
**Theme:** Urban Expansion, Land Use Change & Heat Risk (starter notebook `02_land_use_land_cover_change`) · SDG 3, 11, 13

A heat map answers *where is the ground hot?* QAYDH answers the five questions a city has to act on:

| | Question | How QAYDH answers it |
|---|---|---|
| **WHERE** | Which districts grew, and which burn every summer? | Landsat 2014→2025 land cover (Random Forest) + summer surface temperature, persistence over 2023–2025 |
| **WHEN** | At which hours is it dangerous? | Hourly ERA5 weather (Open-Meteo): the daily window above 40 °C |
| **WHY** | Is it the roof, the road, bare sand or missing greenery? | **Planet Tanager hyperspectral** (426 bands): albedo, asphalt 1730 nm, concrete 2330 nm, plus a roof/road/vegetation/sand classifier trained on **automatic labels** from OpenStreetMap, Microsoft building footprints and ESA WorldCover |
| **WHO** | Who is outside there? | WorldPop 2025 residents + OpenStreetMap mosques, bus stops, delivery-rider hubs, construction sites, schools and clinics |
| **WHAT NEXT** | What should be done first, and how much will it cool? | 300 m Heat-Risk Priority Index, a named action per hotspot, what-if °C estimates with 95% CI, confidence, urgency and a public alert |

It runs on **east Riyadh** (the only Arab-region Tanager scene in the open archive) and transfers to **Abu Dhabi: Musaffah, Masdar City, MBZ City and Khalifa City**.

<!-- RESULTS_START -->
### Results (from `qaydh_outputs/results.json`)
East Riyadh: 470 km², 1,091,324 residents. Abu Dhabi: Musaffah 54.5 °C · Masdar 55.4 °C · MBZ City 54.2 °C · Khalifa City A 53.6 °C.

| Claim | Metric | Validation | Result |
|---|---|---|---|
| Built-up map beats the starter rule | F1 / IoU | 5-fold spatial-block CV vs ESA WorldCover | **0.89** vs 0.58 (IoU 0.81) |
| Generalises to another year & reference | F1 | Independent IO LULC 2023 | **0.86** vs 0.58 |
| Detected change is real | precision / F1 | New built 2017→2023 vs IO LULC | precision 0.64 · F1 0.29 (conservative) |
| Urban growth 2014→2025 | km² | Confident change only | **167 → 214 km² (+28%)** |
| Hotspots persist | r, cells | Urban-cell LST 2024 vs 2025; hot in all 3 summers | r = 0.90 · 415 cells |
| Starter heat proxy (NDBI) works? | Pearson r | NDBI vs LST inside built-up | r = -0.01, so no |
| Surface classes (roof/road/veg/sand) | macro-F1 | Leave-one-tile-out, same pixels | full spectrum **0.76** · 6 bands 0.75 · index rules 0.38 |
| Hyperspectral explains heat | ΔR² for LST | Spatial-block CV ± Tanager | **+0.089** all · **+0.132** built-up |
| Tanager co-registered | Pearson r | albedo vs Landsat | r = 0.87 |
| Cool roofs cool | °C per +0.10 albedo | OLS, block-bootstrap CI | **-0.70 °C** (-0.85 to -0.56) |
| Danger hours | hours ≥40 °C | ERA5 hourly, summer 2025 | 11:00–20:00 · 8.3 h/day |
| People change the answer | top-20 changed | People-aware vs buildings-only | **90%** |
| Service gap | OSM per 10k residents | Hottest 20% vs rest | bus stops 0.00 vs 0.63 · parks 0.13 vs 1.18 |
| Priorities robust | top-20 overlap | 4 alternative weightings | 60–100% |
| Abu Dhabi transfer | built-up F1 | Spatial-block CV | **0.81** vs NDBI 0.43 |
| Starter rule fails in desert cities | % built-up | NDBI vs WorldCover vs QAYDH | Masdar 80% vs 17% vs 35% · Musaffah 92% vs 70% vs 82% |

Also: Planet's *beta* cloud mask flagged 74% of this clear scene as cloud (bright sand and concrete). Our physics test found 0.0%, so the beta mask was replaced.
<!-- RESULTS_END -->

---

## Run it

**Google Colab:** open `QAYDH_T0049_urban_heat_risk.ipynb` → *Runtime → Run all*.

**Locally (VS Code / Jupyter):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name qaydh --display-name "QAYDH (.venv)"
```
Open the notebook and choose the kernel **QAYDH (.venv)**, then *Run All*. Always run from the top: later cells use functions defined in the toolbox cell. The first cell installs any missing package into whatever kernel you picked.

- The first run takes ~30–45 min, mostly downloads: Tanager cube ≈0.9 GB, Landsat via Planetary Computer, WorldPop, OSM, Microsoft footprints. Everything is cached in `data/` (never committed), and later runs are much faster. Network hiccups are retried automatically.
- No credentials needed.
- **Change city:** set `TANAGER_ID` and `COUNTRY_ISO3` in the configuration cell. The Abu Dhabi section (10) shows how to run any AOI without a Tanager scene.

**Dashboard:** open `dashboard/index.html` in a browser, or rebuild it with `python dashboard/build_dashboard.py`.
**Deck:** `python pitch/build_deck.py` regenerates `pitch/QAYDH_T0049_pitch.pdf` from the results and dashboard.

## Do we need manual labelling?

No, not for the PoC. Every class comes from an existing trusted layer, and the model only learns what those layers cannot say:

| What we need to know | Label source |
|---|---|
| Buildings / roofs | OpenStreetMap outlines ∪ Microsoft open building footprints (OSM maps only ~1,250 buildings in this AOI, Microsoft ~66,000) |
| Streets / asphalt | OpenStreetMap roads, widened by road class |
| Vegetation, bare sand, water | ESA WorldCover |
| Names (mosque, bus stop, street) | OpenStreetMap |
| Population | WorldPop 2025 |

Section **6c** keeps only clear pixels (≥50% building, ≥60% road, or uniform WorldCover class), trains a Random Forest on Tanager spectra, and scores it on **tiles the model never saw**, against the starter index rules and 6 broad Landsat-like bands built from the same pixels. Manual polygons (200–300 field-checked points) are planned for incubation to measure label noise.

## Repository

| Path | What |
|---|---|
| `QAYDH_T0049_urban_heat_risk.ipynb` | End-to-end pipeline, executed, all outputs visible |
| `requirements.txt` | Pinned dependencies |
| `dashboard/index.html` | **Interactive story dashboard** (Riyadh + Abu Dhabi): chapters, layers, hotspot cards, what-if, alerts |
| `pitch/QAYDH_T0049_pitch.pdf` | Pitch deck (PDF, built by `pitch/build_deck.py`) |
| `qaydh_outputs/results.json` | Every number, the source of the deck and dashboard |
| `qaydh_outputs/data_provenance.json` | Every scene ID, date and licence |
| `qaydh_outputs/*_heat_risk_cells.geojson` | **Example output**: 300 m decision cells for GIS / API (Riyadh, Abu Dhabi) |
| `qaydh_outputs/*top_hotspots.csv` | Ranked hotspots: who, why, action, °C what-if, confidence, urgency, alert |
| `qaydh_outputs/0*.png, 10_*.png` | All figures |
| `example_input/` | **Example input**: Tanager STAC item, thumbnail, OSM places extract |

## How users get the value

1. **Story dashboard** for planners: WHERE → WHEN → WHY → WHO → WHAT NEXT, with a hotspot card per cell. To be hosted on **gIQ**.
2. **GeoJSON / REST API**: `GET /cells?city=abudhabi&min_hrpi=80` into ArcGIS/QGIS, permitting and capital-planning tools.
3. **Summer brief + public alerts**: a scheduled re-run each summer flags new districts entering the top decile and publishes danger-hour alerts for the hotspots.

## Data and licences

| Dataset | Access | Licence |
|---|---|---|
| Planet Tanager surface reflectance (urban open archive) | Planet open STAC | CC-BY-4.0 © Planet Labs PBC |
| Landsat 8/9 C2 L2 (SR + ST) | Microsoft Planetary Computer | Public domain (USGS) |
| ESA WorldCover 2021 | Planetary Computer | CC-BY-4.0 |
| Impact Observatory LULC 2017/2023 | Planetary Computer | CC-BY-4.0 |
| Microsoft Building Footprints | Planetary Computer `ms-buildings` | ODbL |
| WorldPop 2025 constrained (100 m) | data.worldpop.org | CC-BY-4.0 |
| OpenStreetMap | Overpass API | ODbL |
| Open-Meteo historical weather (ERA5) | archive-api.open-meteo.com | CC-BY-4.0 |

No commercial, gIQ, 813 or MBZ-SAT data is used, no credentials are stored, and no raw imagery is in the repository.

## Limitations

- LST is surface temperature at ~10:40. Air peaks later, so weather data sets the danger hours.
- Automatic labels carry noise (unmapped buildings, typical road widths). We use clear pixels only and validate on unseen tiles.
- Abu Dhabi has no open hyperspectral scene yet. Its materials come from Landsat albedo, and district boxes are approximate.
- People exposure models where outdoor activity is likely. It does not count people. OSM under-maps labour housing and rider waiting spots.
- What-if °C values are statistical slopes with 95% CIs, not simulations. They rank options.

## Incubation (PoC → MVP)

1. Satellite 813 / MBZ-SAT hyperspectral over Abu Dhabi, Dubai and Al Ain.
2. Labour-housing and delivery-hub layers with municipal and platform partners.
3. Weather-station calibration and 200–300 field-checked surface points.
4. gIQ dashboard with a what-if slider (roof albedo, trees, shaded stops).

---
Team T0049: انتصار الحبسي (lead) · نورة الهاجري · مريم البني
