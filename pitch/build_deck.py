"""QAYDH pitch deck, structured like the Ghaf Root reference deck (story-led, image-first, little text).
All numbers come from qaydh_outputs/results.json; screens come from the live dashboard (dashboard/index.html).
usage: python pitch/build_deck.py   (after the notebook and dashboard/build_dashboard.py)
"""
import json, os, base64, subprocess, io
import numpy as np, pandas as pd
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qaydh_outputs"); D = os.path.join(OUT, "dashboard"); PITCH = os.path.join(ROOT, "pitch"); SHOTS = os.path.join(PITCH, "screens")
os.makedirs(SHOTS, exist_ok=True)
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
R = json.load(open(os.path.join(OUT, "results.json")))
MH = pd.read_csv(os.path.join(OUT, "musaffah_hotspots.csv")); MS = pd.read_csv(os.path.join(OUT, "musaffah_exposure_sites.csv"))

# ---------------- dashboard screens (story-map frames) ----------------
DASH = open(os.path.join(ROOT, "dashboard", "index.html")).read().replace("</style>", "#intro{display:none!important}</style>", 1)
def shot(name, js, w=1600, h=950):
    p = os.path.join(SHOTS, name + ".png"); tmp = os.path.join(SHOTS, "_tmp.html")
    open(tmp, "w").write(DASH.replace("build();\n</script>", f"build();setTimeout(()=>{{{js}}},500);\n</script>"))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", "--virtual-time-budget=9000",
                    f"--screenshot={p}", "file://" + tmp], capture_output=True, timeout=180)
    os.remove(tmp); return p
mus = "document.getElementById('city-musaffah').click();"
SC = dict(m_where=shot("m1_where", mus + "setTimeout(()=>goChapter(0),300)"),
          m_who=shot("m2_who", mus + "setTimeout(()=>{goChapter(1);showSite(0)},300)"),
          m_what=shot("m3_what", mus + "setTimeout(()=>goChapter(2),300)"),
          m_labels=shot("m35_labels", mus + "setTimeout(()=>{goChapter(3);map.setView([" + str(MH.iloc[0].lat) + "," + str(MH.iloc[0].lon) + "],16)},300)"),
          m_why=shot("m4_why", mus + "setTimeout(()=>goChapter(4),300)"),
          m_act=shot("m5_act", mus + "setTimeout(()=>showHot(0),300)"),
          r_why=shot("r_why", "goChapter(3)"),
          r_when=shot("r_when", "goChapter(2)"),
          ad=shot("ad", "document.getElementById('city-abudhabi').click();setTimeout(()=>goChapter(2),300)"))

# ---------------- crisp crops from our own layers (Sentinel-2 10 m + 2 m buildings/roads) ----------------
meta = json.load(open(os.path.join(D, "musaffah_overlays.json"))); (la0, lo0), (la1, lo1) = meta["bounds"]
SAT = Image.open(os.path.join(D, "musaffah_satellite.png")).convert("RGBA"); GEO = Image.open(os.path.join(D, "musaffah_geometry.png")).convert("RGBA")
HAZ = Image.open(os.path.join(D, "musaffah_hazard.png")).convert("RGBA"); SURF = Image.open(os.path.join(D, "musaffah_surfaces.png")).convert("RGBA")
def crop(lat, lon, half_m=450, layers=("sat", "geo"), size=900):
    def box_(im):
        W, H = im.size; x = (lon - lo0) / (lo1 - lo0) * W; y = (la1 - lat) / (la1 - la0) * H; r = half_m / 10 * (W / SAT.size[0])
        return im.crop((int(x - r), int(y - r), int(x + r), int(y + r))).resize((size, size), Image.NEAREST if im is not SAT else Image.BICUBIC)
    base = box_(SAT)
    for l in layers[1:]:
        ov = box_({"geo": GEO, "haz": HAZ, "surf": SURF}[l]); base = Image.alpha_composite(base, ov)
    b = io.BytesIO(); base.convert("RGB").save(b, "JPEG", quality=88); return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
ICONS = os.path.join(PITCH, "icons")
def icon(n, size=56, color="#ff6b2c"):
    svg = open(os.path.join(ICONS, n + ".svg")).read()
    return svg.replace('stroke="currentColor"', f'stroke="{color}"').replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
