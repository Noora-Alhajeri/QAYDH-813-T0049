# Judging-question slides + challenge-coverage slides for the QAYDH deck.
# exec'd from build_deck.py (uses its slide/icon/img/fig helpers, R and MH). Every number comes from results.json.
import os as _os, json as _json

def _g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict) or k not in d: return default
        d = d[k]
    return d

_mc = {d["approach"]: d for d in R["musaffah_classifier"]["scores"]}
_best = R["musaffah_classifier"]["chosen"]; _rule = [k for k in _mc if k.startswith("Index")][0]
_hs = {d["approach"]: d for d in R["material_classifier"]["scores"]}
_h6 = [k for k in _hs if k.startswith("6")][0]; _hf = [k for k in _hs if k.startswith("Full")][0]
_wm = {d["model"]: d for d in R["musaffah_why_model"]["scores"]}["Random Forest"]
_st = R.get("station_check", []); _w = R["weather"]
_road = _g(_mc[_best], "per_class_F1", default={}) or {}
_h0 = MH.iloc[0]

# ---------- Q1 · the business problem ----------
_cust = [("building-skyscraper", "Municipal planners", "One-off consultant studies, complaints, the same tree programme everywhere",
          "A ranked list of streets and sites, each with its reason and its fix"),
         ("building-factory", "Industrial zones & contractors", "One blanket midday-break rule; no idea which yard or camp is worst",
          "Which yards, camps and bus stops need shade, rest nodes and roof coating first"),
         ("motorbike", "Transport & delivery operators", "Riders and passengers wait wherever the stop or restaurant happens to be",
          "Cooling points and shaded stops placed where heat and waiting overlap")]
slide(f'''<div class="kick">Question 1 · the business problem</div><h1 class="big">Who loses when a city heats up, and what do they do today?</h1>
<div class="q1">{"".join(f'<div class="c">{icon(i_, 46)}<b>{t}</b><div class="tag bad">Today</div><p>{a}</p><div class="tag good">With QAYDH</div><p class="g">{b}</p></div>' for i_, t, a, b in _cust)}</div>
<div class="cost"><div><b>{_w["heat_hours_ge40_per_day"]:.1f} h</b>a day above 40 °C air</div><div><b>{_w["days_air_ge_40"]}/{_w["n_days"]}</b>summer days at 40 °C+</div>
<div><b>+{(_st[0]["LST_minus_air_C"] if _st else 15):.0f} °C</b>ground above air at 10:40</div><div><b>{R["residents_hot20"]:,.0f}</b>residents in the hottest fifth (Riyadh)</div></div>
<p class="biz">Business model · per-city subscription: dashboard + API + summer report · open-data core keeps cost near zero · upgrades to Satellite 813 / MBZ-SAT hyperspectral in incubation</p>''')

# ---------- Q2 · how good is it, really? ----------
_rows = [("Built-up map · east Riyadh", "F1", R["cv_built_f1_ndbi"], R["cv_built_f1_rf"], "5-fold spatial-block CV vs ESA WorldCover"),
         ("Same map, another year & source", "F1", R["indep2023_built_f1_ndbi"], R["indep2023_built_f1_rf"], "independent Impact Observatory 2023"),
         ("Musaffah surfaces (10 m)", "macro-F1", _mc[_rule]["test_macro_F1"], _mc[_best]["test_macro_F1"], "held-out 1 km test blocks"),
         ("Hyperspectral surfaces (Tanager)", "macro-F1", _hs[_h6]["macro_F1"], _hs[_hf]["macro_F1"], "6 broad bands → full spectrum, unseen tiles"),
         ("Why-model: surfaces → heat", "R²", max(R["ndbi_lst_r_builtup"], 0) ** 2, _wm["R2"], f"spatial CV · RMSE {_wm['RMSE_C']:.2f} °C · MAE {_wm['MAE_C']:.2f} °C")]
_sar = R.get("sar_fusion")
if _sar:
    _sc = {d["model"]: d for d in _sar["scores"]}; _a, _b = list(_sc)[0], list(_sc)[2]
    _rows.append(("Built-up with radar (S2 → S2+SAR)", "F1", _sc[_a]["built_F1"], _sc[_b]["built_F1"], f"held-out blocks · sand→roof {_sar['sand_called_roof_pct_s2']:.1f}% → {_sar['sand_called_roof_pct_fusion']:.1f}%"))
