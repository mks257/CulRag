import { useState } from "react";
import type { FeedbackRequest, RecommendationResponse } from "../types";
import MacroChart from "./MacroChart";

interface RecommendationCardProps {
  recommendation: RecommendationResponse;
  onFeedback: (feedback: FeedbackRequest) => Promise<boolean>;
}

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold text-white ${color}`}>
      {children}
    </span>
  );
}

/** Displays one meal recommendation with macros, badges, and feedback controls. */
export default function RecommendationCard({
  recommendation,
  onFeedback,
}: RecommendationCardProps) {
  const [comment, setComment] = useState("");
  const [feedbackState, setFeedbackState] = useState<"idle" | "sent" | "failed">("idle");

  const submitFeedback = async (rating: number) => {
    const ok = await onFeedback({
      recommendation_id: recommendation.recommendation_id,
      rating,
      comment: comment.trim() || null,
    });
    setFeedbackState(ok ? "sent" : "failed");
  };

  return (
    <article className="animate-slide-in space-y-5 rounded-xl bg-white p-6 shadow-md">
      <header className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{recommendation.meal_name}</h2>
          <p className="text-sm text-gray-500">{recommendation.portion}</p>
        </div>
        <div aria-hidden="true" className="text-4xl">
          🍛
        </div>
      </header>

      <div className="flex flex-wrap gap-2">
        <Badge color="bg-accent">{recommendation.region} Indian</Badge>
        {recommendation.vegetarian && <Badge color="bg-healthgreen">Vegetarian</Badge>}
        <Badge color="bg-saffron">{recommendation.ayurvedic_type}</Badge>
        <Badge color="bg-gray-500">{recommendation.cooking_time} min</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="flex flex-col justify-center rounded-lg bg-gray-50 p-4">
          <p className="text-sm text-gray-500">Calories</p>
          <p className="text-3xl font-bold text-gray-900">
            {recommendation.calories}
            <span className="ml-1 text-base font-normal text-gray-500">kcal</span>
          </p>
          <dl className="mt-3 space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Protein</dt>
              <dd className="font-medium">{recommendation.macros.protein_g}g</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Carbs</dt>
              <dd className="font-medium">{recommendation.macros.carbs_g}g</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Fat</dt>
              <dd className="font-medium">{recommendation.macros.fat_g}g</dd>
            </div>
          </dl>
        </div>
        <MacroChart macros={recommendation.macros} />
      </div>

      <p className="rounded-lg bg-amber-50 p-4 text-sm leading-relaxed text-gray-700">
        {recommendation.reasoning}
      </p>

      {!recommendation.guardrails.passed && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">
          ⚠️ This recommendation did not pass all safety checks:{" "}
          {recommendation.guardrails.violations.join("; ")}
        </p>
      )}

      <footer className="space-y-3 border-t pt-4">
        <label htmlFor="feedback-comment" className="block text-sm font-medium text-gray-700">
          How was this recommendation?
        </label>
        <textarea
          id="feedback-comment"
          rows={2}
          placeholder="Optional comment..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-accent focus:outline-none"
        />
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => submitFeedback(5)}
            disabled={feedbackState === "sent"}
            className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            aria-label="Like this recommendation"
          >
            👍 Like
          </button>
          <button
            type="button"
            onClick={() => submitFeedback(2)}
            disabled={feedbackState === "sent"}
            className="rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            aria-label="Dislike this recommendation"
          >
            👎 Dislike
          </button>
          {feedbackState === "sent" && (
            <span className="text-sm text-healthgreen">Thanks for your feedback!</span>
          )}
          {feedbackState === "failed" && (
            <span className="text-sm text-red-600" role="alert">
              Could not save feedback.
            </span>
          )}
        </div>
      </footer>
    </article>
  );
}
