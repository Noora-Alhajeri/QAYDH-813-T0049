"""Build the QAYDH story dashboard (one self-contained HTML file) from qaydh_outputs/.
usage: python dashboard/build_dashboard.py      (after running the notebook)
"""
import os, json, base64, urllib.request
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qaydh_outputs"); D = os.path.join(OUT, "dashboard")
R = json.load(open(os.path.join(OUT, "results.json")))

def b64(p, jpeg=False):
    if jpeg:   # photographic layers as JPEG to keep the single-file dashboard small
        from PIL import Image; import io
        b = io.BytesIO(); Image.open(p).convert("RGB").save(b, "JPEG", quality=85); return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
NEWPAL = {"#3a3a3a": "#50535f", "#e4572e": "#9b7bff", "#e9d8a6": "#e8dcb0", "#2e9e44": "#22b573", "#2b83ba": "#3ba3f0"}
def recolor(path, old):
    """Swap the class colours of a rendered class map for a clearly distinct, colour-blind-safer palette."""
    from PIL import Image; import numpy as np, io
    im = np.array(Image.open(path).convert("RGBA")).astype(int); rgb = im[..., :3]
    o = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in old]); n = np.array([[int(NEWPAL.get(c, c)[i:i + 2], 16) for i in (1, 3, 5)] for c in old])
    d = ((rgb[..., None, :] - o[None, None]) ** 2).sum(-1); k = d.argmin(-1); hit = (d.min(-1) < 900) & (im[..., 3] > 0)
    rgb[hit] = n[k[hit]]; im[..., :3] = rgb
    b = io.BytesIO(); Image.fromarray(im.astype("uint8")).save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def overlays(tag):
    m = json.load(open(os.path.join(D, f"{tag}_overlays.json")))
    L_ = {}
    for k, v in m["layers"].items():
        p_ = os.path.join(D, f"{tag}_{k}.png")
        if k in ("surfaces", "annotation") and v.get("colors"):
            L_[k] = dict(v, img=recolor(p_, v["colors"])); L_[k]["colors"] = [NEWPAL.get(c, c) for c in v["colors"]]
        else: L_[k] = dict(img=b64(p_, jpeg=(k == "satellite")), **v)
    return dict(bounds=m["bounds"], layers=L_)
def cells(path, keep):
    g = json.load(open(path))
    for f in g["features"]:
        f["properties"] = {k: f["properties"].get(k) for k in keep}
        f["geometry"]["coordinates"] = [[[round(x, 5), round(y, 5)] for x, y in ring] for ring in f["geometry"]["coordinates"]]
    return g
def places(path): return pd.read_csv(path).fillna("").to_dict("records")
def hot(path, n=10):
    df = pd.read_csv(path).head(n)
    return json.loads(df.to_json(orient="records"))

KEEP = ["HRPI", "LST_C", "people", "green", "roof", "road", "action"]
mc = {d["approach"]: d for d in R["material_classifier"]["scores"]}
z = {d["zone"]: d for d in R["lst_by_zone"]}
ad = R["abudhabi"]; dist = {d["district"]: d for d in ad["districts"]}
DATA = dict(
    riyadh=dict(name="East Riyadh", sub="As Sali · Saudi Arabia", center=[24.576, 46.856], ov=overlays("riyadh"),
                cells=cells(os.path.join(OUT, "qaydh_heat_risk_cells.geojson"), KEEP), places=places(os.path.join(OUT, "riyadh_outdoor_places.csv")),
                hot=hot(os.path.join(OUT, "top_hotspots.csv")), weather=json.load(open(os.path.join(D, "riyadh_weather.json")))),
    abudhabi=dict(name="Abu Dhabi", sub="Musaffah · Masdar · MBZ City · Khalifa City", center=[24.385, 54.55], ov=overlays("abudhabi"),
                  cells=cells(os.path.join(OUT, "abudhabi_heat_risk_cells.geojson"), ["HRPI", "LST_C", "people", "green", "action"]),
                  places=places(os.path.join(OUT, "abudhabi_outdoor_places.csv")), hot=hot(os.path.join(OUT, "abudhabi_top_hotspots.csv")),
                  districts=json.load(open(os.path.join(D, "abudhabi_districts.json")))["districts"], dist=dist))
