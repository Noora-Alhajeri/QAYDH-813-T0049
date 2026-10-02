"""Build the QAYDH pitch deck (HTML -> PDF via headless Chrome) from qaydh_outputs/results.json.
Every number on the slides comes from the notebook run, so the deck never drifts from the evidence.
usage: python pitch/build_deck.py   (from the repo root, after running the notebook)
"""
import json, os, base64, subprocess, html
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qaydh_outputs"); PITCH = os.path.join(ROOT, "pitch")
R = json.load(open(os.path.join(OUT, "results.json")))
HOT = pd.read_csv(os.path.join(OUT, "top_hotspots.csv"))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def img(name):
    p = os.path.join(OUT, name) if not os.path.isabs(name) else name
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

z = {d["zone"]: d for d in R["lst_by_zone"]}
zk = lambda pre: next(v for k, v in z.items() if k.startswith(pre))
est, new, des, veg = zk("Established"), zk("New"), zk("Desert"), zk("Vegetation")
lm = {(d["subset"][:3], d["features"][0]): d for d in R["lst_model"]}
cool = R["cooling_per_0p1_albedo_C"]; gap = R["amenities_per_10k_hot_vs_rest"]
ov = R["hrpi_top20_overlap"]; chg = R["change_agreement_2017_2023"]
f2 = lambda x: f"{x:.2f}"; f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:,.0f}"

# ---- dashboard screenshot (interactive map) ----
shot = os.path.join(PITCH, "dashboard.png")
if os.path.exists(CHROME):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1500,900",
                    "--virtual-time-budget=15000", f"--screenshot={shot}",
                    "file://" + os.path.join(OUT, "qaydh_interactive_map.html")], capture_output=True, timeout=120)

top = HOT.head(5)
hot_rows = "".join(
    f"<tr><td>#{int(r['rank'])}</td><td>{r.lat:.4f}, {r.lon:.4f}</td><td>{r.LST_C:.1f} °C</td>"
    f"<td>{f0(r.population)}</td><td>{html.escape(str(r.recommended_action))}</td></tr>" for _, r in top.iterrows())

def gap_row(k, label):
    g = gap[k]; h, o = g["hottest_20pct"], g["rest_of_city"]
    ratio = (o / h) if h > 0 else float("inf")
    rtxt = "none mapped" if h == 0 else (f"{ratio:.1f}× fewer" if ratio > 1 else f"{1/ratio:.1f}× more")
    return f"<tr><td>{label}</td><td>{h:.2f}</td><td>{o:.2f}</td><td><b>{rtxt}</b></td></tr>"

slides = []
S = slides.append

S(f"""<section class="title">
  <div class="kicker">Arab Youth Space Hackathon 2026 · Challenge 813 · Team T0049</div>
  <h1>QAYDH <span class="ar">القيظ</span></h1>
  <h2>Heat-risk intelligence for fast-growing Gulf cities</h2>
  <p class="lead">Where the city grew · which districts burn hottest · <b>which materials</b> make them hot · <b>who is outside</b> in that heat. One map that tells planners where to act first, and with what.</p>
  <div class="meta">Theme: Sustainable Urban Planning &amp; Smart Cities, Urban Expansion, Land Use Change &amp; Heat Risk · SDG 3 · 11 · 13</div>
  <div class="meta">Team: انتصار الحبسي (lead) · نورة الهاجري · مريم البني</div>
</section>""")

S(f"""<section>
  <div class="kicker">01 · Problem</div><h2>Gulf summers are getting hotter, and people still have to be outside</h2>
  <div class="cols">
   <div>
    <ul class="big">
     <li>Gulf cities are among the fastest-growing on Earth. Surfaces pass <b>50 °C</b> in summer (median LST here: <b>{f1(est['mean_LST'])} °C</b> in established districts).</li>
     <li>Every new district locks in its roofs, roads and greenery for decades.</li>
     <li>Planners decide cool roofs, trees and shade <b>case by case</b>. There is no routine city-wide view linking <b>growth → heat → materials → people</b>.</li>
    </ul>
   </div>
   <div class="people">
     <div class="p"><span>🕌</span><b>Walking to Dhuhr &amp; Asr</b><br>prayers at peak heat</div>
     <div class="p"><span>🚌</span><b>Waiting at bus stops</b><br>often unshaded</div>
     <div class="p"><span>🛵</span><b>Delivery riders</b><br>waiting outside restaurants</div>
     <div class="p"><span>🏗️</span><b>Construction workers</b><br>outdoors all day</div>
   </div>
  </div>
  <div class="who"><b>User:</b> municipal planning &amp; heat-resilience offices &nbsp;·&nbsp; <b>Decision:</b> which neighbourhoods get cool roofs, shade trees, shaded bus stops, mosque-walkway shade or rider cooling points <i>first</i></div>
</section>""")

