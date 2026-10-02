"""QAYDH pitch deck: visual, story-map style (HTML -> PDF via headless Chrome).
Every number comes from qaydh_outputs/results.json; screens come from the live dashboard (dashboard/index.html).
usage: python pitch/build_deck.py   (after the notebook and dashboard/build_dashboard.py)
"""
import json, os, base64, subprocess, html
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qaydh_outputs"); PITCH = os.path.join(ROOT, "pitch"); SHOTS = os.path.join(PITCH, "screens")
os.makedirs(SHOTS, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
R = json.load(open(os.path.join(OUT, "results.json")))
HOT = pd.read_csv(os.path.join(OUT, "top_hotspots.csv"))

# ---------- dashboard screens (story-map frames, like a live product walkthrough) ----------
DASH = open(os.path.join(ROOT, "dashboard", "index.html")).read()
def shot(name, js, w=1600, h=950):
    p = os.path.join(SHOTS, name + ".png"); tmp = os.path.join(SHOTS, "_tmp.html")
    open(tmp, "w").write(DASH.replace("build();\n</script>", f"build();setTimeout(()=>{{{js}}},400);\n</script>"))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", "--virtual-time-budget=9000",
                    f"--screenshot={p}", "file://" + tmp], capture_output=True, timeout=180)
    os.remove(tmp); return p
SC = dict(
    grow=shot("01_grow", "goChapter(0);document.getElementById('layer-growth')"),
    heat=shot("02_heat", "goChapter(1)"),
    when=shot("03_when", "goChapter(2)"),
    why=shot("04_why", "goChapter(3)"),
    who=shot("05_who", "goChapter(4)"),
    act=shot("06_act", "showHot(0)"),
    ad=shot("07_abudhabi", "document.getElementById('city-abudhabi').click();setTimeout(()=>goChapter(1),300)"),
    adact=shot("08_abudhabi_act", "document.getElementById('city-abudhabi').click();setTimeout(()=>showHot(1),300)"),
)
def img(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
def fig(n): return img(os.path.join(OUT, n))

z = {d["zone"]: d for d in R["lst_by_zone"]}; est = next(v for k, v in z.items() if k.startswith("Est"))
mc = {d["approach"]: d for d in R["material_classifier"]["scores"]}
kh = [k for k in mc if k.startswith("Full")][0]; k6 = [k for k in mc if k.startswith("6")][0]; ki = [k for k in mc if k.startswith("Index")][0]
w = R["weather"]; g = R["amenities_per_10k_hot_vs_rest"]; cool = R["cooling_per_0p1_albedo_C"]; ad = R["abudhabi"]
dist = {d["district"]: d for d in ad["districts"]}; ms, mu = dist["Masdar City"], dist["Musaffah industrial"]
t10 = R["top10_summary"]; ov = R["hrpi_top20_overlap"]
f2 = lambda x: f"{x:.2f}"; f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:,.0f}"

S = []
def slide(body, cls=""): S.append(f'<section class="{cls}">{body}</section>')
def screen(src, kicker, title, quote, n):
    slide(f'''<img class="bleed" src="{src}"><div class="tag">{kicker}</div>
    <div class="quote"><div class="qn">{n}</div><h2>{title}</h2><p>{quote}</p></div>''', "screen")

# 1 cover
slide(f'''<img class="bleed art" src="{fig('dashboard/riyadh_heat.png')}">
<div class="cover"><div class="kick">Arab Youth Space Hackathon 2026 · Challenge 813 · Team T0049</div>
<h1>QAYDH <span>القيظ</span></h1><h2>Heat-risk intelligence for fast-growing Gulf cities</h2>
<div class="team">انتصار الحبسي · نورة الهاجري · مريم البني</div></div>''', "dark")

# 2 why
slide(f'''<div class="split"><div><div class="kick">Why QAYDH</div><h1 class="big">A heat map says where.<br>A city needs who, why and what next.</h1></div>
<dl class="why">
<dt>Challenge</dt><dd>Summer surfaces pass 50 °C. Cooling budgets are spent case by case.</dd>
<dt>Significance</dt><dd>People still walk to prayer, wait for buses, deliver and build outdoors at noon.</dd>
<dt>Impact</dt><dd>Shade, cool roofs and trees go first where people are exposed.</dd>
<dt>Solution</dt><dd>Hyperspectral + thermal + people data → one ranked action map.</dd></dl></div>''')