f2 = lambda x: f"{x:.2f}"; f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:,.0f}"
w = R["weather"]; g = R["amenities_per_10k_hot_vs_rest"]; cool = R["cooling_per_0p1_albedo_C"]
kh = [k for k in mc if k.startswith("Full")][0]; k6 = [k for k in mc if k.startswith("6")][0]; ki = [k for k in mc if k.startswith("Index")][0]
est = next(v for k, v in z.items() if k.startswith("Est"))
CH = dict(
    riyadh=[
        dict(id="grew", layer="growth", kicker="Where", title="The city grew 28% in eleven years",
             body=f"Built-up land rose from {f0(R['built_km2_before'])} to {f0(R['built_km2_after'])} km² (2014→2025). Magenta = {f0(R['new_urban_km2'])} km² of confidently new districts.",
             stat=[(f2(R['cv_built_f1_rf']), "built-up F1"), (f2(R['cv_built_f1_ndbi']), "starter NDBI rule")]),
        dict(id="burn", layer="heat", kicker="Where", title="Where it burns at 10:40 am",
             body=f"Median summer surface temperature. Established districts average {f1(est['mean_LST'])} °C. The same cells stay hottest year after year (2024↔2025 r = {f2(R['lst_cells_r_2024_vs_2025'])}).",
             stat=[(f"{R['persistent_hot_cells']}", "cells hot 3 summers"), (f2(R['ndbi_lst_r_builtup']), "starter NDBI ↔ heat r")]),
        dict(id="when", layer="heat", kicker="When", title=f"Danger runs {w['danger_window_local']}",
             body=f"Air passes 40 °C on most summer days from {w['danger_window_local'].split('–')[0]}. That covers Dhuhr and Asr prayers, school runs and lunch-rush deliveries. Peak at {w['typical_peak_hour']}:00.",
             stat=[(f1(w['heat_hours_ge40_per_day']), "hours/day ≥ 40 °C"), (f"{w['days_air_ge_45']}", "days ≥ 45 °C")], ribbon=True),
        dict(id="why", layer="surfaces", kicker="Why", title="Roof, road or sand? Tanager reads the surface",
             body=f"426-band Tanager spectra, labelled automatically from OpenStreetMap + Microsoft building outlines and WorldCover, sort every pixel into road, roof, vegetation and sand. Tested on tiles the model never saw.",
             stat=[(f2(mc[kh]['macro_F1']), "full spectrum F1"), (f2(mc[k6]['macro_F1']), "6 broad bands"), (f2(mc[ki]['macro_F1']), "starter index rules")]),
        dict(id="who", layer="places", kicker="Who", title="Who is outside in it",
             body=f"Mosques, bus stops, delivery-rider hubs, construction sites, schools and clinics on WorldPop residents. The hottest fifth of neighbourhoods has {f2(g['bus_stop']['hottest_20pct'])} mapped bus stops per 10,000 people, against {f2(g['bus_stop']['rest_of_city'])} elsewhere.",
             stat=[(f0(R['residents_hot20']), "residents in hottest 20%"), (f"{R['top20_changed_by_people_layer_pct']:.0f}%", "priorities changed by counting people")]),
        dict(id="act", layer="priority", kicker="What next", title="Where to act first",
             body=f"300 m cells ranked by heat × people × missing greenery. Pick a hotspot to see who is exposed, why it is hot, what to do and the estimated cooling.",
             stat=[(f"{cool[0]:+.2f} °C", "per +0.10 roof albedo"), (f"+{f2(R['dR2_built'])}", "R² gained from hyperspectral")], list=True),
    ],
    abudhabi=[
        dict(id="grew", layer="growth", kicker="Where", title=f"Abu Dhabi mainland grew {f0(ad['built_km2_before'])} → {f0(ad['built_km2_after'])} km²",
             body="The same open-data pipeline, moved to the UAE by changing the area of interest. Magenta = new urban land since 2014.",
             stat=[(f2(ad['cv_built_f1_rf']), "built-up F1"), (f2(ad['cv_built_f1_ndbi']), "starter NDBI rule")]),
        dict(id="burn", layer="heat", kicker="Where", title="Masdar reads hottest, and the reason is sand",
             body=f"Masdar City averages {f1(dist['Masdar City']['mean_LST_C'])} °C, but only {dist['Masdar City']['builtup_QAYDH_RF_pct']:.0f}% of it is built. The rest is open sand and {dist['Masdar City']['construction_sites']} construction sites. Musaffah: {f1(dist['Musaffah industrial']['mean_LST_C'])} °C.",
             stat=[(f1(dist['Masdar City']['mean_LST_C']) + " °C", "Masdar City"), (f1(dist['Musaffah industrial']['mean_LST_C']) + " °C", "Musaffah")], districts=True),
        dict(id="rule", layer="satellite", kicker="Why", title="The starter rule calls sand a city",
             body=f"NDBI > 0 labels Musaffah {dist['Musaffah industrial']['builtup_starter_NDBI_pct']:.0f}% and Masdar {dist['Masdar City']['builtup_starter_NDBI_pct']:.0f}% built-up. WorldCover says {dist['Musaffah industrial']['builtup_WorldCover_pct']:.0f}% and {dist['Masdar City']['builtup_WorldCover_pct']:.0f}%. QAYDH's model: {dist['Musaffah industrial']['builtup_QAYDH_RF_pct']:.0f}% and {dist['Masdar City']['builtup_QAYDH_RF_pct']:.0f}%.",
             stat=[(f"{dist['Masdar City']['builtup_starter_NDBI_pct']:.0f}%", "NDBI says built (Masdar)"), (f"{dist['Masdar City']['builtup_WorldCover_pct']:.0f}%", "WorldCover")], districts=True),
        dict(id="who", layer="places", kicker="Who", title="Musaffah: workers, riders, worshippers",
             body=f"Musaffah holds {f0(dist['Musaffah industrial']['residents'])} residents, {dist['Musaffah industrial']['bus_stops']} bus stops and {dist['Musaffah industrial']['mosques']} mosques in one hot industrial grid, the highest people-priority of the four districts.",
             stat=[(f1(dist['Musaffah industrial']['mean_priority']), "Musaffah priority"), (f1(dist['Masdar City']['mean_priority']), "Masdar priority")], districts=True),
        dict(id="act", layer="priority", kicker="What next", title="Where to act first in Abu Dhabi",
             body="Ranked 300 m cells with the action each one needs. Hyperspectral roof/road detail plugs in when Satellite 813 or MBZ-SAT data is available.",
             stat=[(f0(ad['population']), "residents covered"), (f"{ad['n_osm_places']}", "mapped outdoor places")], list=True),
    ])

