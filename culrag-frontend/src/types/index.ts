/** TypeScript mirrors of the backend Pydantic models (src/api.py). */

export interface RecommendationRequest {
  target_calories: number;
  vegetarian: boolean;
  regional_preference?: string | null;
  ayurvedic_type?: string | null;
  allergies?: string[] | null;
  cooking_time_min?: number | null;
}

export interface Macros {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface GuardrailResult {
  passed: boolean;
  violations: string[];
  flags: string[];
  confidence: number;
}

export interface RecommendationResponse {
  meal_name: string;
  calories: number;
  macros: Macros;
  portion: string;
  cooking_time: number;
  region: string;
  vegetarian: boolean;
  ayurvedic_type: string;
  reasoning: string;
  recommendation_id: string;
  guardrails: GuardrailResult;
}

export interface FeedbackRequest {
  recommendation_id: string;
  rating: number;
  comment?: string | null;
}