def img(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
def fig(n): return img(os.path.join(OUT, n))
h0 = MH.iloc[0]
camp = MS[MS.name.str.contains("camp", case=False, na=False)]; camp = camp.iloc[0] if len(camp) else MS.iloc[0]
bus = MS[MS.site == "Bus stop"].iloc[0]; mosque = MS[MS.site == "Mosque"].iloc[0]
COL = [(crop(h0.lat, h0.lon, layers=("sat", "geo", "haz")), f"Hotspot {h0.id}", f"P{h0.heat_pct} heat · {h0.road*100:.0f}% pavement"),
       (crop(bus.lat, bus.lon), f"Bus stop · {bus['name'][:28]}", f"P{bus.heat_percentile} heat · {bus.vegetation_pct}% green"),
       (crop(camp.lat, camp.lon), f"{camp.site} · {camp['name'][:28]}", f"P{camp.heat_percentile} heat · nearest green {camp.nearest_green_m:.0f} m"),
       (crop(mosque.lat, mosque.lon, layers=("sat", "surf")), "What is physically there", "road · roof · sand · green at 10 m")]

# ---------------- numbers ----------------
f2 = lambda x: f"{x:.2f}"; f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:,.0f}"
mc = {d["approach"]: d for d in R["musaffah_classifier"]["scores"]}; mbest = R["musaffah_classifier"]["chosen"]; mrule = [k for k in mc if k.startswith("Index")][0]
wm = {d["model"]: d for d in R["musaffah_why_model"]["scores"]}; th = R["musaffah_hazard_thresholds_C"]; ann = R["musaffah_annotation"]; sites = R["musaffah_sites"]
hs = {d["approach"]: d for d in R["material_classifier"]["scores"]}; hk = [k for k in hs if k.startswith("Full")][0]; h6 = [k for k in hs if k.startswith("6")][0]
w = R["weather"]; ad = R["abudhabi"]; dist = {d["district"]: d for d in ad["districts"]}; mu, ms = dist["Musaffah industrial"], dist["Masdar City"]
ov = R["hrpi_top20_overlap"]; cool = R["cooling_per_0p1_albedo_C"]

S = []
def slide(body, cls=""): S.append(f'<section class="{cls}">{body}</section>')
def screen(src, kicker, title, quote, n):
    slide(f'<img class="bleed" src="{src}"><div class="quote"><div class="qn">{n} · {kicker}</div><h2>{title}</h2><p>{quote}</p></div>', "screen")