# ---- Musaffah deep dive (10 m block) ----
if os.path.exists(os.path.join(D, "musaffah_overlays.json")):
    mh = pd.read_csv(os.path.join(OUT, "musaffah_hotspots.csv")).head(10); ms_ = pd.read_csv(os.path.join(OUT, "musaffah_exposure_sites.csv"))
    mcells = json.load(open(os.path.join(OUT, "musaffah_cells_100m.geojson")))
    for k_, f_ in enumerate(mcells["features"]): f_["properties"]["block"] = f"C-{k_+1:04d}"     # 100 m thermal block id
    for f_ in mcells["features"]: f_["geometry"]["coordinates"] = [[[round(x, 5), round(y, 5)] for x, y in ring] for ring in f_["geometry"]["coordinates"]]
    mc_ = {d["approach"]: d for d in R["musaffah_classifier"]["scores"]}; wm = {d["model"]: d for d in R["musaffah_why_model"]["scores"]}
    th = R["musaffah_hazard_thresholds_C"]; top = R["musaffah_top_hotspot"]; sites = R["musaffah_sites"]
    DATA["musaffah"] = dict(name="Musaffah deep dive", sub="Abu Dhabi · 9 × 9 km at 10 m", center=[24.355, 54.50], ov=overlays("musaffah"), block=True,
                            cells=mcells, places=places(os.path.join(OUT, "musaffah_outdoor_places.csv")), hot=json.loads(mh.to_json(orient="records")),
                            sites=json.loads(ms_.to_json(orient="records")),
                            icons={k: open(os.path.join(ROOT, "pitch", "icons", f + ".svg")).read().replace('width="24"', 'width="15"').replace('height="24"', 'height="15"').replace('stroke="currentColor"', 'stroke="#14110e"').replace('stroke-width="2"', 'stroke-width="2.4"')
                                   for k, f in {"Bus stop": "bus", "Mosque": "building-mosque", "School": "school", "Kindergarten": "baby-carriage", "Clinic": "first-aid-kit", "Hospital": "building-hospital"}.items()})
    if os.path.exists(os.path.join(D, "musaffah_ann_overlays.json")):
        a_ = overlays("musaffah_ann"); DATA["musaffah"]["ov"]["layers"]["annotation"] = a_["layers"]["annotation"]
        def gj(p, nd=6):
            g = json.load(open(p))
            def rnd(c): return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], nd), round(c[1], nd)]
            for f_ in g["features"]: f_["geometry"]["coordinates"] = rnd(f_["geometry"]["coordinates"])
            return g
        DATA["musaffah"]["objects"] = gj(os.path.join(D, "musaffah_objects_near_hotspots.geojson"))
        rmp = os.path.join(OUT, "musaffah_roof_materials.csv")          # 10g roof materials, joined by building id
        if os.path.exists(rmp):
            rm = dict(pd.read_csv(rmp).values)
            for f_ in DATA["musaffah"]["objects"]["features"]: f_["properties"]["roof_material"] = rm.get(f_["properties"].get("id"), "")
        # Each building inherits the value of the 100 m thermal block it sits in (Dr D. Francis, KU review):
        # one block -> one number for every building in it, block id shown, never a per-building temperature.
        from shapely.geometry import shape as _shape
        from shapely.strtree import STRtree
        _polys = [_shape(f_["geometry"]) for f_ in mcells["features"]]; _tree = STRtree(_polys)
        _count = {}
        for f_ in DATA["musaffah"]["objects"]["features"]:
            c_ = _shape(f_["geometry"]).centroid; hit = [j for j in _tree.query(c_) if _polys[j].contains(c_)]
            pr_ = f_["properties"]; pr_.pop("LST_C", None)
            if hit:
                cp = mcells["features"][hit[0]]["properties"]; pr_["block"] = cp["block"]; pr_["block_LST_C"] = cp["LST_C"]; pr_["block_heat_pct"] = cp["heat_pct"]
                _count[cp["block"]] = _count.get(cp["block"], 0) + 1
        for f_ in DATA["musaffah"]["objects"]["features"]: f_["properties"]["block_n"] = _count.get(f_["properties"].get("block"), 0)
        _lsm = [d for d in json.load(open(os.path.join(OUT, "data_provenance.json"))) if "Landsat" in d["source"] and "Musaffah" in d["source"]]
        DATA["musaffah"]["acq"] = (f"Landsat 8/9 TIRS · median of {len(_lsm[0]['dates'])} clear scenes {_lsm[0]['dates'][0]} → {_lsm[0]['dates'][-1]} · ~10:40 local · native ≈100 m"
                                   if _lsm else "Landsat 8/9 TIRS, summer 2025, ~10:40 local, native ≈100 m")
        ifp = os.path.join(OUT, "musaffah_informal_candidates.geojson")   # 10h informal-housing candidates
        if os.path.exists(ifp): DATA["musaffah"]["informal"] = gj(ifp)
        DATA["musaffah"]["segments"] = gj(os.path.join(OUT, "musaffah_sam_segments.geojson"))
        DATA["musaffah"]["review"] = gj(os.path.join(OUT, "musaffah_annotation_review_queue.geojson"))
        br = pd.read_csv(os.path.join(OUT, "musaffah_planner_briefs.csv")); DATA["musaffah"]["briefs"] = {r.hotspot: dict(text=r.brief, check=r.fact_check, signoff=r.human_signoff) for r in br.itertuples()}
    rules_ = [k for k in mc_ if k.startswith("Index")][0]; bestk = R["musaffah_classifier"]["chosen"]
    s0 = ms_.iloc[0]; h0_ = mh.iloc[0]
    CH["musaffah"] = [
        dict(id="where", layer="blocks", hint="Red = extreme heat zone. Press Next to see who is there.", kicker="Where is heat high?", title=f"Hazard zones, not fake street temperatures",
             body=f"Landsat thermal (≈100 m) shows zones: elevated ≥ {th['P75']:.1f} °C, high ≥ {th['P90']:.1f} °C, extreme ≥ {th['P95']:.1f} °C. It never pretends to know one bus stop's exact temperature.",
             stat=[(f"{th['P95']:.1f} °C", "extreme threshold (P95)"), (f"{th['median']:.1f} °C", "block median")]),
        dict(id="who", layer="sites", view=[float(s0.lat), float(s0.lon), 15], hint="Click a lettered icon: B bus stop, M mosque, S school/clinic.", kicker="Who may be exposed?", title="Bus stops, mosques, clinics, labour camps",
             body=f"{sites['n']} named outdoor sites from OpenStreetMap, each scored within 150 m: heat percentile, vegetation, impervious cover, distance to green.",
             stat=[(f"{sites['very_high']}", "very-high sites"), (f"{sites['high']}", "high sites")]),
        dict(id="what", layer="surfaces", view=[float(h0_.lat), float(h0_.lon), 15], hint="Grey road, violet roof, beige sand, green plants, blue water.", kicker="What is physically there?", title="Road, roof, sand, plants, water at 10 m",
             body=f"Rule-based reference labels from OpenStreetMap, Microsoft footprints and WorldCover, kept only at ≥80% purity, mixed pixels excluded, noisy labels removed, scored on held-out 1 km blocks.",
             stat=[(f"{mc_[bestk]['test_macro_F1']:.2f}", "macro-F1, held-out blocks"), (f"{mc_[rules_]['test_macro_F1']:.2f}", "starter index rules")], conf=True),
        dict(id="labels", layer="annotation", view=[float(h0_.lat), float(h0_.lon), 16], hint="Hover a building outline to see its ID and labels. Orange outline = cool-roof candidate.", kicker="How we labelled it", title="Annotation, objects and AI segments",
             body=f"Reference labels at ≥80% purity (A–C train · D validate · E test), {R['musaffah_objects']['buildings']:,} building objects with ID and bounding box, SAM segments around hotspots, and a 300-point review queue for people to check.",
             stat=[(f"{R['musaffah_objects']['buildings']:,}", "labelled building objects"), (f"{R['sam']['annotation_candidates']}", "SAM annotation candidates")]),
        dict(id="why", layer="blocks", hint="Drivers are shown in each hotspot card in the last step.", kicker="Why may it be hot?", title="Asphalt and sand up, green down",
             body=f"A spatially cross-validated model links each 100 m cell's surface mix to its heat. Drivers are shown as associations, not proof of cause.",
             stat=[(f"{wm['Random Forest']['R2']:.2f}", "R², spatial CV"), (f"{wm['Random Forest']['MAE_C']:.1f} °C", "mean error")]),
        dict(id="act", layer="priority", hint="Pick a hotspot from the list to see its card.", kicker="What should be done?", title="Where to act first in Musaffah",
             body="M-001 = Musaffah hotspot #1, ranked by heat × people × missing shade. Ranked 100 m cells with the action, the reason in plain words, and the relative potential of trees, cool pavement and shaded stops.",
             stat=[(top["id"], "top hotspot"), (top["priority"], "priority")], list=True)]

VEND = os.path.join(ROOT, "dashboard", "vendor")   # Leaflet 1.9.4 (BSD-2) vendored: the dashboard works offline and behind strict networks
leaflet_css = open(os.path.join(VEND, "leaflet.css")).read(); leaflet_js = open(os.path.join(VEND, "leaflet.js")).read()
tpl = open(os.path.join(ROOT, "dashboard", "template.html")).read()
html = (tpl.replace("/*LEAFLET_CSS*/", leaflet_css).replace("/*LEAFLET_JS*/", leaflet_js)
           .replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
           .replace("__CHAPTERS__", json.dumps(CH, separators=(",", ":"), ensure_ascii=False)))
open(os.path.join(ROOT, "dashboard", "qaydh_heat_atlas.html"), "w").write(html)        # body-only version (for hosted artifact)
out = os.path.join(ROOT, "dashboard", "index.html")
open(out, "w").write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + html + "</html>")
print("dashboard:", out, f"{os.path.getsize(out)/1e6:.1f} MB")
