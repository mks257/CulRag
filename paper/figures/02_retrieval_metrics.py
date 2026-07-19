"""Figure 2: Per-query retrieval metrics (Precision@5, Recall@5, MRR).

Reads real data from ../tables/eval_results.csv (regenerate that file after the
full-dataset evaluation run, then re-run this script).
Outputs: output/fig2_retrieval_metrics.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(HERE.parent / "tables" / "eval_results.csv")
per_query = df[df["query"] != "MEAN"]
embedding_label = df["embedding"].iloc[0]

x = np.arange(len(per_query))
width = 0.27

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(x - width, per_query["precision_at_5"], width, label="Precision@5", color="#4F46E5")
ax.bar(x, per_query["recall_at_5"], width, label="Recall@5", color="#138808")
ax.bar(x + width, per_query["reciprocal_rank"], width, label="Reciprocal rank", color="#FF9933")

ax.set_xticks(x)
ax.set_xticklabels(per_query["query"], rotation=35, ha="right", fontsize=8)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Score")
ax.set_title(f"Retrieval quality per evaluation query (embedding: {embedding_label})")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(OUT / "fig2_retrieval_metrics.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig2_retrieval_metrics.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig2_retrieval_metrics.{pdf,png}")