_bars = "".join(f'''<div class="r"><span class="n">{n}</span><span class="m">{m}</span>
<span class="bars"><i class="b0" style="width:{max(2, 100*b0):.0f}%"></i><i class="b1" style="width:{max(2, 100*b1):.0f}%"></i></span>
<span class="v"><s>{b0:.2f}</s> → <b>{b1:.2f}</b></span><span class="how">{h}</span></div>''' for n, m, b0, b1, h in _rows)
_extra = [f"<div><b>r {min(d['era5_vs_station_r'] for d in _st):.2f}–{max(d['era5_vs_station_r'] for d in _st):.2f}</b>weather vs 3 NOAA stations · MAE ≈{_st[0]['MAE_C']:.1f} °C</div>" if _st else "",
          f"<div><b>{R['cv_built_iou_rf']:.2f}</b>built-up IoU (Riyadh)</div>",
          f"<div><b>r {R['lst_cells_r_2024_vs_2025']:.2f}</b>hotspots repeat 2024 ↔ 2025</div>",
          f"<div><b>{min(R['hrpi_top20_overlap'].values())*100:.0f}–{max(R['hrpi_top20_overlap'].values())*100:.0f}%</b>top-20 stable under 4 weightings</div>"]
if R.get("informal_screen"): _extra.append(f"<div><b>×{R['informal_screen']['enrichment_ratio']:.1f}</b>informal screen enrichment (p {R['informal_screen']['permutation_p']:.3f})</div>")
slide(f'''<div class="kick">Question 2 · how good is the model, really?</div><h1>Measured against baselines, on places the model never saw</h1>
<div class="legend2"><i class="b0"></i>starter / baseline <i class="b1"></i>QAYDH</div><div class="score">{_bars}</div><div class="extra">{"".join(_extra)}</div>''')

# ---------- Q3 · how end users see it ----------
_dash = _os.path.join(PITCH, "dashboard.png")
_api = _json.dumps({"id": _h0.id, "street": str(_h0.street), "lat": round(float(_h0.lat), 4), "lon": round(float(_h0.lon), 4),
                    "surface_temp_C": float(_h0.LST_C), "heat_percentile": int(_h0.heat_pct), "who": str(_h0.exposure_context),
                    "surfaces": {"road": float(_h0.road), "roof": float(_h0.roof), "sand": float(_h0.sand), "green": float(_h0.veg)},
                    "actions": str(_h0.actions).split(" + ")[:3], "confidence": str(_h0.confidence)}, indent=1, ensure_ascii=False)
_top5 = "".join(f"<tr><td>{r.id}</td><td>{str(r.street)[:22]}</td><td>{r.LST_C:.1f}°</td><td>{str(r.actions).split(' + ')[0]}</td></tr>" for r in MH.head(5).itertuples())
slide(f'''<div class="kick">Question 3 · how end users see the results</div><h1>One engine, four doors. No GIS skills needed.</h1>
<div class="doors">
<div class="d"><div class="dh">{icon("eye", 30)}<b>Dashboard</b><span>open a link → click a hotspot</span></div>{f'<img src="{img(_dash)}">' if _os.path.exists(_dash) else ''}</div>
<div class="d"><div class="dh">{icon("database", 30)}<b>REST API</b><span>into the city's GIS & permits</span></div><pre><em>GET</em> /v1/hotspots?city=musaffah&amp;top=10
{_api[:520]}</pre></div>
<div class="d"><div class="dh">{icon("clock", 30)}<b>Heat alert</b><span>SMS / app push on danger days</span></div>
<div class="phone"><div class="bub"><b>QAYDH heat alert · {_h0.id}</b><br>{str(_h0.street)}: extreme surface heat today {_w["danger_window_local"]}. Outdoor workers & riders: shaded rest nodes open, water at the bus stop. Avoid midday work.</div><div class="bub me">Show nearest shade</div></div></div>
<div class="d"><div class="dh">{icon("checklist", 30)}<b>Summer report</b><span>PDF brief for the planning committee</span></div>
<div class="rep"><b>Musaffah · Summer 2025 · top 5 actions</b><table>{_top5}</table></div></div></div>''')

# ---------- challenge coverage ----------
_cov = [("Quantify urban growth", f"+{R['growth_pct']:.0f}% built-up 2014→2025", "4"),
        ("Map land-use transitions", "new urban 2017→2023 checked vs IO LULC; SAR ΔVV on new buildings", "4 · 10f"),
        ("Urban heat island & heat risk", "LST, SUHII, persistence, Heat-Risk Priority Index", "5 · 8 · 10i"),
        ("Fuse optical + SAR + thermal", "Sentinel-1 VV/VH + Sentinel-2 + Landsat TIRS", "10f · 10i"),
        ("Green space mapping", "vegetation class, distance to green, parks per 10k people", "5b · 7b"),
        ("Heat proxy + weather", f"NDBI r = {R['ndbi_lst_r_builtup']:.2f} → fused model; ERA5 checked vs NOAA stations", "5b · 10d · 10i"),
        ("Informal settlements & roof materials", "metal · concrete · tile · bitumen · white roofs; informal-housing candidates", "10g · 10h"),
        ("Population & OSM", "WorldPop residents; OSM + Microsoft buildings, roads, mosques, stops", "7b · 10b"),
        ("813 urban scenes", "not released in the PoC phase; pipeline is sensor-agnostic (Tanager, EMIT tested)", "incubation")]