# 3 people
slide(f'''<div class="kick">The people in the heat</div><h1 class="big">{w['danger_window_local']}: above 40 °C on most summer days</h1>
<div class="four">
<div><b>Worshippers</b><span>walking to Dhuhr and Asr</span></div>
<div><b>Bus riders</b><span>waiting at unshaded stops</span></div>
<div><b>Delivery riders</b><span>idling outside restaurants</span></div>
<div><b>Workers</b><span>on construction sites</span></div></div>
<div class="strip"><div><b>{f0(R['residents_hot20'])}</b>residents in the hottest fifth of east Riyadh</div>
<div><b>{f2(g['bus_stop']['hottest_20pct'])} vs {f2(g['bus_stop']['rest_of_city'])}</b>mapped bus stops per 10,000 people, hottest vs rest</div>
<div><b>{f1(w['heat_hours_ge40_per_day'])} h</b>a day at or above 40 °C</div></div>''')

# 4 solution overview
slide(f'''<div class="kick">Solution overview</div><h1 class="big">Five questions, one map</h1>
<div class="five">
<div><i>Where</i><b>Persistent hotspots</b><span>Landsat LST, 3 summers</span></div>
<div><i>When</i><b>Danger hours</b><span>ERA5 hourly weather</span></div>
<div class="hs"><i>Why</i><b>Roof · road · sand</b><span>Planet Tanager 426 bands</span></div>
<div><i>Who</i><b>People outdoors</b><span>WorldPop + OpenStreetMap</span></div>
<div class="go"><i>What next</i><b>Named action + °C</b><span>300 m priority cells</span></div></div>''')

# 5 data & tools (Ghaf-style three blocks)
slide(f'''<div class="split"><div><div class="kick">Data &amp; tools</div><h1 class="big">Open data.<br>One notebook.<br>Run all.</h1></div>
<dl class="why">
<dt>Data</dt><dd>Planet Tanager hyperspectral · Landsat 8/9 SR + thermal · ESA WorldCover · Impact Observatory · WorldPop 2025 · OpenStreetMap · Microsoft building footprints · Open-Meteo/ERA5</dd>
<dt>Tools</dt><dd>Python · Planetary Computer STAC · scikit-learn · Leaflet dashboard · gIQ-ready GeoJSON</dd>
<dt>Steps</dt><dd>Cloud &amp; quality masks → automatic labels → model training → spatial validation → ranked actions → dashboard</dd></dl></div>''')

# 6-11 story-map screens (product walkthrough)
screen(SC["grow"], "Where", f"+{R['growth_pct']:.0f}% built-up since 2014", f"{f0(R['built_km2_before'])} → {f0(R['built_km2_after'])} km². Our map scores F1 {f2(R['cv_built_f1_rf'])} against the starter rule's {f2(R['cv_built_f1_ndbi'])}.", "01")
screen(SC["heat"], "Where", "The same streets burn every summer", f"Established districts average {f1(est['mean_LST'])} °C. Hot cells repeat year to year (r = {f2(R['lst_cells_r_2024_vs_2025'])}). The starter NDBI proxy explains none of it (r = {f2(R['ndbi_lst_r_builtup'])}).", "02")
screen(SC["when"], "When", f"Danger from {w['danger_window_local'].split('–')[0]}", f"Above 40 °C for {f1(w['heat_hours_ge40_per_day'])} hours a day, across both afternoon prayers.", "03")
screen(SC["why"], "Why", "Roof, road or sand", f"Labels come free from OpenStreetMap and building footprints. The full spectrum scores F1 {f2(mc[kh]['macro_F1'])} on unseen tiles; the starter index rules score {f2(mc[ki]['macro_F1'])}.", "04")
screen(SC["who"], "Who", "Where people are outside", f"Counting people instead of buildings changes {R['top20_changed_by_people_layer_pct']:.0f}% of the top-20 priorities.", "05")
screen(SC["act"], "What next", "One hotspot, one decision", f"Who is exposed, why it is hot, what to do, the cooling estimate and a public alert. Cool roofs: {cool[0]:+.2f} °C per +0.10 albedo.", "06")

# 12 model architecture
slide(f'''<div class="kick">Model architecture</div><h1 class="big">Surface intelligence from automatic labels</h1>
<div class="pipe">
<div>OSM roads<br>+ building outlines<br>+ WorldCover</div><em>→</em>
<div>Clean pixels<br>≥50% roof · ≥60% road</div><em>→</em>
<div class="hs">Tanager spectra<br>98 bands</div><em>→</em>
<div>Random Forest<br>leave-one-tile-out</div><em>→</em>
<div class="go">Roof / road / sand<br>per 300 m cell</div></div>
<div class="three">
<div><b>Why it fits</b><span>Spectral shape separates asphalt, roofs and sand that look alike in RGB.</span></div>
<div><b>Why Random Forest</b><span>Small labels, many bands, explainable. Bigger models did not earn their place.</span></div>
<div><b>Why tiles</b><span>Testing on unseen tiles stops neighbouring pixels from leaking.</span></div></div>''')

