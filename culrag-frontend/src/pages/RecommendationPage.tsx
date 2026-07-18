import LoadingSpinner from "../components/LoadingSpinner";
import PreferenceForm from "../components/PreferenceForm";
import RecommendationCard from "../components/RecommendationCard";
import { useRecommendation } from "../hooks/useRecommendation";

/** Main dashboard: preferences form on the left, results on the right. */
export default function RecommendationPage() {
  const { recommendation, loading, error, fetchRecommendation, sendFeedback } =
    useRecommendation();

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-gradient-to-r from-saffron to-amber-500 py-6 shadow">
        <div className="mx-auto max-w-6xl px-4">
          <h1 className="text-3xl font-bold text-white">CulRAG</h1>
          <p className="text-amber-50">
            Culturally grounded nutrition guidance for Indian cuisine
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-4 py-8 lg:grid-cols-2">
        <section aria-label="Preferences">
          <PreferenceForm onSubmit={fetchRecommendation} loading={loading} />
        </section>

        <section aria-label="Recommendation" aria-live="polite">
          {loading && <LoadingSpinner />}

          {!loading && error && (
            <div className="rounded-xl bg-red-50 p-6 text-red-700 shadow-md" role="alert">
              <h2 className="mb-1 font-semibold">Something went wrong</h2>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {!loading && !error && recommendation && (
            <RecommendationCard
              key={recommendation.recommendation_id}
              recommendation={recommendation}
              onFeedback={sendFeedback}
            />
          )}

          {!loading && !error && !recommendation && (
            <div className="flex h-full min-h-[300px] flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-8 text-center text-gray-400">
              <span aria-hidden="true" className="mb-3 text-5xl">
                🥘
              </span>
              <p>Set your preferences and get a personalized Indian meal recommendation.</p>
            </div>
          )}
        </section>
      </main>

      <footer className="py-6 text-center text-xs text-gray-400">
        CulRAG research project — recommendations are informational, not medical advice.
      </footer>
    </div>
  );
}
