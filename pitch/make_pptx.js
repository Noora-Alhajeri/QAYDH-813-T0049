// Build an editable PowerPoint from pitch/_layers (made by pitch/extract_layers.py).
// Each slide = background picture (cards, icons, lines) + every figure/screenshot as its own picture + every text as an editable text box.
const pptxgen = require("pptxgenjs"); const fs = require("fs"); const path = require("path");
const L = path.join(__dirname, "_layers"); const S = JSON.parse(fs.readFileSync(path.join(L, "slides.json")));
const PX = 13.333 / 1600, PT = 0.6;            // 1600 px slide -> 13.333 in; 1 px = 0.6 pt
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.title = "QAYDH · Team T0049 · 813 Challenge"; pres.author = "Team T0049";
pres.theme = { headFontFace: "Arial Narrow", bodyFontFace: "Calibri" };
const hex = c => { const m = (c || "").match(/\d+(\.\d+)?/g) || [0, 0, 0]; return m.slice(0, 3).map(v => (+v).toString(16).padStart(2, "0")).join("").toUpperCase(); };
const alpha = c => { const m = (c || "").match(/\d+(\.\d+)?/g); return m && m.length > 3 ? +m[3] : 1; };
const font = (f, t) => /[؀-ۿ]/.test(t) ? "Arial" : /Shoulders/.test(f) ? "Arial Narrow" : /Mono/.test(f) ? "Courier New" : "Calibri";
S.forEach((sd, si) => {
  const s = pres.addSlide(); s.background = { color: "14110E" };
  s.addImage({ path: path.join(L, `bg_${si}.jpg`), x: 0, y: 0, w: 13.333, h: 7.5, objectName: "Background (cards and icons)" });
  sd.imgs.forEach((im, k) => s.addImage({ path: path.join(L, `img_${si}_${k}.jpg`), x: im.x * PX, y: im.y * PX, w: im.w * PX, h: im.h * PX,
      rounding: false, objectName: `Picture ${k + 1}` }));
  sd.texts.forEach((t, k) => {
    const runs = []; t.runs.forEach((r, i) => {
      if (r.br) { if (runs.length) runs[runs.length - 1].options.breakLine = true; return; }
      if (alpha(r.color) < 0.05) return;
      let txt = t.upper ? r.t.toUpperCase() : r.t; if (!runs.length) txt = txt.replace(/^\s+/, "");
      const sh = /Shoulders/.test(r.font);
      runs.push({ text: txt, options: { color: hex(r.color), bold: r.bold, italic: r.italic, fontFace: font(r.font, txt),
        fontSize: Math.max(7, Math.round(r.size * PT * (sh ? 0.9 : 1) * 2) / 2), charSpacing: t.ls && t.ls !== "normal" ? parseFloat(t.ls) * PT : undefined } });
    });
    if (!runs.length) return; runs[runs.length - 1].text = runs[runs.length - 1].text.replace(/\s+$/, "");
    const lh = parseFloat(t.lh); const rtl = t.dir === "rtl" || /[\u0600-\u06FF]/.test(runs.map(r => r.text).join(""));
    const fs0 = Math.max(...t.runs.filter(r => r.size).map(r => r.size)); const one = t.h < (isFinite(lh) ? lh : fs0 * 1.25) * 1.5;
    s.addText(runs, { x: t.x * PX - 0.02, y: t.y * PX, w: t.w * PX * 1.08 + 0.04, h: Math.max(t.h * PX, 0.2), margin: 0, valign: "top", wrap: !one,
      align: rtl ? "right" : (["center", "right"].includes(t.align) ? t.align : "left"), rtlMode: rtl,
      lineSpacing: isFinite(lh) ? lh * PT : undefined, isTextBox: true, objectName: `Text ${k + 1}` });
  });
});
pres.writeFile({ fileName: path.join(__dirname, "QAYDH_T0049_pitch_editable.pptx") }).then(f => console.log("wrote", f));
