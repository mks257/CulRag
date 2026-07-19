# Skill: Deep Research

For literature review and related-work research supporting the CulRAG paper.

## Where findings live

`RELATED_WORK.md` at repo root is the single ledger (14 entries as of 2026-07). Follow
its existing convention — numbered entries under category sections:

```markdown
## <Category section, by how it will be cited>

N. <Title>
   - <arXiv/DOI/journal link>
   - One-line note: what it did and why it matters to CulRAG.
```

Existing sections: **Directly Indian** (most important), **LLM / RAG nutrition systems —
baseline comparisons**, **Benchmarks and evaluation methodology**, **Background /
Foundational**. Add to the right section; continue the numbering. When a paper has
numbers we'll compare against (hallucination rate, P@k), put them in the note.

No entry → the paper effectively wasn't read. Duplicate check before adding.

## What to research (mapped to the paper's claims)

| Claim in our paper | Literature needed |
|---|---|
| First systematic eval of cultural grounding in RAG nutrition | Prior RAG-for-nutrition / diet-recommendation systems — must survey to defend "first" |
| RAG optimized for Indian cuisine | Food knowledge bases, IFCT-based systems, non-Western food NLP |
| Ayurveda + modern nutrition integration | Computational Ayurveda work; be careful — cite as cultural framework, not medical evidence |
| Hallucination rates in dietary recommendations | LLM hallucination measurement methods, RAG faithfulness metrics (RAGAS etc.) |

Also needed: baselines to compare against (vanilla LLM without retrieval, generic RAG
without cultural KB) and standard metric definitions to cite rather than reinvent.

## Method

1. **Search:** Google Scholar, Semantic Scholar, arXiv (cs.CL, cs.IR), PubMed for
   nutrition-side work. Search both directions: "RAG nutrition", "dietary recommendation
   LLM", "cultural bias food LLM", "Indian food database NLP", "hallucination detection RAG".
2. **Snowball:** from each relevant paper, chase its references and its citers.
3. **Read for the claim, not the abstract.** Extract: their dataset size, metrics,
   numbers, and limitations — that's what our related-work section compares against.
4. **The "first" claim is fragile.** Actively hunt for counterexamples to our novelty
   claims. Finding one BEFORE submission means we reword; a reviewer finding it means
   rejection. Log near-misses in RELATED_WORK.md with why they differ from us.
   Known closest prior work already in the ledger: **entry 3, Explainable Graph-RAG for
   Personalized Nutrition (Indian Thali), Frontiers in AI 2026** — any novelty wording
   must explicitly differentiate from it (their focus: graph-RAG explainability; ours:
   systematic evaluation of cultural grounding + hallucination measurement).

## Rules

- Primary sources only for numbers — never cite a blog's summary of a paper.
- Verify every citation exists (title, authors, venue, year) before it enters the ledger;
  LLM-remembered citations are hallucination-prone — check DOI/arXiv links resolve.
- Preprints are citable but mark them as such; prefer the published version if one exists.
- Track venue fit: IEEE Access / Frontiers in AI — note papers from those venues as
  style/structure references.
