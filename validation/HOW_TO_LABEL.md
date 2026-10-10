# Independent accuracy check: how to label (10–20 minutes)

1. Open **https://noora-alhajeri.github.io/QAYDH-813-T0049/dashboard/label.html** (Chrome or Safari, laptop).
2. Type your name in box 1 (Entesar, Noora or Maryam).
3. In box 2 choose **"Accuracy check · 60 random points (surface class)"**.
4. For each orange square, press the class that covers most of the 10 m square:
   1 Road / dark pavement · 2 Building / roof · 3 Bare soil / sand · 4 Vegetation · 5 Water · 6 Unsure.
   Keys 1–6 work. The model's answer is hidden on purpose: label what you see, and do not compare with anyone.
5. **Entesar and Maryam:** label **P-01 to P-20** (the first 20 shown), then stop.
   **Noora:** label all 60.
6. Click **Download my labels (CSV)**. You get `independent_check_<name>.csv`. Send it to Noora.
   Labels save in your browser, so you can close the page and continue later in the same browser.

**Noora, after all three files arrive:** put them in `validation/labels/`, then run
`python validation/score_independent.py`. It writes `qaydh_outputs/independent_check.json` with accuracy (95% CI), macro-F1,
Cohen's κ, the majority-class baseline and the inter-rater κ on the 20 shared points.