S(f"""<section>
  <div class="kicker">02 · Solution</div><h2>Five open-data layers, one decision map</h2>
  <div class="flow">
    <div class="box"><b>1 · Urban expansion</b><br>Landsat 2014→2025<br>Random Forest on WorldCover labels</div>
    <div class="box"><b>2 · Heat hazard</b><br>Landsat surface temperature<br>Jun–Aug 2025</div>
    <div class="box hs"><b>3 · Materials</b><br>Planet <b>Tanager</b> 426 bands<br>albedo · asphalt 1730 nm · concrete 2330 nm</div>
    <div class="box pe"><b>4 · People exposure</b><br>WorldPop 2025 + OpenStreetMap<br>mosques · bus stops · riders · workers</div>
    <div class="box out"><b>5 · Priority map</b><br>300 m cells · ranked<br>action + °C effect per cell</div>
  </div>
  <p class="lead">Heat-Risk Priority Index = <b>heat</b> × <b>people exposure</b> × <b>lack of greenery</b> × <b>new-district factor</b>, so each hotspot comes with a named intervention: cool roofs, shade trees, shaded bus shelters, mosque-walkway shade, rider cooling points, or midday work-break enforcement.</p>
  <p class="note">Portable by design: the Tanager footprint sets the area. Change one scene ID and the whole pipeline moves to another city. AOI here: east Riyadh (As Sali), {f0(R['population_aoi'])} residents, 470 km².</p>
</section>""")

S(f"""<section>
  <div class="kicker">03 · Data &amp; tools</div><h2>Open data only, fully reproducible</h2>
  <table class="t">
   <tr><th>Dataset</th><th>Use</th><th>Licence</th></tr>
   <tr><td><b>Planet Tanager</b> hyperspectral SR (open archive, 15 May 2025)</td><td>Materials, albedo, hyperspectral value test</td><td>CC-BY-4.0</td></tr>
   <tr><td>Landsat 8/9 C2 L2 (SR + surface temperature)</td><td>Land cover 2014/17/21/23/25, summer LST</td><td>Public domain</td></tr>
   <tr><td>ESA WorldCover 2021</td><td>Training labels (no manual annotation needed)</td><td>CC-BY-4.0</td></tr>
   <tr><td>Impact Observatory LULC 2017 / 2023</td><td>Independent validation</td><td>CC-BY-4.0</td></tr>
   <tr><td>WorldPop 2025 (100 m)</td><td>Residents per cell</td><td>CC-BY-4.0</td></tr>
   <tr><td>OpenStreetMap</td><td>Mosques, bus stops, rider hubs, construction, schools, clinics</td><td>ODbL</td></tr>
  </table>
  <p class="note">Python · Planetary Computer STAC · scikit-learn · one Colab notebook · every scene ID in <code>data_provenance.json</code> · no imagery in GitHub. Next: <b>gIQ</b> + Satellite 813 / MBZ-SAT in incubation.</p>
</section>""")

S(f"""<section>
  <div class="kicker">04 · Layer 1, urban expansion</div><h2>East Riyadh grew {f0(R['built_km2_before'])} → {f0(R['built_km2_after'])} km² (+{f0(R['growth_pct'])}%) since 2014</h2>
  <img class="wide" src="{img('01_urban_expansion.png')}">
  <div class="stats">
   <div><b>{f2(R['cv_built_f1_rf'])}</b><span>built-up F1, spatial-block CV<br>vs {f2(R['cv_built_f1_ndbi'])} for the official NDBI rule</span></div>
   <div><b>{f2(R['indep2023_built_f1_rf'])}</b><span>F1 on an <i>independent</i> map (IO LULC 2023)<br>vs {f2(R['indep2023_built_f1_ndbi'])} NDBI</span></div>
   <div><b>{f0(R['new_urban_km2'])} km²</b><span>confident new urban land<br>(p&gt;0.6 after, p&lt;0.4 before)</span></div>
  </div>
</section>""")

S(f"""<section>
  <div class="kicker">05 · Layer 2, heat hazard</div><h2>Peak-summer surface temperature, summer 2025</h2>
  <img class="wide" src="{img('02_heat_hazard.png')}">
  <p class="lead">Established districts <b>{f1(est['mean_LST'])} °C</b> (95% CI {f1(est['ci_low'])}–{f1(est['ci_high'])}) · new districts <b>{f1(new['mean_LST'])} °C</b> · desert {f1(des['mean_LST'])} °C · vegetation <b>{f1(veg['mean_LST'])} °C</b>. In desert cities, open sand is as hot as the city by day, so the decision-relevant comparison is <b>between the places where people live</b>, and greenery is the strongest local coolant.</p>
</section>""")