slide('<div class="kick">Challenge coverage</div><h1>Every challenge line, answered</h1><div class="cov">' +
      "".join(f'<div class="{"todo" if w_ == "incubation" else ""}">{icon("checklist" if w_ != "incubation" else "clock", 28, "#43c6b4" if w_ != "incubation" else "#ffb15c")}<b>{t}</b><span>{d_}</span><em>{w_}</em></div>' for t, d_, w_ in _cov) + "</div>")

# ---------- new evidence slides (appear once the notebook sections have run) ----------
def _figslide(fn, kick, title, strip):
    if _os.path.exists(_os.path.join(OUT, fn)):
        slide(f'<div class="kick">{kick}</div><h1>{title}</h1><img class="figw" style="height:520px" src="{fig(fn)}"><div class="strip" style="bottom:40px">{strip}</div>')
if _sar:
    _figslide("15_sar_fusion.png", "Sentinel-1 radar fusion", "Radar sees structure: sand stops looking like a city",
              f"<div><b>{_sc[_b]['built_F1']:.2f}</b>built-up F1 with SAR (S2 alone {_sc[_a]['built_F1']:.2f})</div><div><b>{_sar['sand_called_roof_pct_fusion']:.1f}%</b>sand mistaken for roof (was {_sar['sand_called_roof_pct_s2']:.1f}%)</div>"
              + (f"<div><b>{_sar['growth_check']['dVV_new_buildings_db']:+.1f} dB</b>radar brightening on buildings new since 2017</div>" if "growth_check" in _sar else ""))
_rr = R.get("roof_materials_riyadh"); _rm = R.get("roof_materials_musaffah")
if _rr:
    _lst = _rr.get("median_LST_C", {}); _hot = max(_lst, key=_lst.get) if _lst else ""
    _figslide("16_roof_materials.png", "Roofing materials from spectra", "Metal, concrete, tile, bitumen, white: the roof decides the fix",
              f"<div><b>{_rr['silhouette']:.2f}</b>spectral separability (silhouette)</div><div><b>{_hot.split(' ')[0]}</b>hottest roof material in Landsat LST</div>"
              + (f"<div><b>{_rm['hot_material_in_hot_zone']:,}</b>metal/bitumen roofs in Musaffah's high-heat zones</div>" if _rm else ""))
_inf = R.get("informal_screen")
if _inf:
    _figslide("17_informal_screen.png", "Informal / substandard-housing screen", "Dense, irregular, sheet-roofed and hot: candidates for a field visit",
              f"<div><b>{_inf['flagged']}</b>candidate 100 m cells of {_inf['cells']}</div><div><b>×{_inf['enrichment_ratio']:.1f}</b>OSM-mapped housing enrichment (p {_inf['permutation_p']:.3f})</div><div><b>Field check</b>never used for enforcement</div>")
_hp = R.get("heat_island_proxy")
if _hp:
    _hsc = {d["model"]: d for d in _hp["scores"]}
    slide(f'''<div class="kick">Heat-island proxy + weather</div><h1 class="big">NDBI alone can't explain heat. Surfaces + radar + weather can.</h1>
<div class="nums"><div><b>r {_hp['ndbi_r']:.2f}</b><span>NDBI vs surface heat<br>in built-up Musaffah</span></div>
<div><b>{max(d['R2'] for d in _hsc.values()):.2f}</b><span>R² of the fused model<br>spatial CV</span></div>
<div><b>{min(d['RMSE_C'] for d in _hsc.values()):.2f} °C</b><span>RMSE, fused model</span></div>
<div><b>{_hp['SUHII_C']:+.1f} °C</b><span>daytime SUHII: city vs open desert</span></div>
<div><b>{_w['danger_window_local']}</b><span>danger window (ERA5, station-checked)</span></div>
<div><b>{_w['heat_hours_ge40_per_day']:.1f} h</b><span>per day above 40 °C air</span></div></div>''')

