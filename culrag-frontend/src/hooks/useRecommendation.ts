import { useCallback, useRef, useState } from "react";
import axios, { AxiosError } from "axios";
import { API_BASE_URL, REQUEST_TIMEOUT_MS } from "../config";
import type {
  FeedbackRequest,
  RecommendationRequest,
  RecommendationResponse,
} from "../types";

interface UseRecommendationResult {
  recommendation: RecommendationResponse | null;
  loading: boolean;
  error: string | null;
  fetchRecommendation: (request: RecommendationRequest) => Promise<void>;
  sendFeedback: (feedback: FeedbackRequest) => Promise<boolean>;
}

const MAX_RETRIES = 1;

function errorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const axiosErr = err as AxiosError<{ detail?: string }>;
    if (axiosErr.response?.data?.detail) return String(axiosErr.response.data.detail);
    if (axiosErr.code === "ECONNABORTED") return "The request timed out. Please try again.";
    if (!axiosErr.response) return "Cannot reach the CulRAG API. Is the backend running?";
    return `Request failed (${axiosErr.response.status}).`;
  }
  return "Something went wrong. Please try again.";
}

/**
 * Manages recommendation fetching and feedback submission against the
 * CulRAG API, with loading/error state, an in-flight guard (prevents
 * double-submits), and a single automatic retry on network failure.
 */
export function useRecommendation(): UseRecommendationResult {
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inFlight = useRef(false);

  const fetchRecommendation = useCallback(async (request: RecommendationRequest) => {
    if (inFlight.current) return;
    inFlight.current = true;
    setLoading(true);
    setError(null);

    let lastError: unknown = null;
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        const response = await axios.post<RecommendationResponse>(
          `${API_BASE_URL}/api/recommend`,
          request,
          { timeout: REQUEST_TIMEOUT_MS },
        );
        setRecommendation(response.data);
        lastError = null;
        break;
      } catch (err) {
        lastError = err;
        // Retry only on network-level failures, not 4xx/5xx responses.
        if (axios.isAxiosError(err) && err.response) break;
      }
    }

    if (lastError !== null) {
      setRecommendation(null);
      setError(errorMessage(lastError));
    }
    setLoading(false);
    inFlight.current = false;
  }, []);

  const sendFeedback = useCallback(async (feedback: FeedbackRequest): Promise<boolean> => {
    try {
      await axios.post(`${API_BASE_URL}/api/feedback`, feedback, {
        timeout: REQUEST_TIMEOUT_MS,
      });
      return true;
    } catch {
      return false;
    }
  }, []);

  return { recommendation, loading, error, fetchRecommendation, sendFeedback };
}