S(f"""<section>
  <div class="kicker">06 · Layer 3, hyperspectral materials (Tanager)</div><h2>What makes it hot? Narrow bands see the material</h2>
  <img class="wide" src="{img('03_hyperspectral_materials.png')}">
  <div class="stats">
   <div><b>+{f2(R['dR2_built'])}</b><span>R² gain for predicting LST in built-up areas<br>when Tanager is added ({f2(lm[('Bui','A')]['R2'])} → {f2(lm[('Bui','B')]['R2'])}, spatial CV)</span></div>
   <div><b>r = {f2(R['coreg_r_after'])}</b><span>Tanager vs Landsat albedo<br>after automatic co-registration</span></div>
   <div><b>{f0(R['tanager_beta_cloud_pct'])}% → {f1(R['tanager_physics_cloud_pct'])}%</b><span>Planet beta mask called bright sand "cloud".<br>We caught it with a physics test</span></div>
  </div>
</section>""")

S(f"""<section>
  <div class="kicker">07 · Layer 4, people exposure</div><h2>Who is outside in this heat?</h2>
  <img class="wide" src="{img('07_people_exposure.png')}">
  <div class="cols">
   <table class="t sm"><tr><th>mapped (OSM) per 10,000 residents</th><th>hottest 20%</th><th>rest of city</th><th></th></tr>
    {gap_row('bus_stop', '🚌 bus stops')}{gap_row('mosque', '🕌 mosques')}{gap_row('park', '🌳 parks / gardens')}{gap_row('vulnerable', '🏫 schools &amp; clinics')}
   </table>
   <div class="callout"><b>{f0(R['residents_hot20'])} residents</b> live in the hottest 20% of populated cells.<br>Counting <b>people instead of buildings</b> changes <b>{f0(R['top20_changed_by_people_layer_pct'])}%</b> of the top-20 priorities.</div>
  </div>
</section>""")

S(f"""<section>
  <div class="kicker">08 · Layer 5, decision product</div><h2>Where to act first, and with what</h2>
  <img class="wide" src="{img('06_heat_risk_priority.png')}">
  <table class="t sm"><tr><th>rank</th><th>location</th><th>LST</th><th>residents</th><th>recommended action</th></tr>{hot_rows}</table>
  <p class="note">Cool-roof what-if inside built-up areas: <b>+0.10 albedo ⇒ {cool[0]:+.2f} °C</b> (95% CI {cool[1]:+.2f} to {cool[2]:+.2f}), and +0.10 NDVI ⇒ {R['cooling_per_0p1_ndvi_C']:+.2f} °C, so budgets can be compared in °C.</p>
</section>""")

S(f"""<section>
  <div class="kicker">09 · Validation</div><h2>Every claim has a number and a method</h2>
  <table class="t">
   <tr><th>Claim</th><th>Metric</th><th>Validation</th><th>Result</th></tr>
   <tr><td>Built-up map beats the official rule</td><td>F1 / IoU</td><td>5-fold spatial-block CV (1 km) vs WorldCover</td><td><b>{f2(R['cv_built_f1_rf'])}</b> vs {f2(R['cv_built_f1_ndbi'])} · IoU {f2(R['cv_built_iou_rf'])}</td></tr>
   <tr><td>Generalises to another year &amp; reference</td><td>F1</td><td>IO LULC 2023, all pixels</td><td><b>{f2(R['indep2023_built_f1_rf'])}</b> vs {f2(R['indep2023_built_f1_ndbi'])}</td></tr>
   <tr><td>Detected change is real</td><td>precision / F1</td><td>new built 2017→23 vs IO LULC</td><td>precision {f2(chg['precision'])} · F1 {f2(chg['f1'])}</td></tr>
   <tr><td>Heat differs between zones</td><td>mean LST ± 95% CI</td><td>block bootstrap, 300×</td><td>{f1(est['mean_LST'])} vs veg {f1(veg['mean_LST'])} °C</td></tr>
   <tr><td>Tanager co-registered</td><td>Pearson r</td><td>albedo vs Landsat, ±4 px search</td><td><b>{f2(R['coreg_r_after'])}</b></td></tr>
   <tr><td><b>Hyperspectral adds value</b></td><td>ΔR², RMSE</td><td>spatial-block CV, ± Tanager</td><td>all <b>+{f2(R['dR2_all'])}</b> · built-up <b>+{f2(R['dR2_built'])}</b></td></tr>
   <tr><td>Cool roofs cool</td><td>°C per +0.10 albedo</td><td>OLS, block-bootstrap CI</td><td><b>{cool[0]:+.2f}</b> ({cool[1]:+.2f}…{cool[2]:+.2f})</td></tr>
   <tr><td>Priorities are robust</td><td>top-20 overlap</td><td>4 alternative weightings</td><td>{f0(min(ov.values())*100)}–{f0(max(ov.values())*100)}%</td></tr>
  </table>
  <p class="note">Honest edge: change detection is precise but conservative (recall {f2(chg['recall'])}). It only flags confident change, which is what a planner should act on.</p>
</section>""")

