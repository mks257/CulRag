# 4. Methods

<!-- Target: ~1500 words. Status: SUBSTANTIVE DRAFT (Kavya, review before submission). -->
<!-- All code references point to https://github.com/mks257/CulRag (branch: dev). -->

## 4.1 System Overview

CulRAG is a retrieval-augmented generation (RAG) system that grounds large
language model (LLM) meal recommendations in a culturally specific knowledge
base of Indian foods. The system comprises four modules arranged in a
pipeline (Figure 1): a **retrieval module** that embeds and indexes food
records in a vector database; an **LLM chain** that composes meal
recommendations from retrieved context; a **guardrail module** that validates
each recommendation against user constraints and the knowledge base; and an
**evaluation module** that measures retrieval quality and recommendation
safety. An orchestrator class (`CulRAG`, in `src/rag_pipeline.py`) wires the
modules into a single `recommend()` entry point:

```
function RECOMMEND(query, constraints):
    docs   <- retriever.search(query, k)          # vector k-NN over food KB
    rec    <- llm_chain.generate(query, docs)     # JSON meal recommendation
    checks <- guardrails.run_all_checks(rec, constraints, KB)
    return {recommendation: rec, retrieved: docs, guardrails: checks}
```

Two design principles drove the architecture. First, **modularity**: each
module is independently replaceable (e.g., the vector store can be switched
between a local and a cloud backend without touching generation code), which
enables the component-wise ablations reported in Section 5. Second,
**testability without paid APIs**: every module accepts injected
dependencies (embedding functions, LLM clients), so the full pipeline runs
offline under deterministic stand-ins. All results in this paper are
reproducible from the public repository, which includes 42 unit tests
covering retrieval, evaluation, and the serving API.

## 4.2 Knowledge Base

The knowledge base is derived from the Indian Food Composition Tables (IFCT
2017) published by the National Institute of Nutrition, India
[@longvah2017ifct], which provides laboratory-measured nutrient composition
for 528 commonly consumed Indian foods. For the experiments in this paper we
use a hand-curated development subset of 50 representative foods spanning
dals, millets, regional staples (idli, dosa, paratha), paneer dishes,
condiments, and desserts; integration of the full IFCT database is described
in Section 6 as ongoing work. <!-- @Vartan: update this paragraph when the full dataset lands -->

Each food is a row with ten attributes: name, region (North, South, East,
West, Pan-India), vegetarian flag, energy (kcal), protein, carbohydrate,
fat, and fiber (g per 100 g), an Ayurvedic classification (e.g.,
*Pitta-pacifying*, *Tridoshic*), and cooking method (Table 1). The Ayurvedic
and regional attributes are the culturally grounding signal that
distinguishes our knowledge base from Western-default databases such as USDA
FoodData Central used in prior RAG nutrition systems [@khamesian2025nutrigen].
The development subset is 94% vegetarian, reflecting the dietary context of
the target population.

For indexing, each record is rendered as a natural-language passage
(`CulRAG._food_to_text()`) that verbalizes all ten attributes, e.g.:

> "Palak Paneer: 180 kcal, protein 9.5g, carbs 7.0g, fat 13.0g, fiber 2.2g,
> vegetarian, region North, ayurvedic type Pitta-pacifying, cooking method
> Sauteed"

The structured row is preserved as vector-store metadata, so downstream
modules can filter and validate on exact values rather than re-parsing text.

## 4.3 Retrieval Module

The retrieval module (`VectorRetriever`, `src/retriever.py`) abstracts over
two vector-store backends behind one interface: **Chroma** for local,
persistent, zero-cost indexing, and **Pinecone** for managed cloud
deployment. Passages are embedded with OpenAI `text-embedding-3-small`
(1,536 dimensions), chosen for its cost/quality balance at our corpus scale;
the embedding function is injectable, which we exploit both for offline
testing (a deterministic hashing embedder) and for future embedding
ablations. Queries are answered by cosine-similarity k-nearest-neighbor
search (k = 5 unless stated otherwise), returning the passage, its
structured metadata, and a similarity score.

## 4.4 LLM Chain