# 1 cover
slide(f'''<img class="bleed art" src="{img(os.path.join(D, 'musaffah_satellite.png'))}"><img class="bleed art2" src="{img(os.path.join(D, 'musaffah_hazard.png'))}">
<div class="cover"><div class="kick">Arab Youth Space Hackathon 2026 · Challenge 813 · Theme 2</div><h1>QAYDH <span>القيظ</span></h1>
<h2>Urban heat risk, through the eyes of satellites</h2><div class="team">Team T0049 · United Arab Emirates</div></div>''', "dark")
# 2 agenda
slide('''<div class="split"><div><div class="kick">Agenda</div><h1 class="big">From where it is hot<br>to where we act first</h1></div>
<ol class="agenda"><li>Team</li><li>The heat problem</li><li>QAYDH</li><li>Approach &amp; tools</li><li>The Musaffah story</li><li>Proof</li><li>Impact &amp; value</li><li>Closing</li></ol></div>''')
# 3 team
slide('''<div class="kick">Team T0049</div><h1 class="big">Three people, one city problem</h1>
<div class="three team3"><div><b>انتصار الحبسي</b><span>Team lead</span></div><div><b>نورة الهاجري</b><span>Team member</span></div><div><b>مريم البني</b><span>Team member</span></div></div>''')
# 4 title
slide(f'''<div class="split"><div><div class="kick">QAYDH · القيظ</div><h1 class="big">The fierce heat of summer,<br>mapped where people live and work</h1>
<p class="lead">Heat · surfaces · people · action, from open satellite data.</p></div><img class="photo" src="{COL[0][0]}"></div>''')
# 5 why + impact (Ghaf: challenge / significance / impact / solution)
slide(f'''<div class="split"><div><h1 class="big">Why QAYDH as a solution?<br><span class="o">What is its impact?</span></h1></div>
<dl class="why"><dt>Challenge</dt><dd>Surfaces pass 55 °C. Cooling budgets are spent case by case.</dd>
<dt>Significance</dt><dd>Workers, riders, worshippers and bus riders are outside {w['danger_window_local']}.</dd>
<dt>Impact</dt><dd>Shade, cool surfaces and trees go first where people are exposed.</dd>
<dt>Solution</dt><dd>Thermal + hyperspectral + 10 m surfaces + OSM → one ranked action map.</dd></dl></div>
<div class="filmstrip">{''.join(f'<img src="{c[0]}">' for c in COL)}</div>''')
# 5b problem · what exists · gap
slide(f'''<div class="kick">The problem we solve</div><h1 class="big">Heat maps exist. Decisions don't.</h1>
<div class="cmp"><div><h3>{icon("eye", 40, "#b3a48e")} What exists today</h3><ul>
<li>City heat maps: they show where, not who or why</li><li>Starter NDBI rule: calls {mu['builtup_starter_NDBI_pct']:.0f}% of Musaffah "built"</li>
<li>Site surveys: slow, one district at a time</li><li>Generic advice: "plant trees" everywhere</li></ul></div>
<div class="arrow">{icon("arrow-right", 64)}</div>
<div class="hl"><h3>{icon("shield-check", 40, "#43c6b4")} What QAYDH adds</h3><ul>
<li>People: who is outside, at which hours</li><li>Surfaces: road, roof, sand, green at 10 m (F1 {mc[mbest]['test_macro_F1']:.2f})</li>
<li>Every Gulf city, every summer, open data</li><li>One named action per hotspot, with its reason</li></ul></div></div>''')
# 6 collage
slide(f'''<div class="kick">Musaffah, Abu Dhabi</div><h1 class="big">Real places, not pixels</h1>
<div class="collage">{''.join(f'<figure><img src="{c[0]}"><figcaption><b>{c[1]}</b>{c[2]}</figcaption></figure>' for c in COL)}</div>
<p class="credit">Sentinel-2 10 m · buildings: Microsoft + OSM · roads: OSM · heat: Landsat</p>''')
# 7 solution overview: five questions, step by step, with icons and real crops
steps = [("flame", "Where is heat high?", "Landsat hazard zones · 3 summers · danger hours", crop(h0.lat, h0.lon, 700, ("sat", "haz"))),
         ("users", "Who may be exposed?", "Bus stops · mosques · clinics · camps · residents", crop(bus.lat, bus.lon, 700)),
         ("scan", "What is there?", "Road · roof · sand · green at 10 m", crop(h0.lat, h0.lon, 700, ("sat", "surf"))),
         ("temperature", "Why may it be hot?", f"Driver model R² {wm['Random Forest']['R2']:.2f}", crop(h0.lat, h0.lon, 700, ("sat", "geo"))),
         ("target", "What should be done?", "Ranked action + reason + brief", crop(h0.lat, h0.lon, 350, ("sat", "geo", "haz")))]
slide('<div class="kick">Solution overview</div><h1 class="big">Five questions, answered step by step</h1><div class="steps5">' +
      "".join(f'<div><div class="ic">{icon(i_, 44)}</div><i>{k+1}</i><b>{t}</b><span>{d_}</span><img src="{im}"></div>' for k, (i_, t, d_, im) in enumerate(steps)) + "</div>")

