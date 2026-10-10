"""Independent accuracy check: 60 simple-random points in the Musaffah block, labelled by people on VHR imagery.
usage: python validation/score_independent.py      (label CSVs from dashboard/label.html in validation/labels/)
Reports inter-rater agreement on the 20 shared points, accuracy vs the majority vote with a 95% Wilson CI,
macro-F1, Cohen's kappa and the majority-class baseline (always guessing the most common true class)."""
import glob, json, math, os
import numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score, confusion_matrix

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
pred = pd.read_csv(os.path.join(HERE, "independent_points_predictions.csv")).set_index("id").predicted
files = glob.glob(os.path.join(HERE, "labels", "*.csv"))
if not files: raise SystemExit("No label files in validation/labels/ yet: label the 60 points in dashboard/label.html first.")
L = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
L = L[L.id.isin(pred.index)].drop_duplicates(["id", "labeller"], keep="last")
L = L[L.label != "Unsure"]

def fleiss(tab):
    n = tab.sum(axis=1); tab = tab[n >= 2]; n = n[n >= 2]
    if len(tab) < 5: return float("nan")
    p = tab.sum(axis=0) / tab.values.sum(); P = ((tab ** 2).sum(axis=1) - n) / (n * (n - 1))
    return float((P.mean() - (p ** 2).sum()) / (1 - (p ** 2).sum()))
tab = pd.crosstab(L.id, L.label)
shared = tab[tab.sum(axis=1) >= 2]
pairs = {}
labs = sorted(L.labeller.unique())
for i in range(len(labs)):
    for j in range(i + 1, len(labs)):
        a = L[L.labeller == labs[i]].set_index("id").label; b = L[L.labeller == labs[j]].set_index("id").label; c = a.index.intersection(b.index)
        if len(c) >= 5: pairs[f"{labs[i]} vs {labs[j]}"] = dict(n=int(len(c)), agreement=float((a[c] == b[c]).mean()), cohen_kappa=float(cohen_kappa_score(a[c], b[c])))
top = tab.max(axis=1); second = tab.apply(lambda r: sorted(r.values)[-2] if len(r) > 1 else 0, axis=1)
truth = tab.idxmax(axis=1)[top > second]                       # majority vote; ties dropped
p_ = pred[truth.index]; n = len(truth); acc = float((p_ == truth).mean())
z = 1.96; lo = (acc + z*z/(2*n) - z*math.sqrt(acc*(1-acc)/n + z*z/(4*n*n))) / (1 + z*z/n); hi = (acc + z*z/(2*n) + z*math.sqrt(acc*(1-acc)/n + z*z/(4*n*n))) / (1 + z*z/n)
base_cls = truth.value_counts().idxmax(); base = float((truth == base_cls).mean())
cls = sorted(set(truth) | set(p_))
# location tolerance: is the labelled class present in the model map within 10 / 20 m of the point? (10 m pixels, imagery co-registration)
from PIL import Image
_D = os.path.join(ROOT, "qaydh_outputs", "dashboard"); _m = json.load(open(os.path.join(_D, "musaffah_overlays.json"))); (_a0, _o0), (_a1, _o1) = _m["bounds"]
_im = np.array(Image.open(os.path.join(_D, "musaffah_surfaces.png")).convert("RGB")).astype(int); _H, _W = _im.shape[:2]
_C = {(58, 58, 58): "Road / dark pavement", (228, 87, 46): "Building / roof", (43, 131, 186): "Water", (233, 216, 166): "Bare soil / sand", (46, 158, 68): "Vegetation"}
_pts = {f["properties"]["id"]: f["geometry"]["coordinates"][:2] for f in json.load(open(os.path.join(HERE, "independent_points.geojson")))["features"]}
def _within(r_):
    h_ = 0
    for i_, t_ in truth.items():
        lo_, la_ = _pts[i_]; x_ = int((lo_ - _o0) / (_o1 - _o0) * _W); y_ = int((_a1 - la_) / (_a1 - _a0) * _H)
        h_ += t_ in {_C.get(tuple(c_)) for c_ in _im[max(y_ - r_, 0):y_ + r_ + 1, max(x_ - r_, 0):x_ + r_ + 1].reshape(-1, 3)}
    return round(h_ / n, 3)
out = dict(design="60 simple-random points in the Musaffah 9x9 km block (seed 813); 20 labelled by all three teammates, 40 by one; Esri World Imagery ~0.3-0.5 m; blind to the model",
           labellers=labs, labels=int(len(L)), points_with_truth=n,
           inter_rater=dict(points_shared=int(len(shared)), fleiss_kappa=fleiss(tab), pairs=pairs),
           accuracy=acc, accuracy_CI95=[round(lo, 3), round(hi, 3)], macro_F1=float(f1_score(truth, p_, labels=cls, average="macro", zero_division=0)),
           cohen_kappa_vs_truth=float(cohen_kappa_score(truth, p_)), majority_class_baseline=dict(class_=base_cls, accuracy=base),
           accuracy_within_10m=_within(1), accuracy_within_20m=_within(2),
           confusion=pd.DataFrame(confusion_matrix(truth, p_, labels=cls), index=cls, columns=cls).to_dict())
json.dump(out, open(os.path.join(ROOT, "qaydh_outputs", "independent_check.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "confusion"}, indent=1))
r = os.path.join(ROOT, "qaydh_outputs", "results.json")
if os.path.exists(r): R = json.load(open(r)); R["independent_check"] = out; json.dump(R, open(r, "w"), indent=2, default=float)
