"""Figure/Table 6: Example queries and system outputs rendered as a table figure.

Row 1 is a REAL demo-mode output observed during Phase 3A testing; replace all
rows with production-mode (LLM) outputs before submission.
Outputs: output/fig6_examples.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

rows = [
    ["Vegetarian South Indian meal,\n~1400 kcal/day, ≤60 min",
     "Sambar", "102 kcal · P 5g / C 15g / F 2.5g\nSouth · Pitta-pacifying · 35 min"],
    ["[PLACEHOLDER: production query]", "[PLACEHOLDER]", "[PLACEHOLDER: LLM-composed meal\nwith portion + reasoning]"],
    ["[PLACEHOLDER: production query]", "[PLACEHOLDER]", "[PLACEHOLDER]"],
]

fig, ax = plt.subplots(figsize=(9, 2.8))
ax.axis("off")

table = ax.table(
    cellText=rows,
    colLabels=["User request", "Recommendation", "Details"],
    colWidths=[0.36, 0.2, 0.44],
    cellLoc="left",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.4)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D1D5DB")
    if row == 0:
        cell.set_facecolor("#F3F4F6")
        cell.set_text_props(fontweight="bold")

ax.set_title("Example recommendations  [rows 2-3 PLACEHOLDER]", fontsize=12, pad=12)
fig.tight_layout()
fig.savefig(OUT / "fig6_examples.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig6_examples.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig6_examples.{pdf,png}")
