# Skill: Maintaining Skills

Meta-skill: keeps every other skill in `skills/` true as the model, code, and data evolve.
A skill that states stale facts is worse than no skill — the assistant will act on it
confidently. Load this skill at the END of any work session that changed the repo, or
when explicitly asked to "sync/update the skills".

## The trigger table — what changed → which skills to update

| Repo change | Update these skills |
|---|---|
| Class/method added, renamed, or removed in `src/` | `rag-pipeline` (component map), `culrag-context` (architecture) |
| `sample_foods.csv` schema or full-dataset columns change | `building-food-data` (data contract), `rag-pipeline` (document format) |
| New dataset file / full IFCT import lands | `building-food-data`, `evaluating-rag` (dataset version note), `culrag-context` (data section, phases) |
| `eval_queries.json` format or metric definitions change | `evaluating-rag` |
| `GuardrailChecker` output shape changes | `rag-pipeline` (rule 5), `evaluating-rag` (safety metrics), `serving-api` (response shape) |
| Dependency upgraded / swapped (requirements.txt) | `rag-pipeline` (versions section), `CLAUDE.md` quick facts |
| LLM model / embedding model switched | `rag-pipeline`, `running-experiments` (config record fields), `evaluating-rag` |
| New paper claim, dropped claim, venue change | `culrag-context` (contributions), `writing-the-paper`, `deep-research` (claim table) |
| RELATED_WORK.md restructured or closest-prior-work changes | `deep-research` |
| Phase completed / roadmap change | `culrag-context` (phases), `skills/README.md` if a new task category exists |
| API endpoints added/changed | `serving-api` |
| New recurring task with no matching skill | Create the skill + add a router row |

## Verification protocol (run this, don't eyeball)

1. **Code facts:** `grep -E "^(class | +def )" src/*.py` — diff against the component maps
   in `rag-pipeline` and `culrag-context`.
2. **Data facts:** read the header row of each dataset CSV — diff against the contract
   table in `building-food-data`.
3. **Version facts:** `pip list` for the packages named in `rag-pipeline`'s version
   section and `CLAUDE.md`.
4. **Path facts:** every file path mentioned in any skill must exist (`skills/`-wide grep
   for `src/`, `data/`, `scripts/`, `results/`, `tests/` and check each). Paths marked
   "when it exists" are allowed as forward references.
5. **Cross-references:** every skill named in `skills/README.md`'s table exists, and every
   skill folder appears in the table.

## Rules

- Update the skill in the SAME commit as the change that invalidated it, when feasible.
- Skills state facts and project decisions, not history — replace stale text, don't
  append "UPDATE:" notes. Git holds the history.
- Keep each skill loadable alone: if an update makes one skill depend on reading another
  mid-task, inline the needed fact instead (except `culrag-context`, which is the shared
  base).
- Don't grow skills — a skill over ~80 lines is trying to be two skills or a README.
  Cut generic advice; keep only what's specific to CulRAG.
- Deleting beats deprecating: a skill for a task that no longer exists is removed from
  the folder AND the router table in the same commit.
