/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Primary Sinhala font
        sinhala: ['"Noto Sans Sinhala"', "sans-serif"],
        // Clean modern UI font
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Minimal color palette
        neutral: {
          50: "#fafafa",
          100: "#f5f5f5",
          200: "#e5e5e5",
          300: "#d4d4d4",
          400: "#a3a3a3",
          500: "#737373",
          600: "#525252",
          700: "#404040",
          800: "#262626",
          900: "#171717",
        },
        // Single accent color - subtle blue
        accent: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
        },
        // Semantic colors for dyslexia patterns
        akura: {
          error: {
            50: "#fef2f2",
            100: "#fee2e2",
            200: "#fecaca",
            500: "#ef4444",
            600: "#dc2626",
          },
          success: {
            50: "#f0fdf4",
            100: "#dcfce7",
            200: "#bbf7d0",
            500: "#22c55e",
            600: "#16a34a",
          },
          visual: {
            50: "#eff6ff",
            100: "#dbeafe",
            500: "#3b82f6",
          },
          phonetic: {
            50: "#fffbeb",
            100: "#fef3c7",
            500: "#f59e0b",
          },
          grammar: {
            50: "#faf5ff",
            100: "#f3e8ff",
            500: "#a855f7",
          },
          ignored: {
            50: "#f9fafb",
            100: "#f3f4f6",
            500: "#9ca3af",
          },
        },
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-up": "slideUp 0.2s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