# 13 evidence
slide(f'''<div class="kick">Validation</div><h1 class="big">Every claim has a number</h1>
<div class="nums">
<div><b>{f2(R['cv_built_f1_rf'])}</b><span>built-up F1 · spatial CV<br>starter rule {f2(R['cv_built_f1_ndbi'])}</span></div>
<div><b>{f2(R['indep2023_built_f1_rf'])}</b><span>F1 on independent<br>IO LULC 2023</span></div>
<div><b>{f2(mc[kh]['macro_F1'])}</b><span>surface F1, unseen tiles<br>6 bands {f2(mc[k6]['macro_F1'])} · rules {f2(mc[ki]['macro_F1'])}</span></div>
<div><b>+{f2(R['dR2_built'])}</b><span>R² for heat from adding<br>hyperspectral (built-up)</span></div>
<div><b>r {f2(R['coreg_r_after'])}</b><span>Tanager ↔ Landsat<br>co-registration</span></div>
<div><b>{f0(min(ov.values())*100)}–{f0(max(ov.values())*100)}%</b><span>top-20 stable under<br>re-weighting</span></div></div>''')

# 14 tradeoffs
slide(f'''<div class="split"><div><div class="kick">Known tradeoffs</div><h1 class="big">Where the edges are</h1></div>
<dl class="why">
<dt>Labels</dt><dd>Automatic labels carry noise. We keep clear pixels only and test on held-out tiles.</dd>
<dt>Heat</dt><dd>Landsat sees surfaces at 10:40. Air peaks {w['air_daily_max_minus_overpass_C']:+.1f} °C later; weather data sets the hours.</dd>
<dt>Spectra</dt><dd>Full spectrum gains {R['material_macroF1_gain_full_vs_6band']:+.2f} F1 over 6 bands for surfaces, +{f2(R['dR2_built'])} R² for heat. Modest, measured, reported.</dd>
<dt>People</dt><dd>We model where outdoor activity is likely. We do not track people.</dd></dl></div>''')

# 15 Abu Dhabi
screen(SC["ad"], "UAE transfer", "Abu Dhabi: Masdar reads hottest, and the reason is sand",
       f"Masdar {f1(ms['mean_LST_C'])} °C with {ms['builtup_QAYDH_RF_pct']:.0f}% built. The starter rule calls it {ms['builtup_starter_NDBI_pct']:.0f}% built and Musaffah {mu['builtup_starter_NDBI_pct']:.0f}%. Musaffah ranks first for people: {f0(mu['residents'])} residents, {mu['bus_stops']} bus stops, {mu['mosques']} mosques.", "07")

# 16 who benefits / business
slide(f'''<div class="kick">Who benefits</div><h1 class="big">From map to budget line</h1>
<div class="three">
<div><b>Municipalities</b><span>Annual city licence: ranked cells, actions, °C estimates, alerts.</span></div>
<div><b>Developers &amp; master-planners</b><span>Heat-aware design check before districts lock in.</span></div>
<div><b>Delivery platforms &amp; contractors</b><span>Rest points, shifts and routes for riders and workers.</span></div></div>
<div class="strip"><div><b>Dashboard</b>story map + hotspot cards</div><div><b>API</b>GeoJSON per 300 m cell</div><div><b>Alerts</b>summer brief + public heat alerts</div></div>
<p class="sdg">SDG 3 · 11 · 13 · UAE Net Zero 2050 · Abu Dhabi &amp; Dubai urban heat goals</p>''')

# 17 roadmap
slide(f'''<div class="split"><div><div class="kick">Incubation</div><h1 class="big">PoC → MVP</h1></div>
<dl class="why">
<dt>Data</dt><dd>Satellite 813 and MBZ-SAT hyperspectral over Abu Dhabi, Dubai and Al Ain</dd>
<dt>People</dt><dd>Labour housing and delivery-hub layers from municipal and platform partners</dd>
<dt>Truth</dt><dd>Weather-station calibration and 200–300 field-checked surface points</dd>
<dt>Product</dt><dd>gIQ dashboard with a what-if slider for roofs, trees and shaded stops</dd></dl></div>''')

