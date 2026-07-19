/**
 * Environment-based configuration.
 *
 * In development the API defaults to the local uvicorn server; in production
 * set VITE_API_BASE_URL (e.g. the Railway backend URL) at build time.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** Timeout for recommendation requests, in milliseconds. */
export const REQUEST_TIMEOUT_MS = 30_000;
