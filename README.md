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

![QAYDH dashboard walkthrough: Musaffah](pitch/gifs/qaydh_musaffah_tour.gif)

### ▶ Live dashboard: [**https://noora-alhajeri.github.io/QAYDH-813-T0049/**](https://noora-alhajeri.github.io/QAYDH-813-T0049/)
Backup link that always works: [open the dashboard directly](https://raw.githack.com/Noora-Alhajeri/QAYDH-813-T0049/main/dashboard/index.html) · Pitch: [`pitch/QAYDH_T0049_pitch.pdf`](pitch/QAYDH_T0049_pitch.pdf)

**Dashboard:** open the live link (or `dashboard/index.html` locally) and press **Start the tour**, then **Next**. The six steps are: where is heat high → who may be exposed → what is physically there → how it was labelled → why it may be hot → what should be done. Click any hotspot (M-001), site (S-001) or building (B-00001) for its evidence card.

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
| **Musaffah** surfaces at 10 m (road/roof/sand/veg/water) | macro-F1 | Rule-based reference labels (OSM + Microsoft footprints + WorldCover, ≥80% purity), 1 km blocks A–C train · D val · **E held-out test** | **0.91** vs starter index rules 0.47 (road F1 0.88 vs 0.00) |
| Annotation quality | labels removed | Confident learning (out-of-fold) | 1,718 of 64,643 flagged as noise; 300-point review queue exported |
| **Musaffah** why-model | R² / MAE | 5-fold 1 km spatial CV, 100 m thermal cells | **R² 0.85**, MAE 1.2 °C (linear 0.81) |
| **Musaffah** exposure sites | count | OSM sites scored within 150 m | 139 sites · 1 very high · 7 high |
| Top Musaffah hotspot | — | Rule engine with stated reasons | M-001: Shade structures + cool pavement + Shaded rest nodes + midday work-break enforcement + Trees / vegetated shade on open ground (irrigation needed) |
| Ground truth: Al Bateen (OMAD) | ERA5 vs station r, MAE | NOAA ISD hourly, summer 2025 | r 0.95 · MAE 1.4 °C · danger 12:00–15:00 (station) vs 11:00–16:00 (ERA5) · LST−air +15.2 °C |
| Ground truth: Abu Dhabi Intl (OMAA) | ERA5 vs station r, MAE | NOAA ISD hourly, summer 2025 | r 0.95 · MAE 1.5 °C · danger 11:00–16:00 (station) vs 11:00–17:00 (ERA5) · LST−air +15.5 °C |
| Ground truth: Riyadh King Khaled (OERK) | ERA5 vs station r, MAE | NOAA ISD hourly, summer 2025 | r 0.99 · MAE 1.4 °C · danger 10:00–20:00 (station) vs 11:00–19:00 (ERA5) · LST−air +10.7 °C |

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

**Dashboard:** live at https://noora-alhajeri.github.io/QAYDH-813-T0049/, or open `dashboard/index.html` in a browser, or rebuild it with `python dashboard/build_dashboard.py`.
**Deck:** `python pitch/build_deck.py` regenerates `pitch/QAYDH_T0049_pitch.pdf` from the results and dashboard.

## Challenge coverage (sections 10f–10i)

| Challenge line | Where |
|---|---|
| **Fuse 813/optical with SAR and thermal** | **10f** Sentinel-1 RTC VV/VH fused with Sentinel-2: built-up precision/recall/F1/IoU and the sand→roof confusion rate, with vs without radar, on held-out blocks. Radar ΔVV 2017→2025 independently confirms new buildings |
| **Informal settlement detection, roofing materials** | **10g** roof materials from Tanager spectra (white/cool, bitumen, clay tile, concrete, metal sheet) with separability and thermal-physics checks plus OSM `roof:material`; Musaffah building-level roof screen. **10h** informal / substandard-housing candidates (density, small footprints, irregular layout, hot roofs, heat), validated by OSM-housing enrichment with a permutation test |
| **Heat-island proxy + weather** | **10i** NDBI alone vs fused optical + SAR model (R², RMSE, MAE, spatial CV), daytime SUHII, danger hours from station-checked ERA5 |
| Urban growth · land-use change · green space · population · OSM | sections 4, 5b, 7b, 10b |
| 813 urban scenes | not released in the PoC phase; the pipeline is sensor-agnostic (Tanager and EMIT already plug in) |

Run sections 10f–10i once (each is self-contained and cannot break Run All). Then run `python dashboard/build_dashboard.py` and `CHROME=<path to chrome> python pitch/build_deck.py` to put the new numbers and figures into the dashboard and deck.

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
| `qaydh_outputs/musaffah_*` | **Musaffah deep dive**: annotation polygons + review queue (QGIS), exposure sites, hotspots, 100 m cells |
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

## Annotation & AI models
- **Reference annotation:** GIS candidates kept at ≥80% purity, mixed pixels excluded, 1 km blocks A–C/D/E, confident-learning cleanup → `qaydh_outputs/musaffah_annotation_reference_polygons.geojson`.
- **Human review queue:** the 300 most uncertain pixels → `musaffah_annotation_review_queue.geojson` (open in QGIS).
- **Object labels:** every building (Microsoft + OSM) with ID, bounding box, roof class, dark-roof flag, heat zone, new-since-2017, street → `musaffah_building_objects.geojson/.csv`.
- **SAM (Segment Anything, Apache-2.0)** segments around hotspots with class, purity and heat → `musaffah_sam_segments.geojson`.
- **Qwen2.5-1.5B-Instruct (Apache-2.0)** drafts planner briefs from verified facts. A unit-aware fact-checker rejects hallucinations and a person signs off → `musaffah_planner_briefs.csv`.

## Limitations: solved, reduced, remaining

| Limitation | Status | How |
|---|---|---|
| Starter NDBI rule confuses sand, roads and roofs | Solved | Riyadh F1 0.89 vs 0.58; Musaffah surfaces 0.91 vs 0.47 on held-out blocks |
| Planet beta cloud mask flags bright desert as cloud | Solved | Physics-based cloud test (74% → 0%) |
| Labels need annotation | Solved for the PoC | ≥80%-purity GIS labels, confident-learning cleanup, SAM candidates, 300-point review queue |
| Unnamed OSM places · sparse OSM buildings | Solved | Nearest-street names · Microsoft open footprints |
| No air-temperature check | Solved | NOAA stations: ERA5 r 0.95–0.99; LST runs 11–15 °C above air, so it is used as relative hazard |
| LST is a 10:40 snapshot | Reduced | Station-checked ERA5 sets the danger hours; 3-summer persistence |
| Thermal is coarse (~100 m) | Reduced | Shown as hazard zones; 10 m surfaces and objects explain them |
| LLMs can hallucinate | Reduced | Unit-aware fact-check rejected 5/5 drafts here; verified template + human sign-off |
| Hyperspectral over Musaffah | In progress | No Tanager scene; **NASA EMIT** (285 bands, 60 m) has 33 passes over Musaffah and plugs into section 10e with a free NASA Earthdata login |
| Field truth for labels | Remains | Review queue is ready for a field visit |
| People exposure ≠ head counts | By design | Exposure opportunity from places + residents; no tracking of individuals |

## Incubation (PoC → MVP)

1. Satellite 813 / MBZ-SAT hyperspectral over Abu Dhabi, Dubai and Al Ain.
2. Labour-housing and delivery-hub layers with municipal and platform partners.
3. Weather-station calibration and 200–300 field-checked surface points.
4. gIQ dashboard with a what-if slider (roof albedo, trees, shaded stops).

---
Team T0049: انتصار الحبسي (lead) · نورة الهاجري · مريم البني
