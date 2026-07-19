"""Figure/Table 3: Hallucination-detection examples rendered as a table figure.

The example rows are REAL guardrail outputs observed during Phase 3A testing;
swap in examples from the production run before submission.
Outputs: output/fig3_hallucination.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

rows = [
    ["Sambar (retrieved as-is)", "PASS", "none"],
    ["Paneer Tikka with Dal\n(LLM-composed meal)", "FLAGGED",
     "macro deviation: protein +150%,\ncarbs +817% vs. per-100g KB values"],
    ["'Namkeen cloud bowl'\n(synthetic unknown food)", "FLAGGED", "unknown food: not in knowledge base"],
    ["Chicken Curry under\nvegetarian constraint", "VIOLATION", "non-vegetarian food detected"],
]

fig, ax = plt.subplots(figsize=(8.5, 3.2))
ax.axis("off")

table = ax.table(
    cellText=rows,
    colLabels=["Recommendation", "Verdict", "Guardrail reason"],
    colWidths=[0.34, 0.14, 0.52],
    cellLoc="left",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.2)

verdict_colors = {"PASS": "#138808", "FLAGGED": "#D97706", "VIOLATION": "#DC2626"}
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D1D5DB")
    if row == 0:
        cell.set_facecolor("#F3F4F6")
        cell.set_text_props(fontweight="bold")
    elif col == 1:
        cell.set_text_props(color=verdict_colors.get(rows[row - 1][1], "black"), fontweight="bold")

ax.set_title("Guardrail verdicts on example recommendations", fontsize=12, pad=12)
fig.tight_layout()
fig.savefig(OUT / "fig3_hallucination.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig3_hallucination.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig3_hallucination.{pdf,png}")
