"""Record animated GIF walkthroughs of the QAYDH dashboard (headless Chrome frames → GIF).
usage: python pitch/make_gifs.py     → pitch/gifs/*.gif (used in README and the presentation)
"""
import os, subprocess
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTD = os.path.join(ROOT, "pitch", "gifs"); TMP = os.path.join(OUTD, "_frames"); os.makedirs(TMP, exist_ok=True)
DASH = open(os.path.join(ROOT, "dashboard", "index.html")).read().replace("</style>", "#intro{display:none!important}</style>", 1)

def frame(name, js, w=1280, h=760, wait=9000):
    html = os.path.join(TMP, name + ".html"); png = os.path.join(TMP, name + ".png")
    open(html, "w").write(DASH.replace("build();\n</script>", f"build();setTimeout(()=>{{{js}}},600);\n</script>"))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", f"--virtual-time-budget={wait}",
                    f"--screenshot={png}", "file://" + html], capture_output=True, timeout=180)
    return png

def gif(name, steps, ms=1800):
    frames = [Image.open(frame(f"{name}_{i}", js)).convert("RGB") for i, js in enumerate(steps)]
    frames = [f.resize((1100, int(f.height * 1100 / f.width)), Image.LANCZOS).quantize(colors=200, method=Image.Quantize.MEDIANCUT) for f in frames]
    p = os.path.join(OUTD, name + ".gif"); frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
    print(p, f"{os.path.getsize(p)/1e6:.1f} MB"); return p

mus = "document.getElementById('city-musaffah').click();"
gif("qaydh_musaffah_tour", [mus + f"setTimeout(()=>goChapter({i}),300)" for i in range(6)] + [mus + "setTimeout(()=>showHot(0),300)", mus + "setTimeout(()=>{goChapter(1);showSite(0)},300)"])
gif("qaydh_three_cities", ["goChapter(1)", "goChapter(3)", "showHot(0)",
                           "document.getElementById('city-abudhabi').click();setTimeout(()=>goChapter(1),300)",
                           "document.getElementById('city-abudhabi').click();setTimeout(()=>goChapter(2),300)"])
for f in os.listdir(TMP): os.remove(os.path.join(TMP, f))
os.rmdir(TMP)
