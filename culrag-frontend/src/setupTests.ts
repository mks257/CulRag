import "@testing-library/jest-dom";

// Recharts' ResponsiveContainer needs a real layout engine; jsdom has none,
// so stub ResizeObserver to keep chart components renderable in tests.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver;
}
