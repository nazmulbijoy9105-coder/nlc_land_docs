/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#1a2744",
          50: "#eef1f8",
          100: "#d5dced",
          200: "#aab9db",
          300: "#7e96c9",
          400: "#5273b7",
          500: "#3558a3",
          600: "#2a4586",
          700: "#1a2744",
          800: "#111b30",
          900: "#080e1a",
        },
        gold: {
          DEFAULT: "#c9a84c",
          50: "#fdf8ec",
          100: "#f9edca",
          200: "#f3db95",
          300: "#ecc860",
          400: "#e3b430",
          500: "#c9a84c",
          600: "#a88733",
          700: "#84661f",
          800: "#5e4712",
          900: "#3a2b08",
        },
        pearl: "#f8f6f0",
        cream: "#fefcf8",
      },
      fontFamily: {
        display: ["'Playfair Display'", "Georgia", "serif"],
        body: ["'DM Sans'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(26,39,68,0.08), 0 4px 16px 0 rgba(26,39,68,0.04)",
        "card-hover": "0 4px 12px 0 rgba(26,39,68,0.12), 0 12px 32px 0 rgba(26,39,68,0.08)",
        "gold-glow": "0 0 20px rgba(201,168,76,0.25)",
      },
      backgroundImage: {
        "hero-pattern": "radial-gradient(ellipse at 20% 50%, rgba(201,168,76,0.06) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(26,39,68,0.04) 0%, transparent 50%)",
      },
    },
  },
  plugins: [],
};
