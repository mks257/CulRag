# Abstract

<!-- Target: 150 words. Status: STUB — fill metrics after full-dataset evaluation. -->

Personalized nutrition systems built on large language models (LLMs)
typically retrieve from Western-default food databases, limiting their
relevance and safety for the majority of the world's eaters. We present
**CulRAG**, a retrieval-augmented generation system for Indian dietary
guidance that grounds LLM recommendations in a knowledge base derived from
the Indian Food Composition Tables (IFCT 2017), enriched with regional and
Ayurvedic attributes. CulRAG couples vector retrieval with a rule-based
guardrail layer that validates every recommendation for vegetarian
compliance, calorie targets, allergens, and hallucinated foods or
macronutrients. On a hand-labeled evaluation set, the system achieves
[PLACEHOLDER: X% Precision@5, Y% Recall@5, Z MRR] with a hallucination rate
of [PLACEHOLDER: H%] before guardrails and [PLACEHOLDER: H'%] after. We
release the system, evaluation framework, and interactive dashboard to
support culturally grounded nutrition AI research.

<!-- @Kavya: tighten to exactly 150 words once metrics are final. -->