# 8 splash with three lenses (Ghaf: GreenScope · Palm / Ghaf / Mangrove)
slide(f'''<h1 class="splash">QAYDH <span>القيظ</span></h1><div class="lenses">
<figure><img src="{crop(h0.lat, h0.lon, 900, ("sat", "haz"))}"><figcaption>Heat</figcaption></figure>
<figure><img src="{crop(h0.lat, h0.lon, 900, ("sat", "surf"))}"><figcaption>Surfaces</figcaption></figure>
<figure><img src="{crop(h0.lat, h0.lon, 900, ("sat", "geo"))}"><figcaption>People &amp; places</figcaption></figure></div>''', "dark")
# 9 data & tools (Ghaf: data / tools / application steps)
slide(f'''<div class="split"><div><h1 class="big">Data<br><span class="o">&amp; tools</span></h1></div>
<dl class="why"><dt>Data</dt><dd>Landsat 8/9 thermal · Sentinel-2 10 m · Planet Tanager hyperspectral · ESA WorldCover · OSM · Microsoft footprints · WorldPop · ERA5</dd>
<dt>Tools</dt><dd>Python · Planetary Computer · scikit-learn · QGIS-ready GeoJSON · gIQ-ready dashboard</dd>
<dt>Steps</dt><dd>Masks → annotation → training → spatial validation → priority → dashboard</dd></dl></div>''')
# 10 approach (Ghaf: short-term / long-term)
slide(f'''<div class="split"><div><h1 class="big">QAYDH<br><span class="o">Approach</span></h1></div>
<dl class="why"><dt>Now · PoC</dt><dd>Musaffah at 10 m, end to end · hyperspectral proof on Riyadh (Tanager) · Abu Dhabi screening</dd>
<dt>Next · MVP</dt><dd>Satellite 813 / MBZ-SAT over Abu Dhabi, Dubai, Al Ain · field-checked labels · gIQ</dd>
<dt>Later</dt><dd>Every Gulf city, every summer: one brief, one map, one budget line</dd></dl></div>''')
# 11-15 Musaffah story screens
screen(SC["m_where"], "Where is heat high?", "Hazard zones, not fake street temperatures", f"Extreme ≥ {f1(th['P95'])} °C. Landsat gives the zone; buildings and places tell us what falls inside it.", "01")
screen(SC["m_who"], "Who may be exposed?", f"{sites['n']} named outdoor sites", f"Each scored within 150 m: heat percentile, green, impervious cover, distance to shade.", "02")
screen(SC["m_what"], "What is physically there?", "Road · roof · sand · green · water", f"Held-out blocks: macro-F1 {f2(mc[mbest]['test_macro_F1'])}. Starter index rules: {f2(mc[mrule]['test_macro_F1'])}.", "03")
screen(SC["m_labels"], "How we labelled it", "Objects with ID, box and label", f"{R['musaffah_objects']['buildings']:,} buildings labelled: roof class, heat zone, dark-roof flag, street. {R['musaffah_objects']['cool_roof_candidates']} are cool-roof candidates.", "03b")
screen(SC["m_why"], "Why may it be hot?", "Asphalt and sand up, green down", f"Spatially validated: R² {f2(wm['Random Forest']['R2'])}, error {f1(wm['Random Forest']['MAE_C'])} °C. Shown as associations, not proof of cause.", "04")
screen(SC["m_act"], "What should be done?", f"Hotspot {h0.id}: one decision", f"{h0.actions}. Because {h0.why}.", "05")
# 16 hyperspectral proof + 17 Abu Dhabi screening
screen(SC["r_why"], "Hyperspectral proof · Riyadh", "Tanager reads roof, road and sand", f"Full spectrum F1 {f2(hs[hk]['macro_F1'])} vs 6 bands {f2(hs[h6]['macro_F1'])} on unseen tiles, and +{f2(R['dR2_built'])} R² for heat.", "06")
screen(SC["ad"], "Abu Dhabi screening", "The starter rule calls sand a city", f"NDBI says Masdar {ms['builtup_starter_NDBI_pct']:.0f}% built; WorldCover {ms['builtup_WorldCover_pct']:.0f}%. Musaffah: {mu['builtup_starter_NDBI_pct']:.0f}% vs {mu['builtup_WorldCover_pct']:.0f}%.", "07")
# 18 annotation / detection image (Ghaf: segmentation model visual)
slide(f'''<div class="kick">Annotation &amp; surface model</div><h1>Rule-based labels, honest tests</h1><img class="figw" src="{fig('11_musaffah_annotation_surfaces.png')}">''')
slide(f'''<div class="kick">Open AI models · SAM + LLM</div><h1>Segment, label, brief, then a person decides</h1><img class="figw" style="height:520px" src="{fig('13_musaffah_sam_objects.png')}">
<div class="strip" style="bottom:40px"><div><b>{R['sam']['segments']}</b>SAM segments, each with class, box and heat</div><div><b>{R['sam']['annotation_candidates']}</b>≥80% pure → annotation candidates</div>
<div><b>{R['llm_briefs']['llm_drafts_passing_fact_check']}/{R['llm_briefs']['n']}</b>LLM drafts passed the fact-check. The rest were caught and replaced</div></div>''')
# 19 architecture (icon diagram)
def col(title, items, cls=""):
    return f'<div class="acol {cls}"><h4>{title}</h4>' + "".join(f'<div class="aitem">{icon(i_, 30, "#ffb15c" if not cls else "#0d1f1c")}<span>{t}</span></div>' for i_, t in items) + "</div>"
