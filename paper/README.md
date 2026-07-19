# CulRAG Paper Workspace

Working directory for the Paper 1 (system/architecture) manuscript.

## Layout

```
paper/
├── paper.md          # Master file: assembly order, status tracker, checklist
├── abstract.md       # One file per section — edit independently, merge at the end
├── introduction.md
├── related_work.md
├── methods.md        # SUBSTANTIVE DRAFT — start reviewing here
├── results.md
├── discussion.md
├── conclusion.md
├── references.bib    # BibTeX; entries with "TODO verify" need metadata confirmed
├── figures/          # Standalone matplotlib scripts → figures/output/*.pdf + .png
└── tables/           # CSV sources for in-paper tables
```

## Workflow

1. **Methods is drafted** — Kavya reviews/edits first, it anchors everything else.
2. Stubs contain per-paragraph outlines as HTML comments with citation keys
   already wired to `references.bib` — expand comments into prose.
3. Figures: `cd paper/figures && python 01_architecture.py` (etc.). Each script
   is standalone, reads real repo data where it exists, and writes PDF + PNG to
   `figures/output/`. Re-run after the full-dataset evaluation to refresh.
4. `@Kavya` / `@Vartan` comments mark ownership of specific passages.
5. Before submission: work through the checklist at the bottom of `paper.md`.

## Ground rules baked into the scaffold

- **No invented citations.** Every references.bib entry comes from the repo's
  curated RELATED_WORK.md or is a verified foundational paper. Entries whose
  full metadata wasn't on hand are explicitly marked `TODO verify` — confirm
  them against the linked URL before submission, never guess.
- **Baseline numbers are labeled as baselines.** The retrieval metrics currently
  in results.md come from the offline hash-embedding run (pipeline validation
  only) and are marked as placeholders for the production-embedding run.
