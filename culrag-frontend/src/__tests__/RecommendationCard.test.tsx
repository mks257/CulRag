import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import RecommendationCard from "../components/RecommendationCard";
import type { RecommendationResponse } from "../types";

const RECOMMENDATION: RecommendationResponse = {
  meal_name: "Paneer Tikka",
  calories: 242,
  macros: { protein_g: 18, carbs_g: 6, fat_g: 17 },
  portion: "1 standard serving (100g)",
  cooking_time: 25,
  region: "North",
  vegetarian: true,
  ayurvedic_type: "Kapha-aggravating",
  reasoning: "High protein vegetarian option for your goals.",
  recommendation_id: "rec-123",
  guardrails: { passed: true, violations: [], flags: [], confidence: 0.95 },
};

describe("RecommendationCard", () => {
  it("renders meal name, calories, and badges", () => {
    render(<RecommendationCard recommendation={RECOMMENDATION} onFeedback={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "Paneer Tikka" })).toBeInTheDocument();
    expect(screen.getByText("242")).toBeInTheDocument();
    expect(screen.getByText("North Indian")).toBeInTheDocument();
    expect(screen.getByText("Vegetarian")).toBeInTheDocument();
    expect(screen.getByText("25 min")).toBeInTheDocument();
    expect(
      screen.getByText("High protein vegetarian option for your goals."),
    ).toBeInTheDocument();
  });

  it("displays macro values", () => {
    render(<RecommendationCard recommendation={RECOMMENDATION} onFeedback={vi.fn()} />);

    expect(screen.getByText("18g")).toBeInTheDocument();
    expect(screen.getByText("6g")).toBeInTheDocument();
    expect(screen.getByText("17g")).toBeInTheDocument();
  });

  it("sends rating 5 with comment when Like is clicked", async () => {
    const onFeedback = vi.fn().mockResolvedValue(true);
    const user = userEvent.setup();
    render(<RecommendationCard recommendation={RECOMMENDATION} onFeedback={onFeedback} />);

    await user.type(screen.getByLabelText(/how was this recommendation/i), "Loved it");
    await user.click(screen.getByRole("button", { name: /^like this recommendation$/i }));

    expect(onFeedback).toHaveBeenCalledWith({
      recommendation_id: "rec-123",
      rating: 5,
      comment: "Loved it",
    });
    await waitFor(() =>
      expect(screen.getByText(/thanks for your feedback/i)).toBeInTheDocument(),
    );
  });

  it("sends rating 2 when Dislike is clicked", async () => {
    const onFeedback = vi.fn().mockResolvedValue(true);
    const user = userEvent.setup();
    render(<RecommendationCard recommendation={RECOMMENDATION} onFeedback={onFeedback} />);

    await user.click(screen.getByRole("button", { name: /dislike this recommendation/i }));

    expect(onFeedback).toHaveBeenCalledWith({
      recommendation_id: "rec-123",
      rating: 2,
      comment: null,
    });
  });

  it("shows an error message when feedback fails", async () => {
    const onFeedback = vi.fn().mockResolvedValue(false);
    const user = userEvent.setup();
    render(<RecommendationCard recommendation={RECOMMENDATION} onFeedback={onFeedback} />);

    await user.click(screen.getByRole("button", { name: /^like this recommendation$/i }));

    await waitFor(() =>
      expect(screen.getByText(/could not save feedback/i)).toBeInTheDocument(),
    );
  });

  it("shows guardrail violations when checks fail", () => {
    const failing = {
      ...RECOMMENDATION,
      guardrails: {
        passed: false,
        violations: ["Calories 900 outside target range"],
        flags: [],
        confidence: 0.5,
      },
    };
    render(<RecommendationCard recommendation={failing} onFeedback={vi.fn()} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Calories 900 outside target range");
  });
});