slide('<div class="kick">Architecture</div><h1>From open satellites to a decision</h1><div class="arch">' +
      col("Data", [("satellite", "Landsat 8/9 thermal"), ("satellite", "Sentinel-2 10 m"), ("satellite", "Planet Tanager hyperspectral"), ("database", "WorldCover · Microsoft footprints"), ("map-pin", "OpenStreetMap · WorldPop"), ("sun", "ERA5 + NOAA stations")]) +
      f'<div class="aarr">{icon("arrow-right", 44)}</div>' +
      col("Process", [("checklist", "Cloud & quality masks"), ("scan", "Annotation ≥80% purity"), ("brain", "SAM segments · RF models"), ("chart-dots", "Spatial validation A–E")]) +
      f'<div class="aarr">{icon("arrow-right", 44)}</div>' +
      col("Answers", [("flame", "Hazard zones"), ("road", "Surface mix"), ("users", "Exposure sites"), ("temperature", "Heat drivers"), ("target", "Priority + action")]) +
      f'<div class="aarr">{icon("arrow-right", 44)}</div>' +
      col("Delivery", [("world", "Story dashboard"), ("database", "GeoJSON / API"), ("checklist", "Planner brief + sign-off"), ("clock", "Summer alerts")], "go") + "</div>")

# 20 why it fits
slide(f'''<div class="kick">Why it fits</div><h1 class="big">Matched to a desert city</h1>
<div class="four"><div><b>Sand looks built</b><span>Index rules call {mc[mrule].get('F1 Road / dark pavement',0)*100:.0f}% of roads right. The model: {mc[mbest]['F1 Road / dark pavement']*100:.0f}%.</span></div>
<div><b>Pixels are mixed</b><span>Only ≥80% pure pixels train; confidence is mapped.</span></div>
<div><b>Neighbours leak</b><span>Train, validate, test on separate 1 km blocks.</span></div>
<div><b>Heat is coarse</b><span>Thermal = zones; 10 m surfaces explain them.</span></div></div>''')
# 21 tradeoffs
slide(f'''<div class="split"><div><div class="kick">Known tradeoffs</div><h1 class="big">Being upfront</h1></div>
<dl class="why"><dt>Labels</dt><dd>Automatic candidates still carry noise. {ann['removed_as_noisy']:,} removed; a {300}-point review queue goes to QGIS.</dd>
<dt>Heat</dt><dd>Surface runs 11–15 °C above air (NOAA stations). We rank zones; ERA5, checked against stations, sets the hours.</dd>
<dt>Materials</dt><dd>No open hyperspectral over Musaffah yet. 813 plugs in.</dd>
<dt>People</dt><dd>Exposure opportunity, not head counts.</dd></dl></div>''')
# 22 proof
slide(f'''<div class="kick">Proof</div><h1 class="big">Every claim has a number</h1>
<div class="nums"><div><b>{f2(mc[mbest]['test_macro_F1'])}</b><span>Musaffah surfaces, held-out<br>starter rules {f2(mc[mrule]['test_macro_F1'])}</span></div>
<div><b>{f2(wm['Random Forest']['R2'])}</b><span>heat driver model R²<br>spatial CV</span></div>
<div><b>{f2(R['cv_built_f1_rf'])}</b><span>built-up F1 Riyadh<br>starter {f2(R['cv_built_f1_ndbi'])}</span></div>
<div><b>+{f2(R['dR2_built'])}</b><span>R² from hyperspectral<br>Riyadh built-up</span></div>
<div><b>{f2(R['lst_cells_r_2024_vs_2025'])}</b><span>hotspots repeat<br>2024 ↔ 2025</span></div>
<div><b>{f0(min(ov.values())*100)}–{f0(max(ov.values())*100)}%</b><span>priorities stable<br>under re-weighting</span></div></div>''')
# 23 who benefits (icon tiles)
ben = [("building-skyscraper", "Municipalities", "Ranked cells, actions and briefs"), ("building-factory", "Industrial zones", "Rest nodes, work-break planning"),
       ("bus", "Transport authorities", "Which bus stops to shade first"), ("motorbike", "Delivery platforms", "Rider cooling points and hours"),
       ("crane", "Contractors", "Outdoor-work heat safety"), ("home", "Residents", "Shade on the routes they walk")]
