"""3-minute narrated walkthrough of the dashboard -> pitch/demo/qaydh_demo.mp4
Voice: ffmpeg's built-in flite text-to-speech. Screen: Playwright recording of dashboard/index.html.
usage: python pitch/make_demo.py   (needs playwright + ffmpeg with flite)"""
import os, subprocess, json, wave, shutil
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "pitch", "demo"); os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(OUT, "_tmp"); os.makedirs(TMP, exist_ok=True)
STEPS = [
 ("This is QAYDH, a heat risk atlas for Gulf cities, built from open satellite data. We open the Musaffah deep dive in Abu Dhabi.",
  "document.getElementById('city-musaffah').click()"),
 ("Step one: where. Landsat thermal images from ten summer scenes show heat zones. Orange is elevated, red is high, and dark red is extreme, the hottest five percent.",
  "goChapter(0)"),
 ("Step two: who. These icons are named bus stops, mosques, schools and clinics. Clicking a bus stop opens its card: the heat around it, the greenery, and the recommended fix, a shaded and ventilated shelter.",
  "goChapter(1); setTimeout(()=>showSite(0), 1500)"),
 ("Step three: what. Sentinel two shows what the ground is made of at ten metres. Grey is road, violet is roof, beige is sand, green is plants and blue is water.",
  "goChapter(2)"),
 ("Step four: labels. Every building is an object with an I D, a roof material, a heat zone and a street. Orange outlines are cool roof candidates.",
  "goChapter(3)"),
 ("Step five: why. Each one hundred metre block is coloured by its summer surface temperature. Asphalt and bare sand push heat up. Greenery pulls it down.",
  "goChapter(4)"),
 ("Step six: act. Hotspot M zero zero one is the first place to act. Its card shows who is outside, what the ground is made of, and the plan: shade, water and trees first. Cool pavement is minor here.",
  "showHot(0)"),
 ("The same pipeline runs on other cities. This is east Riyadh, where Planet Tanager hyperspectral data reads roof, road and sand.",
  "document.getElementById('city-riyadh').click()"),
 ("And this is the Abu Dhabi mainland, comparing districts such as Musaffah and Masdar City.",
  "document.getElementById('city-abudhabi').click()"),
 ("Everything is open data and open code, and the notebook reproduces every number. Thank you from team T zero zero four nine.",
  "document.getElementById('city-musaffah').click()"),
]
def tts(text, path):
    t = text.replace("'", "").replace(":", " ").replace(",", " ,")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"flite=text='{t}':voice=slt", "-ar", "44100", path], check=True)
    with wave.open(path) as w: return w.getnframes() / w.getframerate()
durs = [tts(t, os.path.join(TMP, f"v{i}.wav")) + 3.5 for i, (t, _) in enumerate(STEPS)]
# audio track with 3.5 s pause after each line
lst = os.path.join(TMP, "list.txt"); sil = os.path.join(TMP, "sil.wav")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "3.5", sil], check=True)
open(lst, "w").write("".join(f"file 'v{i}.wav'\nfile 'sil.wav'\n" for i in range(len(STEPS))))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, os.path.join(TMP, "voice.wav")], check=True)

html = open(os.path.join(ROOT, "dashboard", "index.html")).read().replace("</style>", "#intro{display:none!important}</style>", 1)
page_path = os.path.join(ROOT, "dashboard", "_demo.html"); open(page_path, "w").write(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 900}, record_video_dir=TMP, record_video_size={"width": 1600, "height": 900})
    pg = ctx.new_page(); pg.goto("file://" + page_path); pg.wait_for_timeout(2500)
    lead = 2.5
    for (text, js), d in zip(STEPS, durs):
        pg.evaluate(js); pg.wait_for_timeout(int(d * 1000))
    vid = pg.video.path(); ctx.close(); b.close()
os.remove(page_path)
out = os.path.join(OUT, "qaydh_demo.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.5", "-i", vid, "-i", os.path.join(TMP, "voice.wav"),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-vf", "scale=1280:-2",
                "-c:a", "aac", "-b:a", "96k", "-shortest", out], check=True)
shutil.rmtree(TMP)
print(out, f"{os.path.getsize(out)/1e6:.1f} MB", f"{sum(durs):.0f} s")
