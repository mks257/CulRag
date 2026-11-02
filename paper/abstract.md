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
macronutrients. On a hand-labeled evaluation set, an offline
baseline with a hash-based embedding achieves Precision@5 of 0.153, Recall@5 of
0.216, and MRR of 0.260 over 30 queries, while the guardrail layer flags
unknown foods and macronutrient deviations in generated recommendations. We
release the system, evaluation framework, and interactive dashboard to
support culturally grounded nutrition AI research.

<!-- @Kavya: tighten to exactly 150 words once metrics are final. -->
