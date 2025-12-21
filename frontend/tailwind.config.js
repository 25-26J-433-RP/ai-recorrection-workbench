/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Primary Sinhala font - clear character separation
        sinhala: ['"Noto Sans Sinhala"', "sans-serif"],
        // UI font for English text
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Custom semantic colors for dyslexia patterns
        akura: {
          // Error states
          error: {
            50: "#fef2f2",
            100: "#fee2e2",
            200: "#fecaca",
            500: "#ef4444",
            600: "#dc2626",
          },
          // Corrected states
          success: {
            50: "#f0fdf4",
            100: "#dcfce7",
            200: "#bbf7d0",
            500: "#22c55e",
            600: "#16a34a",
          },
          // Visual pattern (blue)
          visual: {
            50: "#eff6ff",
            100: "#dbeafe",
            500: "#3b82f6",
            600: "#2563eb",
          },
          // Phonetic pattern (amber)
          phonetic: {
            50: "#fffbeb",
            100: "#fef3c7",
            500: "#f59e0b",
            600: "#d97706",
          },
          // Grammar pattern (purple)
          grammar: {
            50: "#faf5ff",
            100: "#f3e8ff",
            500: "#a855f7",
            600: "#9333ea",
          },
          // Ignored state (gray)
          ignored: {
            50: "#f9fafb",
            100: "#f3f4f6",
            500: "#6b7280",
          },
        },
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-soft": "pulseSoft 2s infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
    },
  },
  plugins: [],
};
