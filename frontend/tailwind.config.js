/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Primary Sinhala font - clear character separation
        sinhala: ['"Noto Sans Sinhala"', "sans-serif"],
        // UI font - child-friendly rounded font
        sans: ["Nunito", "Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Child-friendly green theme
        primary: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
        },
        // Accent colors for variety
        accent: {
          yellow: "#fbbf24",
          orange: "#fb923c",
          pink: "#f472b6",
          blue: "#60a5fa",
          purple: "#a78bfa",
        },
        // Custom semantic colors for dyslexia patterns
        akura: {
          // Error states - softer red
          error: {
            50: "#fef2f2",
            100: "#fee2e2",
            200: "#fecaca",
            500: "#f87171",
            600: "#ef4444",
          },
          // Corrected states - bright green
          success: {
            50: "#ecfdf5",
            100: "#d1fae5",
            200: "#a7f3d0",
            500: "#10b981",
            600: "#059669",
          },
          // Visual pattern (blue)
          visual: {
            50: "#eff6ff",
            100: "#dbeafe",
            500: "#60a5fa",
            600: "#3b82f6",
          },
          // Phonetic pattern (amber)
          phonetic: {
            50: "#fffbeb",
            100: "#fef3c7",
            500: "#fbbf24",
            600: "#f59e0b",
          },
          // Grammar pattern (purple)
          grammar: {
            50: "#faf5ff",
            100: "#f3e8ff",
            500: "#a78bfa",
            600: "#8b5cf6",
          },
          // Ignored state (gray)
          ignored: {
            50: "#f9fafb",
            100: "#f3f4f6",
            500: "#9ca3af",
          },
        },
      },
      borderRadius: {
        'blob': '60% 40% 30% 70% / 60% 30% 70% 40%',
        '4xl': '2rem',
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-soft": "pulseSoft 2s infinite",
        "bounce-soft": "bounceSoft 2s infinite",
        "blob": "blob 7s infinite",
        "float": "float 6s ease-in-out infinite",
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
        bounceSoft: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-5px)" },
        },
        blob: {
          "0%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(30px, -50px) scale(1.1)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.9)" },
          "100%": { transform: "translate(0px, 0px) scale(1)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
    },
  },
  plugins: [],
};
