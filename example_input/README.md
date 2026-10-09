# Example input

The notebook reads `tanager_stac_item_20250515_080954_16_4001.json` from this folder (section 2). Everything else is downloaded by the notebook from open archives, with the **exact** IDs below (also in `qaydh_outputs/data_provenance.json`).

| File | What |
|---|---|
| `tanager_stac_item_20250515_080954_16_4001.json` | Planet Tanager STAC item (Riyadh, 2025-05-15 08:09 UTC), bbox and asset links; read by the notebook |
| `osm_pois_20250515_080954_16_4001.json` | OpenStreetMap outdoor-place extract for the same AOI (Overpass) |
| `tanager_thumbnail_riyadh.png` | Scene quick-look |

## Exact scenes and parameters used

| Source | Collection | Dates | Items / parameters | Licence |
|---|---|---|---|---|
| Planet Tanager (open archive) | `tanager-core-imagery/urban` | 2025-05-15T08:09:54.165094Z | 20250515_080954_16_4001 | CC-BY-4.0 © Planet Labs PBC |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2021-06-16 → 2021-10-06 | LC08_L2SP_166043_20211006_02_T1, LC08_L2SP_165043_20210913_02_T1, LC08_L2SP_165043_20210828_02_T1, LC08_L2SP_166043_20210819_02_T1, LC08_L2SP_165043_20210812_02_T1, LC08_L2SP_166043_20210803_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2014-07-24 → 2014-11-04 | LC08_L2SP_166043_20141104_02_T1, LC08_L2SP_166043_20141019_02_T1, LC08_L2SP_166043_20141003_02_T1, LC08_L2SP_165043_20140926_02_T1, LC08_L2SP_166043_20140917_02_T1, LC08_L2SP_166043_20140901_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2025-08-07 → 2025-10-09 | LC09_L2SP_166043_20251009_02_T1, LC08_L2SP_166043_20251001_02_T1, LC09_L2SP_165043_20250916_02_T1, LC08_L2SP_166043_20250915_02_T1, LC08_L2SP_165043_20250908_02_T1, LC09_L2SP_165043_20250831_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2023-08-17 → 2023-10-12 | LC08_L2SP_166043_20231012_02_T1, LC08_L2SP_165043_20231005_02_T1, LC09_L2SP_166043_20231004_02_T1, LC09_L2SP_165043_20230927_02_T1, LC08_L2SP_165043_20230919_02_T1, LC08_L2SP_165043_20230903_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2017-06-21 → 2017-10-27 | LC08_L2SP_166043_20171027_02_T1, LC08_L2SP_166043_20171011_02_T1, LC08_L2SP_165043_20171004_02_T1, LC08_L2SP_166043_20170925_02_T1, LC08_L2SP_165043_20170918_02_T1, LC08_L2SP_165043_20170902_02_T1 … (+4) | Public domain (USGS) |
| esa-worldcover 2021 | `esa-worldcover` | 2021 | ESA_WorldCover_10m_2021_v200_N24E045 | CC-BY-4.0 © ESA WorldCover project 2021 |
| io-lulc-annual-v02 2023 | `io-lulc-annual-v02` | 2023 | 38R-2023 | CC-BY-4.0 © Impact Observatory, Microsoft, Esri |
| io-lulc-annual-v02 2017 | `io-lulc-annual-v02` | 2017 | 38R-2017 | CC-BY-4.0 © Impact Observatory, Microsoft, Esri |
| Landsat 8/9 C2 L2 surface temperature (ST_B10) | `landsat-c2-l2` | 2025-07-05 → 2025-08-31 | LC09_L2SP_165043_20250831_02_T1, LC08_L2SP_166043_20250830_02_T1, LC08_L2SP_165043_20250823_02_T1, LC08_L2SP_166043_20250814_02_T1, LC08_L2SP_165043_20250807_02_T1, LC09_L2SP_166043_20250806_02_T1 … (+4) | Public domain (USGS) |
| Open-Meteo historical weather API (ERA5 reanalysis) | `archive-api.open-meteo.com` | 2025-06-01 → 2025-08-31 | 24.576,46.856 | CC-BY-4.0 © Open-Meteo / Copernicus ERA5 |
| Landsat 8/9 surface temperature summer 2023 | `landsat-c2-l2` | 2023-07-09 → 2023-08-26 | LC09_L2SP_165043_20230826_02_T1, LC08_L2SP_166043_20230825_02_T1, LC08_L2SP_165043_20230818_02_T1, LC09_L2SP_166043_20230817_02_T1, LC08_L2SP_166043_20230809_02_T1, LC08_L2SP_165043_20230802_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 surface temperature summer 2024 | `landsat-c2-l2` | 2024-06-17 → 2024-08-28 | LC09_L2SP_165043_20240828_02_T1, LC09_L2SP_165043_20240812_02_T1, LC08_L2SP_166043_20240811_02_T1, LC08_L2SP_166043_20240726_02_T1, LC08_L2SP_166043_20240710_02_T1, LC08_L2SP_165043_20240703_02_T1 … (+4) | Public domain (USGS) |
| Microsoft Building Footprints (Planetary Computer ms-buildings, 2023) | `ms-buildings` | 2023-04-25 | 66063 footprints | ODbL |
| OpenStreetMap buildings + roads (automatic labels, 4 tiles) | `OSM` |  | tile 1, tile 2, tile 3, tile 4 | ODbL © OpenStreetMap contributors |
| WorldPop 2025 constrained population 100 m (SAU) | `https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/SAU/v1/100m/constrained/sau_pop_2025_CN_100m_R2025A_v1.tif` | 2025 | sau_pop_2025_CN_100m_R2025A_v1.tif | CC-BY-4.0 © WorldPop |
| OpenStreetMap places via Overpass (20250515_080954_16_4001) | `OSM` | 2026-10-02T14:46:36Z | 434 POIs | ODbL © OpenStreetMap contributors |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2021-06-13 → 2021-10-19 | LC08_L2SP_161043_20211019_02_T1, LC08_L2SP_160043_20211012_02_T1, LC08_L2SP_160043_20210926_02_T1, LC08_L2SP_161043_20210901_02_T1, LC08_L2SP_161043_20210816_02_T1, LC08_L2SP_160043_20210724_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2014-06-03 → 2014-10-25 | LC08_L2SP_160043_20141025_02_T1, LC08_L2SP_161043_20141016_02_T1, LC08_L2SP_161043_20140829_02_T1, LC08_L2SP_160043_20140721_02_T1, LC08_L2SP_161043_20140712_02_T1, LC08_L2SP_160043_20140619_02_T1 … (+4) | Public domain (USGS) |
| Landsat 8/9 C2 L2 surface reflectance | `landsat-c2-l2` | 2025-07-26 → 2025-10-31 | LC09_L2SP_160043_20251031_02_T1, LC08_L2SP_160043_20251023_02_T1, LC09_L2SP_160043_20251015_02_T1, LC08_L2SP_160043_20251007_02_T1, LC09_L2SP_161043_20251006_02_T1, LC08_L2SP_161043_20250928_02_T1 … (+4) | Public domain (USGS) |
| esa-worldcover 2021 | `esa-worldcover` | 2021 | ESA_WorldCover_10m_2021_v200_N24E054 | CC-BY-4.0 © ESA WorldCover project 2021 |
| Landsat 8/9 surface temperature summer 2025 (Abu Dhabi) | `landsat-c2-l2` | 2025-06-01 → 2025-08-28 | LC09_L2SP_160043_20250828_02_T1, LC09_L2SP_160043_20250812_02_T1, LC09_L2SP_161043_20250803_02_T1, LC08_L2SP_161043_20250726_02_T1, LC09_L2SP_161043_20250718_02_T1, LC08_L2SP_160043_20250617_02_T1 … (+4) | Public domain (USGS) |
| WorldPop 2025 constrained population 100 m (ARE) | `https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/ARE/v1/100m/constrained/are_pop_2025_CN_100m_R2025A_v1.tif` | 2025 | are_pop_2025_CN_100m_R2025A_v1.tif | CC-BY-4.0 © WorldPop |
| OpenStreetMap places via Overpass (abudhabi) | `OSM` | 2026-10-02T18:09:51Z | 1709 POIs | ODbL © OpenStreetMap contributors |
| Sentinel-2 L2A (Musaffah, summer 2025) | `sentinel-2-l2a` | 2025-06-06 → 2025-08-12 | S2B_MSIL2A_20250616T064619_R020_T40QBM_20250616T090449, S2B_MSIL2A_20250616T064619_R020_T39QZG_20250616T090449, S2B_MSIL2A_20250616T064619_R020_T40RBN_20250616T090449, S2B_MSIL2A_20250616T064619_R020_T39RZH_20250616T090449, S2B_MSIL2A_20250606T064629_R020_T40QBM_20250606T092257, S2B_MSIL2A_20250606T064629_R020_T39QZG_20250606T092257 … (+2) | Copernicus open licence (ESA) |
| Landsat 8/9 ST (Musaffah, summer 2025) | `landsat-c2-l2` | 2025-06-01 → 2025-08-28 | LC09_L2SP_160043_20250828_02_T1, LC09_L2SP_160043_20250812_02_T1, LC09_L2SP_161043_20250803_02_T1, LC08_L2SP_161043_20250726_02_T1, LC09_L2SP_161043_20250718_02_T1, LC08_L2SP_160043_20250617_02_T1 … (+4) | Public domain (USGS) |
| Microsoft footprints + OSM geometry (Musaffah) | `ms-buildings / OSM` | 2023 / 2026-10-02T19:11:06Z | 15501 MS + 10645 OSM buildings, 6793 roads | ODbL |
| WorldPop 2025 constrained population 100 m (ARE) | `https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/ARE/v1/100m/constrained/are_pop_2025_CN_100m_R2025A_v1.tif` | 2025 | are_pop_2025_CN_100m_R2025A_v1.tif | CC-BY-4.0 © WorldPop |
| OpenStreetMap places via Overpass (musaffah) | `OSM` | 2026-10-02T19:11:06Z | 786 POIs | ODbL © OpenStreetMap contributors |
| NOAA Integrated Surface Database (hourly) | `ncei global-hourly` | 2025-06-01 → 2025-08-31 | 41216099999, 41217099999, 40437099999 | Public domain (NOAA) |

Areas of interest: Riyadh = the Tanager scene bbox above; Musaffah block = `[54.455, 24.315, 54.545, 24.395]` (EPSG:32640, 10 m); summer window = 1 Jun – 31 Aug 2025. Random seed `SEED = 813` everywhere.
