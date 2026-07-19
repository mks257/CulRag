"""Figure 1: CulRAG system architecture diagram.

Standalone; no repo data needed. Run from paper/figures/:
    python 01_architecture.py
Outputs: output/fig1_architecture.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

SAFFRON, GREEN, INDIGO, GRAY = "#FF9933", "#138808", "#4F46E5", "#6B7280"


def box(ax, xy, w, h, label, sublabel, color):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                facecolor=color, edgecolor="none", alpha=0.9))
    ax.text(x + w / 2, y + h * 0.62, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white")
    ax.text(x + w / 2, y + h * 0.3, sublabel, ha="center", va="center",
            fontsize=8, color="white")


def arrow(ax, start, end, label=""):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18,
                                 linewidth=1.6, color="#374151"))
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + 0.035, label, ha="center", fontsize=8, color="#374151")


fig, ax = plt.subplots(figsize=(10, 3.2))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

box(ax, (0.01, 0.38), 0.15, 0.3, "User query", "preferences +\nconstraints", GRAY)
box(ax, (0.22, 0.38), 0.17, 0.3, "Retriever", "Chroma / Pinecone\nk-NN search", INDIGO)
box(ax, (0.45, 0.38), 0.17, 0.3, "LLM chain", "GPT-4 / Claude\nJSON meal plan", SAFFRON)
box(ax, (0.68, 0.38), 0.17, 0.3, "Guardrails", "constraints +\nhallucination checks", GREEN)
box(ax, (0.88, 0.38), 0.11, 0.3, "Output", "validated\nrecommendation", GRAY)

box(ax, (0.22, 0.02), 0.17, 0.24, "Knowledge base", "IFCT 2017 foods\nregion + Ayurveda", "#8B5CF6")

arrow(ax, (0.16, 0.53), (0.22, 0.53))
arrow(ax, (0.39, 0.53), (0.45, 0.53), "top-k foods")
arrow(ax, (0.62, 0.53), (0.68, 0.53), "candidate meal")
arrow(ax, (0.85, 0.53), (0.88, 0.53))
arrow(ax, (0.305, 0.26), (0.305, 0.38))
# Guardrails validate against the same KB
ax.add_patch(FancyArrowPatch((0.39, 0.12), (0.765, 0.38), arrowstyle="-|>",
                             mutation_scale=18, linewidth=1.4, color="#374151",
                             linestyle="--", connectionstyle="arc3,rad=-0.25"))
ax.text(0.62, 0.13, "validate against KB", fontsize=8, color="#374151")

fig.suptitle("CulRAG pipeline: retrieve → generate → validate", fontsize=12, y=0.98)
fig.tight_layout()
fig.savefig(OUT / "fig1_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig1_architecture.png", dpi=200, bbox_inches="tight")
print("wrote", OUT / "fig1_architecture.{pdf,png}")