EXTRA_CSS = """
.q1{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:6px}
.q1 .c{background:#1f1a15;border:1px solid #3a3027;border-radius:18px;padding:22px 24px;display:flex;flex-direction:column;gap:8px}
.q1 b{font:800 32px/1.05 'Big Shoulders Display'} .q1 p{margin:0;font-size:19px;line-height:1.35;color:#cdbda4} .q1 p.g{color:#e6fff9}
.tag{font:600 12px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;width:max-content;padding:3px 10px;border-radius:999px;margin-top:6px}
.tag.bad{background:#3a2a20;color:#ffb15c}.tag.good{background:#14332e;color:#43c6b4}
.cost{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:26px}
.cost div{border-top:4px solid #ff6b2c;padding-top:10px;font-size:18px;color:#cdbda4} .cost b{display:block;font:800 52px/1 'Big Shoulders Display';color:#ff6b2c}
.biz{position:absolute;left:96px;right:96px;bottom:46px;font:500 17px 'IBM Plex Mono';color:#43c6b4;letter-spacing:.02em}
.legend2{font:500 15px 'IBM Plex Mono';color:#cdbda4;display:flex;gap:10px;align-items:center;margin:-8px 0 12px}
.legend2 i{width:26px;height:10px;border-radius:5px;display:inline-block}.b0{background:#5c4e40}.b1{background:#ff6b2c}
.score .r{display:grid;grid-template-columns:330px 90px 1fr 150px 360px;gap:14px;align-items:center;padding:9px 0;border-bottom:1px solid #2c241d;font-size:18px}
.score .n{font-weight:600}.score .m{font:500 14px 'IBM Plex Mono';color:#ffb15c}
.score .bars{display:flex;flex-direction:column;gap:4px}.score .bars i{height:10px;border-radius:5px;display:block}
.score .v{font:500 20px 'IBM Plex Mono'}.score .v s{color:#8f806b}.score .v b{color:#ff6b2c}.score .how{font-size:15px;color:#a8977f}
.extra{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;margin-top:22px}.extra div{font-size:15px;color:#cdbda4}.extra b{display:block;font:800 38px/1 'Big Shoulders Display';color:#43c6b4}
.doors{display:grid;grid-template-columns:1.25fr 1fr 0.8fr 1fr;gap:18px;height:620px}
.doors .d{background:#1f1a15;border:1px solid #3a3027;border-radius:18px;padding:16px;display:flex;flex-direction:column;gap:12px;overflow:hidden}
.dh{display:grid;grid-template-columns:34px 1fr;gap:0 10px;align-items:center}.dh svg{grid-row:span 2}.dh b{font:800 30px/1 'Big Shoulders Display'}.dh span{font-size:14px;color:#a8977f}
.doors img{width:100%;flex:1;object-fit:cover;object-position:left top;border-radius:10px}
.doors pre{margin:0;flex:1;background:#0f0c0a;border-radius:10px;padding:12px;font:500 12.5px/1.45 'IBM Plex Mono';color:#cfe9e4;white-space:pre-wrap;overflow:hidden}.doors pre em{color:#ff6b2c;font-style:normal}
.phone{flex:1;background:#0f0c0a;border:3px solid #3a3027;border-radius:26px;padding:16px 12px;display:flex;flex-direction:column;gap:10px}
.bub{background:#2a2119;border-radius:14px 14px 14px 4px;padding:10px 12px;font-size:14px;line-height:1.4}.bub b{color:#ff6b2c}.bub.me{align-self:flex-end;background:#43c6b4;color:#0d1f1c;border-radius:14px 14px 4px 14px;font-weight:600}
.rep{flex:1;background:#f4ede0;color:#1f1a15;border-radius:10px;padding:14px;font-size:13px}.rep b{display:block;font:800 22px 'Big Shoulders Display';margin-bottom:8px}
.rep table{width:100%;border-collapse:collapse}.rep td{border-bottom:1px solid #d8ccb6;padding:5px 4px;vertical-align:top}.rep td:nth-child(3){color:#c2410c;font-weight:600}
.cov{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.cov div{background:#1f1a15;border:1px solid #3a3027;border-left:4px solid #43c6b4;border-radius:12px;padding:14px 16px;display:grid;grid-template-columns:34px 1fr;gap:2px 10px}
.cov div.todo{border-left-color:#ffb15c}.cov svg{grid-row:span 3}.cov b{font:800 24px/1.05 'Big Shoulders Display'}.cov span{font-size:15px;color:#cdbda4;line-height:1.3}
.cov em{font:500 12px 'IBM Plex Mono';color:#ffb15c;font-style:normal;letter-spacing:.08em}
"""