# 18 close
slide(f'''<img class="bleed art" src="{fig('dashboard/riyadh_surfaces.png')}"><div class="cover"><h1>QAYDH <span>القيظ</span></h1>
<h2>Where it burns. Why. Who is outside. What to do first.</h2>
<div class="team">Notebook · dashboard · data: GitHub repository README</div></div>''', "dark")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:'IBM Plex Sans Arabic',Tahoma,sans-serif;color:#efe3cf;background:#14110e}
section{width:1600px;height:900px;position:relative;overflow:hidden;page-break-after:always;padding:80px 96px;background:#14110e}
section::after{content:"QAYDH · T0049";position:absolute;right:40px;bottom:24px;font:500 13px 'IBM Plex Mono';color:#6f6252;letter-spacing:.1em}
.kick{font:500 16px 'IBM Plex Mono';letter-spacing:.18em;text-transform:uppercase;color:#ffb15c}
h1{font:800 64px/1 'Big Shoulders Display';margin:14px 0 36px;color:#efe3cf;letter-spacing:.01em}
h1.big{font-size:76px;max-width:1250px}
h1 span,.cover h1 span{color:#ff6b2c;font-family:'IBM Plex Sans Arabic'}
.bleed{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bleed.art{object-fit:cover;filter:brightness(.55) saturate(1.2);opacity:.9}
.bleed.dim{filter:brightness(.42) saturate(1.1)}
.cover{position:absolute;left:96px;bottom:110px;max-width:1200px}
.cover h1{font-size:150px;margin:10px 0}
.cover h2{font:600 40px/1.2 'IBM Plex Sans Arabic';color:#ffcf9a;margin:0 0 26px}
.team{font:500 22px 'IBM Plex Sans Arabic';color:#efe3cf;opacity:.85}
.split{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;height:100%}
dl.why{display:grid;grid-template-columns:150px 1fr;gap:26px 28px;margin:0}
dl.why dt{font:500 15px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:#ff6b2c;padding-top:6px}
dl.why dd{margin:0;font-size:26px;line-height:1.35}
.four{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-top:10px}
.four div,.three div{border-top:4px solid #ff6b2c;padding-top:18px}
.four b,.three b{display:block;font:800 40px/1 'Big Shoulders Display';margin-bottom:10px}
.four span,.three span{font-size:22px;color:#cdbda4;line-height:1.35}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:36px;margin-top:40px}
.strip{position:absolute;left:96px;right:96px;bottom:80px;display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.strip div{font-size:19px;color:#cdbda4;line-height:1.3}
.strip b{display:block;font:800 54px/1 'Big Shoulders Display';color:#ff6b2c;margin-bottom:8px}
.five{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:20px}
.five div{background:#1f1a15;border:1px solid #3a3027;border-radius:14px;padding:30px 22px;min-height:330px;display:flex;flex-direction:column;gap:14px}
.five i{font:500 15px 'IBM Plex Mono';font-style:normal;letter-spacing:.16em;text-transform:uppercase;color:#ffb15c}
.five b{font:800 40px/1 'Big Shoulders Display'} .five span{font-size:19px;color:#cdbda4;margin-top:auto}
.five .hs{border-color:#ff6b2c} .five .go{background:#43c6b4;border-color:#43c6b4;color:#0d1f1c} .five .go span,.five .go i{color:#0d1f1c}
.screen{padding:0}
.screen .tag{position:absolute;top:28px;left:420px;font:500 15px 'IBM Plex Mono';letter-spacing:.18em;text-transform:uppercase;background:#ff6b2c;color:#1b0d05;padding:8px 14px;border-radius:999px}
.quote{position:absolute;right:56px;bottom:56px;width:560px;background:rgba(20,17,14,.94);border:1px solid #3a3027;border-left:6px solid #ff6b2c;border-radius:14px;padding:28px 32px}
.quote .qn{font:500 14px 'IBM Plex Mono';color:#ffb15c;letter-spacing:.16em}
.quote h2{font:800 42px/1.02 'Big Shoulders Display';margin:8px 0 12px}
.quote p{font-size:20px;line-height:1.4;margin:0;color:#e2d4bc}
.pipe{display:flex;align-items:stretch;gap:12px;margin-top:10px}
.pipe div{flex:1;background:#1f1a15;border:1px solid #3a3027;border-radius:14px;padding:26px 18px;font-size:22px;line-height:1.3;display:flex;align-items:center}
.pipe div.hs{border-color:#ff6b2c} .pipe div.go{background:#43c6b4;color:#0d1f1c;font-weight:600}
.pipe em{font-style:normal;font:800 40px 'Big Shoulders Display';color:#ff6b2c;align-self:center}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:46px 40px;margin-top:10px}
.nums b{display:block;font:800 104px/1 'Big Shoulders Display';color:#ff6b2c;font-variant-numeric:tabular-nums}
.nums span{font-size:21px;color:#cdbda4;line-height:1.3}
.sdg{position:absolute;left:96px;bottom:34px;font:500 15px 'IBM Plex Mono';color:#8f806b;letter-spacing:.08em}
"""
doc = f"<!doctype html><html><head><meta charset='utf-8'><title>QAYDH pitch</title><style>{CSS}</style></head><body>{''.join(S)}</body></html>"
hp = os.path.join(PITCH, "QAYDH_T0049_pitch.html"); open(hp, "w").write(doc)
pdf = os.path.join(PITCH, "QAYDH_T0049_pitch.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=10000", f"--print-to-pdf={pdf}", "file://" + hp], capture_output=True, timeout=300)
print("deck:", len(S), "slides ->", pdf, f"{os.path.getsize(pdf)/1e6:.1f} MB")