slide('<div class="kick">Who benefits</div><h1 class="big">Six users, one map</h1><div class="tiles">' +
      "".join(f'<div>{icon(i_, 52)}<b>{t}</b><span>{d_}</span></div>' for i_, t, d_ in ben) + "</div>")

# 24 solution value + impact (icon tiles + numbers)
st_ = {d["station"]: d for d in R.get("station_check", [])}
slide(f'''<div class="kick">Solution value &amp; impact</div><h1 class="big">Value you can measure</h1><div class="tiles four4">
<div>{icon("users", 52)}<b>{f0(R['residents_hot20'])}</b><span>residents in the hottest fifth of east Riyadh</span></div>
<div>{icon("building-skyscraper", 52)}<b>{R['musaffah_objects']['cool_roof_candidates']}</b><span>cool-roof candidates in Musaffah</span></div>
<div>{icon("bus", 52)}<b>{sites['very_high'] + sites['high']}</b><span>exposure sites at high or very high priority</span></div>
<div>{icon("leaf", 52)}<b>{cool[0]:+.2f} °C</b><span>per +0.10 roof albedo (95% CI)</span></div></div>
<p class="sdg">Aligned with UAE Net Zero 2050 · We the UAE 2031 · Abu Dhabi urban heat goals · SDG 3 · 11 · 13</p>''')
# 24b ground truth
if st_:
    slide(f'''<div class="kick">Ground truth · NOAA weather stations</div><h1>Checked against real thermometers</h1><img class="figw" style="height:430px" src="{fig('14_station_validation.png')}">
    <div class="strip" style="bottom:50px">{"".join(f"<div><b>r {d['era5_vs_station_r']:.2f}</b>{n}: ERA5 vs station · danger {d['danger_window_station']}</div>" for n, d in list(st_.items())[:3])}</div>''')
# 24c see it work (storyboard from the GIF)
from PIL import ImageSequence
g_ = Image.open(os.path.join(PITCH, "gifs", "qaydh_musaffah_tour.gif")); frs = [f.convert("RGB") for f in ImageSequence.Iterator(g_)]
def fb(f): b = io.BytesIO(); f.save(b, "JPEG", quality=85); return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
lab_ = ["Where", "Who", "What", "Labels", "Why", "Act", "Hotspot card", "Site card"]
slide('<div class="kick">See it work · animated walkthrough in the repo</div><h1>The dashboard, step by step</h1><div class="story8">' +
      "".join(f'<figure><img src="{fb(f)}"><figcaption>{k+1} · {lab_[k]}</figcaption></figure>' for k, f in enumerate(frs[:8])) + "</div>")