dash = f'<img class="wide" src="{img(shot)}">' if os.path.exists(shot) else ""
S(f"""<section>
  <div class="kicker">10 · Product &amp; delivery</div><h2>How planners use it</h2>
  <div class="cols">
   <div>{dash}</div>
   <div><ul class="big">
    <li><b>Heat-risk dashboard</b>: 300 m cells by priority, top-10 pinned, toggle layers for mosques, bus stops, rider hubs and construction. Hovering shows LST, residents and the action. To be hosted on <b>gIQ</b>.</li>
    <li><b>GeoJSON / REST API</b>: <code>GET /cells?city=riyadh&amp;min_hrpi=80</code>, straight into ArcGIS/QGIS and permitting.</li>
    <li><b>Annual heat brief + alerts</b>: after each summer, a one-page brief per municipality flags new districts entering the top decile, and projects that moved a cell out of it.</li>
   </ul></div>
  </div>
</section>""")

S(f"""<section>
  <div class="kicker">11 · Impact &amp; business</div><h2>Value for cities, people and budgets</h2>
  <div class="cols3">
   <div class="card"><h3>Impact</h3><ul><li>Protects people outdoors: worshippers, bus riders, riders, workers, children</li><li>Targets the shade and cooling budget where it lowers the most °C per dirham</li><li>SDG 3 · 11 · 13 · UAE Net Zero 2050 · Saudi Green Riyadh</li></ul></div>
   <div class="card"><h3>Who pays</h3><ul><li>Municipalities &amp; planning departments (annual city licence)</li><li>Real-estate developers (heat-aware master-plan check)</li><li>Delivery platforms &amp; contractors (rider and worker heat-safety planning)</li></ul></div>
   <div class="card"><h3>Why it scales</h3><ul><li>Open data only: any Arab city with Landsat + one hyperspectral scene</li><li>Runs in ~20 min per city per year</li><li>Satellite 813 adds regional hyperspectral revisit</li></ul></div>
  </div>
</section>""")

S(f"""<section>
  <div class="kicker">12 · Roadmap &amp; limits</div><h2>From PoC to MVP in incubation</h2>
  <div class="cols">
   <div><h3>Incubation plan</h3><ol class="big">
    <li>UAE cities (Abu Dhabi, Dubai, Al Ain) with <b>Satellite 813 / MBZ-SAT</b> data</li>
    <li>Worker-housing and delivery-hub layers from municipal and platform partners</li>
    <li>Calibrate LST with NCM / municipal weather stations. Field-check 200–300 material points</li>
    <li>Dashboard on <b>gIQ</b> with a what-if slider (roof albedo, trees, shaded stops)</li></ol></div>
   <div><h3>Known limits</h3><ul>
    <li>LST is a ~10:30 surface snapshot, not afternoon air temperature</li>
    <li>Reference maps, not field truth. Sandy low-density suburbs are hardest</li>
    <li>OSM under-maps labour housing and rider waiting spots</li>
    <li>Cooling what-if is a statistical slope with a CI, not a simulation</li>
    <li>One Tanager date (May). Materials are stable, shade is not</li></ul></div>
  </div>
</section>""")

S(f"""<section class="title">
  <h1>QAYDH <span class="ar">القيظ</span></h1>
  <h2>Know where it burns, why, and who is outside.</h2>
  <p class="lead">{f0(R['residents_hot20'])} residents in the hottest 20% of east Riyadh · +{f2(R['dR2_built'])} R² from hyperspectral · {cool[0]:+.2f} °C per +0.10 roof albedo</p>
  <div class="meta">Code, notebook and outputs: GitHub repository (README) · Data © Planet Labs PBC (CC-BY-4.0), USGS, ESA, Impact Observatory, WorldPop, OpenStreetMap contributors</div>
</section>""")

