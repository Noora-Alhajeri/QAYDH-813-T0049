# QAYDH (القيظ) · Heat-risk intelligence for Gulf cities

## 1 · Title and summary

**Project:** QAYDH · **Team:** T0049 (United Arab Emirates) · **Challenge:** Arab Youth Space Hackathon 2026, 813 Challenge
**Theme 05:** Urban Expansion, Land Use Change & Heat Risk

**What the PoC does:** it finds summer heat hotspots in Gulf cities from satellite data, explains each hotspot by its surface materials, shows who is outside there, and ranks the fix to do first.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Noora-Alhajeri/QAYDH-813-T0049/blob/main/QAYDH_T0049_urban_heat_risk.ipynb)

| ▶ Live dashboard | 📊 Slides | 💻 Notebook |
|---|---|---|
| [noora-alhajeri.github.io/QAYDH-813-T0049](https://noora-alhajeri.github.io/QAYDH-813-T0049/) ([backup](https://raw.githack.com/Noora-Alhajeri/QAYDH-813-T0049/main/dashboard/index.html)) | [`pitch/QAYDH_T0049_pitch.pdf`](pitch/QAYDH_T0049_pitch.pdf) | [`QAYDH_T0049_urban_heat_risk.ipynb`](QAYDH_T0049_urban_heat_risk.ipynb) (run end to end, outputs visible) |

![QAYDH dashboard walkthrough over Musaffah](pitch/gifs/qaydh_musaffah_tour.gif)

## 2 · Business use case

- **User:** municipal planners (e.g. Abu Dhabi DMT, Riyadh RCRC), transport authorities, developers, delivery platforms.
- **Decision:** where to put shade, cool roofs, cool pavement, trees, water and rest points first, and which fix suits each surface.
- **What they use today:** heat maps that show *where* it is hot, then judgement site by site. Nothing says *why* a place is hot, *who* is outside, or *which* fix matches the material.
- **What QAYDH gives them:** a ranked list of hotspots, each with its materials, exposed sites (bus stops, mosques, labour camps, schools) and a short action plan, as a dashboard and as GeoJSON for ArcGIS/QGIS.

## 3 · The problem

Gulf city surfaces pass **55 °C** in summer, yet people still walk to prayers, wait at bus stops, deliver food and build outdoors from 11:00 to 20:00. Cities grow fast, replacing sand with asphalt and metal roofs. Cooling budgets are spent case by case because no map links heat to its cause and to the people exposed.

**Why satellites:** heat, surfaces and growth must be measured across a whole city, every summer, at the same time of day. Thermal (Landsat), multispectral (Sentinel-2), radar (Sentinel-1) and hyperspectral (Tanager, EMIT) satellites are the only tools that do this. Hyperspectral also tells roof materials apart (metal, concrete, tile), which decides the fix.

## 4 · Data used

| Dataset | Provider | Dates | Processing level | Licence |
|---|---|---|---|---|
| Landsat 8/9 TIRS land surface temperature | USGS (via Microsoft Planetary Computer) | Summers 2023–2025 (Musaffah: 10 clear scenes, 2025-06-01 to 2025-08-28) | Collection 2 Level-2 ST | Public domain |
| Sentinel-2 MSI | ESA Copernicus | Summer 2025 | Level-2A | Copernicus open licence |
| Sentinel-1 GRD | ESA Copernicus | Summer 2025 | RTC (terrain corrected) | Copernicus open licence |
| Planet Tanager hyperspectral (Riyadh) | Planet Labs | 2025 (scene ID in `data/sample_input/`) | Surface reflectance | Tanager STAC Data © 2025 Planet Labs PBC |
| NASA EMIT hyperspectral (Musaffah) | NASA LP DAAC | 2024–2025 | L2A reflectance | NASA open data |
| ESA WorldCover | ESA | 2021 | 10 m land cover | CC-BY-4.0 |
| Impact Observatory land cover | Esri / IO | 2023 | 10 m land cover | CC-BY-4.0 |
| Building footprints | Microsoft and OpenStreetMap | 2024–2025 | Vector | ODbL |
| Roads, bus stops, mosques, schools | OpenStreetMap | 2025 | Vector | ODbL |
| Population | WorldPop | 2025 | 100 m grid | CC-BY-4.0 |
| Air temperature | ERA5 (via Open-Meteo); NOAA ISD stations | Summer 2025, hourly | Reanalysis / station | Copernicus licence / NOAA open |

Exact scene IDs and dates: [`data/sample_input/README.md`](data/sample_input/README.md) and [`qaydh_outputs/data_provenance.json`](qaydh_outputs/data_provenance.json). No raw scenes are committed.

## 5 · Technical approach (in execution order)

| Step | Question | Method | Output |
|---|---|---|---|
| 1 | Where is heat high? | Landsat LST, median of clear summer scenes; hazard zones (top 5% = extreme); ERA5 danger hours | Heat hazard map |
| 2 | Who is exposed? | WorldPop residents + OpenStreetMap bus stops, mosques, schools, clinics, labour camps | Named exposure sites |
| 3 | What is there? | Sentinel-2 10 m surface classes (road, roof, sand, green, water); Sentinel-1 radar for built-up; Tanager/EMIT for roof materials; 25,462 building objects | Surface and material maps |
| 4 | Why is it hot? | Random Forest linking surfaces to LST | Heat drivers per hotspot |
| 5 | What to do? | Material-to-fix rules (Estidama cool-roof SRI, MoHRE midday break, shade standards); Llama-3.3-70B writes a short brief from verified numbers only, then every number is checked | Ranked action plan per hotspot |

**Labels:** OSM roads, Microsoft + OSM buildings and ESA WorldCover. A 10 m pixel gets a label only if one class covers at least 80% of it. Confident learning removed 1,718 noisy labels from the training blocks.
**Model settings:** Random Forest (scikit-learn), `SEED = 813`. Musaffah is split into 1 km blocks: A–C train, D validates, E is the held-out test. SAM segments are used for display only, never as training labels.

## 6 · Installation

Requires **Python 3.11–3.13** (Google Colab uses 3.13). No GPU needed.

**Google Colab (easiest):** click the *Open in Colab* badge above, or run in a new notebook:
```
!git clone https://github.com/Noora-Alhajeri/QAYDH-813-T0049.git
%cd QAYDH-813-T0049
!pip install -r requirements.txt
```
Then *Runtime → Restart session*. Colab may print dependency warnings about its own preinstalled packages; they are safe to ignore.

**Local:**
```bash
git clone https://github.com/Noora-Alhajeri/QAYDH-813-T0049.git
cd QAYDH-813-T0049
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt jupyterlab
```

**Tokens (optional, never stored in the repo):** `EARTHDATA_TOKEN` (NASA EMIT section) and `HF_TOKEN` (Llama brief). Without them those two sections skip and the rest runs.

## 7 · How to run

```bash
jupyter lab QAYDH_T0049_urban_heat_risk.ipynb
```
- **Run all cells.** Nothing to edit: the area (Musaffah, bbox `[54.455, 24.315, 54.545, 24.395]`) and `SEED = 813` are set in the first cells.
- **Runtime:** about 60 minutes on the first run (it downloads the scenes), faster afterwards (cached in `data/`). On free Colab keep the tab open so the session does not disconnect.
- **Reads** `data/sample_input/tanager_stac_item_20250515_080954_16_4001.json` (plus open data fetched by scene ID). **Writes** `results/example_output.png`, `results/example_output_hotspots.csv` and `results/example_output_results.json` (last cell), and all products to `qaydh_outputs/`.
- **At the end** you see the hotspot priority map and the evidence table.

All paths are relative to the repository. Optional: `python dashboard/build_dashboard.py` rebuilds the dashboard from the notebook outputs.

## 8 · Example input and output

- **Input:** [`data/sample_input/`](data/sample_input/): the Tanager STAC item, an OpenStreetMap extract, and the exact scene list (IDs, dates, bbox).
- **Output:** [`results/example_output.png`](results/example_output.png), [`results/example_output_hotspots.csv`](results/example_output_hotspots.csv), [`results/example_output_results.json`](results/example_output_results.json).

![Example output: Musaffah heat, surfaces, exposure and priority](results/example_output.png)

**Example, hotspot M-001 (Al Hayal Street, Musaffah):** 57.2 °C surface, hotter than 93% of Musaffah · 54% asphalt, 44% bare sand, 0% green · industrial workers and pedestrians · **Do first:** shaded rest point and water, the MoHRE midday break, cool-pavement coating, coating on concrete roofs, shade and Ghaf trees on the sand.

## 9 · Results and limitations

| What we measured | How we validated it | Result | Baseline |
|---|---|---|---|
| Musaffah surface classes | Held-out 1 km test block | **Macro-F1 0.91** (accuracy 0.90) | Index rules 0.47 |
| Built-up map, Riyadh (transfer test) | Spatial-block CV vs ESA WorldCover | **F1 0.89** | NDBI rule 0.58 |
| Same map, another year and source | Impact Observatory 2023 | **F1 0.86** | 0.58 |
| Adding Sentinel-1 radar | Held-out blocks | **F1 0.89** | Optical only 0.85 |
| Heat drivers, Musaffah | LST on unseen blocks | **R² 0.85**, MAE 1.2 °C | NDBI alone r 0.40 |
| Value of hyperspectral (Tanager) | Spatial CV with and without | **+0.13 R²** | — |
| ERA5 air temperature for danger hours | 3 NOAA stations, ≈2,000 hourly readings each, summer 2025 | MAE 1.4–1.5 °C | — |
| Surface minus air (descriptive) | Landsat LST minus station air on 18 / 10 / 22 overpass days (Al Bateen / Abu Dhabi Intl / Riyadh) | +15.2 / +15.5 / +10.7 °C | Different quantities, not a validation of LST |
| Hotspots stable over time | Same cells, 2024 vs 2025 | **r 0.90** | — |
| Priorities robust | 4 other weightings | 60–100% top-20 overlap | — |
| Cool roofs cool | Block-bootstrap regression | **−0.70 °C per +0.10 albedo** (95% CI −0.85 to −0.56) | — |
| Planner briefs | Number-by-number fact-check | 5/5 pass | — |
| Independent check by people | 60 random points labelled blind on very-high-resolution imagery (`validation/`) | Pending; reported when labelled | Majority class |

**Notes:** the 0.91 is macro-F1 on a near-balanced test set (up to 3,000 pixels per class, majority baseline ≈0.21), not the district's natural class mix. Most numbers above compare against reference maps, not field survey.

**Limitations:**
- Thermal pixels are ~100 m, so we map heat **zones** and the buildings inside them, not single buildings. On the dashboard, a building shows its surrounding block's LST.
- Landsat passes at ~10:40 local time, before the afternoon peak, and LST is surface, not air, temperature.
- There is no buffer between spatial blocks, so test scores may be slightly optimistic.
- EMIT (60 m) mixes roofs and roads; Tanager (30 m) separates materials better. The 139 roof-material labels were AI-assisted and are not yet human-checked, so roof-material accuracy is provisional.
- The independent 60-point check is not yet complete.

**Next steps (incubation):** Satellite 813 / MBZ-SAT imagery over Abu Dhabi, Dubai and Al Ain; a municipal pilot in Musaffah; hosting on Space42 gIQ.

**Repository layout:**

| Path | Contents |
|---|---|
| `QAYDH_T0049_urban_heat_risk.ipynb` | Full pipeline, run, outputs visible |
| `requirements.txt` | Pinned dependencies |
| `data/sample_input/` | Example input |
| `results/` | Example output |
| `qaydh_outputs/` | All figures, `results.json`, GeoJSON decision cells, tables |
| `validation/` | Independent 60-point check and scorer |
| `dashboard/` | Interactive dashboard (`index.html`) and labelling tool |
| `pitch/` | Slides (`QAYDH_T0049_pitch.pdf`), demo GIFs, slide builder |

## 10 · Team, licence and attribution

**Team T0049 (UAE):**
- Entesar Al Habsi (انتصار الحبسي): team lead, story and README
- Noora Al Hajeri (نورة الهاجري): notebook, data and dashboard
- Maryam Al Bunni (مريم البني): slides, licences and checks

**Licence:** code under MIT ([`LICENSE`](LICENSE)). Each dataset keeps its own licence (table in §4).

**Attribution:**
- Tanager STAC Data, available at www.planet.com/data/stac, © 2025 Planet Labs PBC, All Rights Reserved.
- © OpenStreetMap contributors (ODbL); Microsoft Building Footprints (ODbL).
- Contains modified Copernicus Sentinel data 2025; ERA5 © ECMWF / Copernicus Climate Change Service.
- Landsat courtesy of USGS; EMIT courtesy of NASA LP DAAC; WorldPop; ESA WorldCover; Impact Observatory.
- Built with Llama (Llama-3.3-70B, Llama 3.3 Community License). Segment Anything (Meta, Apache-2.0). Basemap imagery © Esri, Maxar.
- Organised by the UAE Space Agency and Space42 (Arab Youth Space Hackathon 2026).
