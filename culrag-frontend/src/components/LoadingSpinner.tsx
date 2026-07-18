/** Spinner shown while a recommendation is being generated. */
export default function LoadingSpinner() {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 py-16"
      role="status"
      aria-live="polite"
    >
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-saffron border-t-transparent" />
      <p className="text-gray-600">Finding the perfect meal for you...</p>
    </div>
  );
}
