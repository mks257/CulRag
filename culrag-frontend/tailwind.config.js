/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        saffron: "#FF9933",
        healthgreen: "#138808",
        accent: "#4F46E5",
      },
      keyframes: {
        "slide-in": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "slide-in": "slide-in 0.4s ease-out",
      },
    },
  },
  plugins: [],
};
