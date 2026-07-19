import { FormEvent, useState } from "react";
import type { RecommendationRequest } from "../types";

interface PreferenceFormProps {
  onSubmit: (request: RecommendationRequest) => void;
  loading: boolean;
}

const REGIONS = ["Any", "North", "South", "East", "West"];
const AYURVEDIC_TYPES = ["Balanced", "Vata", "Pitta", "Kapha"];

/** Collects dietary preferences and submits them as a RecommendationRequest. */
export default function PreferenceForm({ onSubmit, loading }: PreferenceFormProps) {
  const [calories, setCalories] = useState(1800);
  const [vegetarian, setVegetarian] = useState(true);
  const [region, setRegion] = useState("Any");
  const [ayurvedicType, setAyurvedicType] = useState("Balanced");
  const [allergies, setAllergies] = useState("");
  const [cookingTime, setCookingTime] = useState(60);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (calories < 1200 || calories > 3000) {
      setValidationError("Calorie target must be between 1200 and 3000.");
      return;
    }
    setValidationError(null);

    const allergyList = allergies
      .split(",")
      .map((a) => a.trim())
      .filter(Boolean);

    onSubmit({
      target_calories: calories,
      vegetarian,
      regional_preference: region,
      ayurvedic_type: ayurvedicType,
      allergies: allergyList.length > 0 ? allergyList : null,
      cooking_time_min: cookingTime,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-xl bg-white p-6 shadow-md"
      aria-label="Meal preferences"
    >
      <h2 className="text-xl font-semibold text-gray-800">Your Preferences</h2>

      <div>
        <label htmlFor="calories" className="mb-1 block text-sm font-medium text-gray-700">
          Daily calorie target: <span className="font-semibold text-saffron">{calories} kcal</span>
        </label>
        <input
          id="calories"
          type="range"
          min={1200}
          max={3000}
          step={50}
          value={calories}
          onChange={(e) => setCalories(Number(e.target.value))}
          className="w-full accent-saffron"
        />
      </div>

      <div className="flex items-center justify-between">
        <label htmlFor="vegetarian" className="text-sm font-medium text-gray-700">
          Vegetarian only
        </label>
        <button
          id="vegetarian"
          type="button"
          role="switch"
          aria-checked={vegetarian}
          onClick={() => setVegetarian(!vegetarian)}
          className={`relative h-6 w-11 rounded-full transition-colors ${
            vegetarian ? "bg-healthgreen" : "bg-gray-300"
          }`}
        >
          <span
            className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
              vegetarian ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
      </div>

      <div>
        <label htmlFor="region" className="mb-1 block text-sm font-medium text-gray-700">
          Regional preference
        </label>
        <select
          id="region"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="w-full rounded-lg border border-gray-300 p-2 focus:border-accent focus:outline-none"
        >
          {REGIONS.map((r) => (
            <option key={r} value={r}>
              {r === "Any" ? "Any region" : `${r} Indian`}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="ayurvedic" className="mb-1 block text-sm font-medium text-gray-700">
          Ayurvedic type
        </label>
        <select
          id="ayurvedic"
          value={ayurvedicType}
          onChange={(e) => setAyurvedicType(e.target.value)}
          className="w-full rounded-lg border border-gray-300 p-2 focus:border-accent focus:outline-none"
        >
          {AYURVEDIC_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="allergies" className="mb-1 block text-sm font-medium text-gray-700">
          Allergies <span className="text-gray-400">(comma-separated)</span>
        </label>
        <input
          id="allergies"
          type="text"
          placeholder="e.g. peanuts, shellfish"
          value={allergies}
          onChange={(e) => setAllergies(e.target.value)}
          className="w-full rounded-lg border border-gray-300 p-2 focus:border-accent focus:outline-none"
        />
      </div>

      <div>
        <label htmlFor="cookingTime" className="mb-1 block text-sm font-medium text-gray-700">
          Max cooking time:{" "}
          <span className="font-semibold text-saffron">{cookingTime} min</span>
        </label>
        <input
          id="cookingTime"
          type="range"
          min={0}
          max={60}
          step={5}
          value={cookingTime}
          onChange={(e) => setCookingTime(Number(e.target.value))}
          className="w-full accent-saffron"
        />
      </div>

      {validationError && (
        <p className="text-sm text-red-600" role="alert">
          {validationError}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-saffron py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Generating..." : "Get Recommendation"}
      </button>
    </form>
  );
}
