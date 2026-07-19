"""Figure 5: Constraint-compliance rates by check type (bar chart).

PLACEHOLDER DATA — replace the COMPLIANCE dict with output from
RAGEvaluator.evaluate_batch() on the full-dataset production run.
Outputs: output/fig5_compliance.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

# PLACEHOLDER: fill from evaluate_batch() results (fraction passing each check).
COMPLIANCE = {
    "Vegetarian": None,
    "Calorie window": None,
    "Allergens": None,
    "No hallucination flags": None,
    "All checks (pass rate)": None,
}
PLACEHOLDER_VALUE = 0.5  # bars render at 0.5 with hatching until real data lands

labels = list(COMPLIANCE)
values = [v if v is not None else PLACEHOLDER_VALUE for v in COMPLIANCE.values()]
is_placeholder = [v is None for v in COMPLIANCE.values()]

fig, ax = plt.subplots(figsize=(7.5, 4))
bars = ax.bar(np.arange(len(labels)), values, color="#138808", width=0.6)
for bar, placeholder in zip(bars, is_placeholder):
    if placeholder:
        bar.set_hatch("//")
        bar.set_facecolor("#D1D5DB")

ax.set_xticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Fraction of recommendations passing")
title = "Constraint compliance by check type"
if any(is_placeholder):
    title += "  [PLACEHOLDER DATA]"
ax.set_title(title)
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(OUT / "fig5_compliance.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig5_compliance.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig5_compliance.{pdf,png}")