# 25 closing
exec(open(os.path.join(PITCH, "judging_slides.py")).read())   # Q1 business problem · Q2 validation · Q3 delivery · coverage · SAR/roofs/informal/heat-proxy
slide(f'''<img class="bleed art" src="{img(os.path.join(D, 'musaffah_satellite.png'))}"><img class="bleed art2" src="{img(os.path.join(D, 'musaffah_geometry.png'))}">
<div class="cover"><h1>QAYDH <span>القيظ</span></h1><h2>From “where is it hot?” to “where we act first, why, and how.”</h2>
<div class="team">Musaffah → Abu Dhabi → UAE → Gulf cities</div></div>''', "dark")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:'IBM Plex Sans Arabic',Tahoma,sans-serif;color:#efe3cf;background:#14110e}
section{width:1600px;height:900px;position:relative;overflow:hidden;page-break-after:always;padding:80px 96px;background:#14110e}
section::after{content:"QAYDH · T0049";position:absolute;right:40px;bottom:24px;font:500 13px 'IBM Plex Mono';color:#6f6252;letter-spacing:.1em}
.kick{font:500 16px 'IBM Plex Mono';letter-spacing:.18em;text-transform:uppercase;color:#ffb15c}
h1{font:800 60px/1 'Big Shoulders Display';margin:12px 0 24px}
h1.big{font-size:84px;line-height:.98;max-width:1250px}
h1 span,.o{color:#ff6b2c} h1 span{font-family:'IBM Plex Sans Arabic'}
.lead{font-size:28px;color:#cdbda4;max-width:620px}
.bleed{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bleed.art{filter:brightness(.45) saturate(1.1)} .bleed.art2{opacity:.75;mix-blend-mode:screen}
.cover{position:absolute;left:96px;bottom:110px;max-width:1250px}
.cover h1{font-size:160px;margin:6px 0}
.cover h2{font:600 40px/1.2 'IBM Plex Sans Arabic';color:#ffcf9a;margin:0 0 24px}
.team{font:500 24px 'IBM Plex Sans Arabic';opacity:.9}
.split{display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:center;height:100%}
dl.why{display:grid;grid-template-columns:170px 1fr;gap:28px 28px;margin:0}
dl.why dt{font:500 15px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:#ff6b2c;padding-top:6px}
dl.why dd{margin:0;font-size:27px;line-height:1.32}
ol.agenda{font:800 44px/1.5 'Big Shoulders Display';margin:0;padding-left:60px;color:#efe3cf} ol.agenda li::marker{color:#ff6b2c;font-size:28px}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:36px;margin-top:30px}
.three div,.four div{border-top:4px solid #ff6b2c;padding-top:18px}
.three b,.four b{display:block;font:800 40px/1.05 'Big Shoulders Display';margin-bottom:10px}
.three span,.four span{font-size:22px;color:#cdbda4;line-height:1.35}
.team3 b{font:600 46px 'IBM Plex Sans Arabic'}
.four{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin-top:20px}
.photo{width:100%;height:700px;object-fit:cover;border-radius:18px}
.filmstrip{position:absolute;left:0;right:0;bottom:0;height:180px;display:grid;grid-template-columns:repeat(4,1fr)}
.filmstrip img{width:100%;height:100%;object-fit:cover}
section:has(.filmstrip) .split{height:560px}
.collage{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.collage figure{margin:0} .collage img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:12px;display:block}
.collage figcaption{font-size:18px;color:#cdbda4;margin-top:10px} .collage figcaption b{display:block;color:#efe3cf;font-size:20px}
.credit{position:absolute;left:96px;bottom:30px;font:500 13px 'IBM Plex Mono';color:#8f806b}
.mods{display:grid;grid-template-columns:1fr 1fr;gap:26px 34px}
.mods div{display:grid;grid-template-columns:52px 1fr;gap:4px 14px} .mods i{grid-row:span 2;font:800 52px/1 'Big Shoulders Display';color:#ff6b2c;font-style:normal}
.mods b{font:800 32px/1.05 'Big Shoulders Display'} .mods span{font-size:20px;color:#cdbda4}
.splash{font:800 190px/1 'Big Shoulders Display';text-align:center;margin:40px 0 50px} .splash span{color:#ff6b2c;font-family:'IBM Plex Sans Arabic'}
.lenses{display:grid;grid-template-columns:repeat(3,320px);gap:40px;justify-content:center}
.lenses figure{margin:0;text-align:center} .lenses img{width:320px;height:320px;object-fit:cover;border-radius:16px;display:block}
.lenses figcaption{font:800 34px 'Big Shoulders Display';color:#ffcf9a;margin-top:14px}
.screen{padding:0}
.quote{position:absolute;left:400px;bottom:40px;width:640px;background:rgba(20,17,14,.95);border:1px solid #3a3027;border-left:6px solid #ff6b2c;border-radius:14px;padding:26px 30px}
.quote .qn{font:500 14px 'IBM Plex Mono';color:#ffb15c;letter-spacing:.14em;text-transform:uppercase}
.quote h2{font:800 40px/1.02 'Big Shoulders Display';margin:8px 0 12px} .quote p{font-size:20px;line-height:1.4;margin:0;color:#e2d4bc}
.figw{width:100%;height:690px;object-fit:contain;background:#fff;border-radius:12px}
.pipe{display:flex;gap:10px;margin-top:10px}
.pipe div{flex:1;background:#1f1a15;border:1px solid #3a3027;border-radius:14px;padding:24px 16px;font-size:21px;line-height:1.3;display:flex;align-items:center}
.pipe div.hs{border-color:#ff6b2c} .pipe div.go{background:#43c6b4;color:#0d1f1c;font-weight:600}
.pipe em{font-style:normal;font:800 36px 'Big Shoulders Display';color:#ff6b2c;align-self:center}
.strip{position:absolute;left:96px;right:96px;bottom:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.strip div{font-size:19px;color:#cdbda4;line-height:1.3} .strip b{display:block;font:800 54px/1 'Big Shoulders Display';color:#ff6b2c;margin-bottom:6px}
.steps5{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.steps5>div{background:#1f1a15;border:1px solid #3a3027;border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:8px}
.steps5 i{font:800 40px/1 'Big Shoulders Display';font-style:normal;color:#ff6b2c} .steps5 b{font:800 28px/1.05 'Big Shoulders Display'} .steps5 span{font-size:16px;color:#cdbda4;min-height:44px}
.steps5 img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px;margin-top:auto}
.cmp{display:grid;grid-template-columns:1fr 90px 1fr;gap:20px;align-items:center}
.cmp>div:not(.arrow){background:#1f1a15;border:1px solid #3a3027;border-radius:18px;padding:28px} .cmp .hl{border-color:#43c6b4}
.cmp h3{display:flex;align-items:center;gap:12px;font:800 34px 'Big Shoulders Display';margin:0 0 14px;color:#efe3cf}
.cmp ul{margin:0;padding-left:22px;font-size:24px;line-height:1.55;color:#e2d4bc}
.arch{display:flex;gap:10px;align-items:stretch}
.acol{flex:1;background:#1f1a15;border:1px solid #3a3027;border-radius:16px;padding:20px} .acol.go{background:#43c6b4;border-color:#43c6b4;color:#0d1f1c}
.acol h4{font:800 30px 'Big Shoulders Display';margin:0 0 14px;color:#ff6b2c} .acol.go h4{color:#0d1f1c}
.aitem{display:flex;align-items:center;gap:12px;font-size:19px;margin:12px 0} .aarr{align-self:center}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:26px} .tiles.four4{grid-template-columns:repeat(4,1fr)}
.tiles>div{background:#1f1a15;border:1px solid #3a3027;border-radius:16px;padding:26px;display:flex;flex-direction:column;gap:10px}
.tiles b{font:800 40px/1.05 'Big Shoulders Display'} .tiles.four4 b{font-size:64px;color:#ff6b2c} .tiles span{font-size:20px;color:#cdbda4}
.story8{display:grid;grid-template-columns:repeat(4,1fr);gap:14px} .story8 figure{margin:0} .story8 img{width:100%;border-radius:10px;display:block}
.story8 figcaption{font:500 15px 'IBM Plex Mono';color:#ffb15c;margin-top:6px}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:46px 40px}
.nums b{display:block;font:800 108px/1 'Big Shoulders Display';color:#ff6b2c} .nums span{font-size:21px;color:#cdbda4;line-height:1.3}
ul.ben{list-style:none;padding:0;margin:0;font:600 34px/1.7 'IBM Plex Sans Arabic'} ul.ben li{border-bottom:1px solid #3a3027}
"""
doc = f"<!doctype html><html><head><meta charset='utf-8'><title>QAYDH pitch</title><style>{CSS}{globals().get('EXTRA_CSS', '')}</style></head><body>{''.join(S)}</body></html>"
hp = os.path.join(PITCH, "QAYDH_T0049_pitch.html"); open(hp, "w").write(doc)
pdf = os.path.join(PITCH, "QAYDH_T0049_pitch.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=12000", f"--print-to-pdf={pdf}", "file://" + hp], capture_output=True, timeout=300)
print("deck:", len(S), "slides ->", pdf, f"{os.path.getsize(pdf)/1e6:.1f} MB")