The generation module (`RAGChain`, `src/llm_chain.py`) supports both OpenAI
(GPT-4) and Anthropic (Claude) chat models behind a common interface. The
prompt template instructs the model to (i) recommend a meal **using only the
retrieved foods**, (ii) report calories, macronutrients, and portion size,
(iii) respect the user's stated constraints, and (iv) reference Ayurvedic
properties where relevant. The model must respond with a single JSON object:

```json
{
  "meal_name": "...", "calories": 0,
  "macros": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
  "portion": "...", "reasoning": "..."
}
```

Responses are parsed defensively (JSON extracted from surrounding prose or
code fences); malformed outputs are surfaced as structured errors rather
than propagated, so a generation failure can never silently reach a user.
Sampling temperature is 0.7. Prompt-constrained generation of this kind —
restricting the model to retrieved, verifiable foods — follows the
grounding strategy of retrieval-constrained meal generators
[@metaplate2025], and is the first of two defenses against hallucination;
the second is post-hoc validation, described next.

## 4.5 Guardrails

Because dietary advice is a safety-relevant domain, every recommendation
passes through a rule-based validator (`GuardrailChecker`,
`src/guardrails.py`) before being shown to a user. Four checks are applied:

1. **Vegetarian compliance** — the recommended meal is cross-referenced
   against the knowledge base's vegetarian flags, with a keyword fallback
   for foods outside the KB.
2. **Calorie window** — recommended calories must fall within the user's
   target range.
3. **Allergen screening** — meal name and reasoning are scanned for
   user-declared allergens.
4. **Hallucination detection** — the meal name is decomposed into component
   dishes; any component with no knowledge-base match is flagged as an
   *unknown food*, and matched components whose reported macronutrients
   deviate from the knowledge-base values by more than 30% are flagged as
   *macro hallucinations*.

The validator returns a structured verdict — pass/fail, itemized
violations, hallucination flags, and a confidence score — which is logged
for audit and displayed to end users in the companion dashboard (Section
4.7). We deliberately chose transparent, rule-based checks over a learned
critic: in a regulated domain, an auditable failure reason ("calories 900
outside range (300, 700)") is worth more than marginal accuracy from an
opaque model. Limitations of this choice are discussed in Section 6.

## 4.6 Evaluation Framework

The evaluation module (`RAGEvaluator`, `src/evaluator.py`) measures the two
failure surfaces of the pipeline separately.

**Retrieval quality** is scored against a hand-labeled test set
(`data/eval_queries.json`) of queries paired with ground-truth relevant
foods, covering regional cuisine, Ayurvedic properties, macronutrient
goals, desserts, and non-vegetarian requests. We report Precision@k,
Recall@k, and mean reciprocal rank (MRR), following standard RAG evaluation
practice [@rageval2025survey; @chen2023rgb].

**Recommendation safety** is scored by running batches of queries through
the full pipeline and aggregating guardrail verdicts into three rates: the
*pass rate* (fraction of recommendations with zero constraint violations),
the *hallucination rate* (fraction with at least one hallucination flag),
and mean confidence.

All metric implementations are unit-tested against hand-computed values,
including edge cases (empty retrievals, missing relevance labels,
generation failures).

## 4.7 Implementation and Deployment

CulRAG is implemented in Python 3.9+ (pandas, Chroma, OpenAI/Anthropic
SDKs, python-dotenv); the serving layer is a FastAPI application
(`src/api.py`) exposing the pipeline over HTTP with Pydantic-validated
request/response schemas, and a React/TypeScript dashboard collects
structured user feedback (1–5 rating plus free text) for the planned pilot
study. The API runs in two modes: a *full* mode using production embeddings
and LLM generation, and an offline *demo* mode (deterministic hash
embeddings, retrieval-only recommendations) that exercises the identical
code path without external API dependencies — the same mechanism our test
suite and continuous integration use. Code, data schema, evaluation
queries, and deployment configurations are available in the public
repository.

<!-- [FIGURE 1 GOES HERE: system architecture] -->
<!-- [TABLE 1 GOES HERE: sample of 5 food records — generated from paper/tables/food_db_sample.csv] -->