CSS = """
@page { size: 1600px 900px; margin: 0 }
* { box-sizing: border-box }
body { margin: 0; font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; color: #1d2b24; }
section { width: 1600px; height: 900px; padding: 56px 72px; page-break-after: always; position: relative; overflow: hidden;
          background: #fbf8f2; }
section::after { content: "QAYDH · T0049 · Challenge 813"; position: absolute; bottom: 10px; right: 72px; font-size: 14px; color: #a08c6c }
section.title { background: linear-gradient(135deg, #3b1d0e 0%, #8a2c0d 55%, #d9531e 100%); color: #fff7ec; padding-top: 200px }
section.title h1 { font-size: 110px; margin: 10px 0 } section.title h2 { font-size: 44px; font-weight: 500; color: #ffd9a8; margin: 0 0 30px }
section.title .lead { font-size: 26px; max-width: 1250px } .meta { font-size: 18px; color: #ffcf9a; margin-top: 14px }
.ar { font-family: 'Geeza Pro', 'Arial', sans-serif; color: #ffb366 }
.kicker { font-size: 18px; letter-spacing: .08em; text-transform: uppercase; color: #c2410c; font-weight: 700 }
section.title .kicker { color: #ffcf9a }
h2 { font-size: 42px; margin: 8px 0 22px; color: #3b1d0e } h3 { color: #8a2c0d; margin: 0 0 10px; font-size: 24px }
.lead { font-size: 25px; line-height: 1.45 } .note { font-size: 18px; color: #5b4a3a; line-height: 1.4 }
ul.big li, ol.big li { font-size: 23px; margin-bottom: 14px; line-height: 1.4 } ul li { font-size: 19px; margin-bottom: 8px; line-height: 1.35 }
.cols { display: grid; grid-template-columns: 1.15fr 1fr; gap: 36px; align-items: start }
.cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 26px }
.card { background: #fff; border: 1px solid #ecdcc4; border-radius: 14px; padding: 28px; min-height: 560px } .card li { font-size: 23px; margin-bottom: 18px }
.people { display: grid; grid-template-columns: 1fr 1fr; gap: 16px }
.p { background: #fff; border: 1px solid #ecdcc4; border-radius: 14px; padding: 20px; font-size: 19px; line-height: 1.35 }
.p span { font-size: 44px; display: block; margin-bottom: 6px }
.who { position: absolute; bottom: 60px; left: 72px; right: 72px; background: #3b1d0e; color: #ffe7c7; padding: 18px 24px; border-radius: 12px; font-size: 20px }
.flow { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin: 20px 0 30px }
.box { background: #fff; border: 2px solid #e7c9a0; border-radius: 14px; padding: 26px 18px; font-size: 21px; line-height: 1.45; min-height: 260px }
.box b { font-size: 24px; color: #8a2c0d } .box.hs { border-color: #7b3294 } .box.hs b { color: #7b3294 }
.box.pe { border-color: #0e7490 } .box.pe b { color: #0e7490 } .box.out { background: #8a2c0d; color: #fff; border-color: #8a2c0d } .box.out b { color: #ffd9a8 }
img.wide { width: 100%; max-height: 440px; object-fit: contain; display: block; margin: 0 auto 14px; background: #fff; border-radius: 10px }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px }
.stats div { background: #fff; border-left: 6px solid #d9531e; border-radius: 10px; padding: 14px 18px }
.stats b { font-size: 40px; color: #8a2c0d; display: block } .stats span { font-size: 17px; color: #5b4a3a }
table.t { width: 100%; border-collapse: collapse; font-size: 21px; background: #fff }
table.t th { text-align: left; background: #3b1d0e; color: #ffe7c7; padding: 10px 12px }
table.t td { padding: 12px 12px; border-bottom: 1px solid #ecdcc4 } table.t.sm { font-size: 16px } table.t.sm td { padding: 6px 10px }
.callout { background: #8a2c0d; color: #fff; border-radius: 14px; padding: 24px; font-size: 23px; line-height: 1.5 }
code { background: #f1e6d4; padding: 1px 6px; border-radius: 4px; font-size: .9em }
"""
doc = f"<!doctype html><html><head><meta charset='utf-8'><title>QAYDH pitch</title><style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
hp = os.path.join(PITCH, "QAYDH_T0049_pitch.html"); open(hp, "w").write(doc)
pdf = os.path.join(PITCH, "QAYDH_T0049_pitch.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + hp],
               capture_output=True, timeout=180)
print("deck:", hp, "\npdf :", pdf if os.path.exists(pdf) else "NOT CREATED")
