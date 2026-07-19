"""Figure 4: Regional coverage of the food knowledge base (pie chart).

Reads REAL data from data/sample_foods.csv at the repo root; automatically
reflects the full IFCT dataset once integrated.
Outputs: output/fig4_regional_coverage.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(HERE.parent.parent / "data" / "sample_foods.csv")
counts = df["region"].value_counts()

colors = {"North": "#4F46E5", "South": "#FF9933", "East": "#138808",
          "West": "#D97706", "Pan-India": "#8B5CF6"}

fig, ax = plt.subplots(figsize=(5.5, 5))
ax.pie(
    counts.values,
    labels=[f"{region}\n({count} foods)" for region, count in counts.items()],
    colors=[colors.get(region, "#6B7280") for region in counts.index],
    autopct="%1.0f%%",
    startangle=90,
    textprops={"fontsize": 9},
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
)
ax.set_title(f"Regional coverage of the knowledge base (n={len(df)} foods)", fontsize=11)

fig.tight_layout()
fig.savefig(OUT / "fig4_regional_coverage.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig4_regional_coverage.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig4_regional_coverage.{pdf,png}")
