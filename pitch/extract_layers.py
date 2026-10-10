"""Split each slide of pitch/QAYDH_T0049_pitch.html into editable layers for PowerPoint:
background (shapes only), pictures (each <img>), and text boxes (every text block with its runs and style).
usage (needs: pip install playwright): python pitch/extract_layers.py  ->  pitch/_layers/{slides.json, bg_N.png, img_N_K.png}
then:  node pitch/make_pptx.js        ->  pitch/QAYDH_T0049_pitch_editable.pptx
"""
import json, os, base64, re
from playwright.sync_api import sync_playwright

P = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(P, "_layers"); os.makedirs(OUT, exist_ok=True)
JS = r"""
() => {
 const INL = new Set(['SPAN','B','I','EM','STRONG','BR','A','SMALL','SUB','SUP','KBD','CODE']);
 const out = [];
 document.querySelectorAll('section').forEach((sec, si) => {
  const sr = sec.getBoundingClientRect(); const texts = [], imgs = [];
  sec.querySelectorAll('img').forEach((im, k) => { const r = im.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return;
     const cs = getComputedStyle(im); if (im.src.startsWith('data:image/svg')||cs.filter!=='none'||cs.mixBlendMode!=='normal'||+cs.opacity<1) return; imgs.push({src: im.src, k, x: r.left - sr.left, y: r.top - sr.top, w: r.width, h: r.height, fit: cs.objectFit, pos: cs.objectPosition, op: +cs.opacity, filt: cs.filter, blend: cs.mixBlendMode, radius: parseFloat(cs.borderTopLeftRadius) || 0}); im.dataset.k = k; });
  const disp = el => getComputedStyle(el).display;
  const inl = el => el.tagName === 'BR' || (disp(el).startsWith('inline') && !['inline-block','inline-flex','inline-grid'].includes(disp(el)));
  const isSvg = el => el.tagName.toLowerCase() === 'svg' || el.tagName === 'IMG';
  const textBlock = el => el.innerText && el.innerText.trim() && [...el.children].every(c => inl(c) || isSvg(c)) && !isSvg(el);
  const all = [...sec.querySelectorAll('*')].filter(el => !el.closest('svg') && textBlock(el) &&
        (!inl(el) || !el.parentElement || !textBlock(el.parentElement)));
  all.forEach(el => {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {acceptNode: n => (n.parentElement.closest('svg') || !n.textContent.trim()) ? 2 : 1});
    const tn = []; while (tw.nextNode()) tn.push(tw.currentNode); if (!tn.length) return;
    const rg = document.createRange(); rg.setStartBefore(tn[0]); rg.setEndAfter(tn[tn.length - 1]);
    const r = rg.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return;
    const cs = getComputedStyle(el); const runs = [];
    const walk = (node, st) => { node.childNodes.forEach(n => {
       if (n.nodeType === 3) { const t = n.textContent.replace(/\s+/g, ' '); if (t) runs.push({t, ...st}); }
       else if (n.tagName === 'BR') runs.push({br: 1});
       else if (n.nodeType === 1 && n.tagName !== 'svg') { const c = getComputedStyle(n); walk(n, {color: c.color, bold: +c.fontWeight >= 600, italic: c.fontStyle === 'italic', size: parseFloat(c.fontSize), font: c.fontFamily}); } }); };
    walk(el, {color: cs.color, bold: +cs.fontWeight >= 600, italic: cs.fontStyle === 'italic', size: parseFloat(cs.fontSize), font: cs.fontFamily});
    texts.push({x: r.left - sr.left, y: r.top - sr.top, w: r.width, h: r.height, align: cs.textAlign, upper: cs.textTransform === 'uppercase', lh: cs.lineHeight, ls: cs.letterSpacing, dir: cs.direction, runs});
    el.dataset.txt = 1;
  });
  out.push({texts, imgs});
 });
 return out;
}"""
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1600, "height": 900})
    pg.goto("file://" + os.path.join(P, "QAYDH_T0049_pitch.html")); pg.wait_for_timeout(3000)
    data = pg.evaluate(JS)
    pg.add_style_tag(content="section{page-break-after:auto}")
    secs = pg.query_selector_all("section")
    from PIL import Image
    import io
    for si in range(len(secs)):
        for k, im in enumerate(data[si]["imgs"]):
            raw = base64.b64decode(im["src"].split(",", 1)[1]) if im["src"].startswith("data:") else open(im["src"].replace("file://", ""), "rb").read()
            I = Image.open(io.BytesIO(raw)).convert("RGBA"); W, H = I.size; bw, bh = im["w"], im["h"]
            if im["fit"] == "cover":
                s_ = max(bw / W, bh / H); cw, ch = bw / s_, bh / s_
                px, py = [float(v.strip("%")) / 100 if v.endswith("%") else 0.5 for v in (im["pos"].split() + ["50%"])[:2]]
                x0, y0 = (W - cw) * px, (H - ch) * py; I = I.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
            elif im["fit"] == "contain":
                s_ = min(bw / W, bh / H); nw, nh = W * s_, H * s_; im.update(x=im["x"] + (bw - nw) / 2, y=im["y"] + (bh - nh) / 2, w=nw, h=nh)
            I.save(os.path.join(OUT, f"img_{si}_{k}.png")); del im["src"]
    # background: hide pictures and make text transparent (keeps boxes, cards, icons)
    pg.add_style_tag(content="section img[data-k]{visibility:hidden!important} [data-txt]{color:transparent!important} [data-txt] *{color:transparent!important} section::after{content:''!important} .pop{background:transparent!important;box-shadow:none!important}")
    for si, sec in enumerate(secs):
        sec.screenshot(path=os.path.join(OUT, f"bg_{si}.png"))
    b.close()
json.dump(data, open(os.path.join(OUT, "slides.json"), "w"))
print(len(data), "slides", sum(len(d["texts"]) for d in data), "text boxes", sum(len(d["imgs"]) for d in data), "images")
