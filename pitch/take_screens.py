"""Fresh dashboard screenshots for the deck (after the block-LST change).
usage: CHROME=/path/to/chrome python pitch/take_screens.py  -> pitch/screens/m2_who.png, m5_act.png, m6_blocks.png
"""
import os, subprocess, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "pitch", "screens"); CHROME = os.environ.get("CHROME", "chromium")
DASH = open(os.path.join(ROOT, "dashboard", "index.html")).read().replace("</style>", "#intro{display:none!important}</style>", 1)
assert "build();\n</script>" in DASH
def shot(name, js, w=1600, h=950):
    p = os.path.join(SHOTS, name + ".png"); tmp = os.path.join(SHOTS, "_tmp.html")
    open(tmp, "w").write(DASH.replace("build();\n</script>", f"build();setTimeout(()=>{{{js}}},600);\n</script>"))
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    "--virtual-time-budget=12000", f"--screenshot={p}", "file://" + tmp], capture_output=True, timeout=180)
    os.remove(tmp); print("wrote", p)
mus = "document.getElementById('city-musaffah').click();"
shot("m2_who", mus + "setTimeout(()=>{goChapter(1);showSite(0)},400)")
shot("m5_act", mus + "setTimeout(()=>showHot(0),400)")
# blocks coloured by LST, buildings as outlines, one building clicked -> "Surrounding block LST" card
shot("m6_blocks", mus + """setTimeout(()=>{setLayers(null);toggle('blocks',true);if(layer.objects)toggle('objects',true);
  const h=DATA.musaffah.hot[0];map.setView([h.lat,h.lon],17);
  let best=null;layer.objects.eachLayer(l=>{if(!best)best=l});if(best){map.setView(best.getBounds().getCenter(),17);showBuilding(best.feature.properties);}},400)""")
