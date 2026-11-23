/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          teal: "#00685f",
          deep: "#00554e",
          purple: "#8b12c6",
          violet: "#6b0fa8",
          gold: "#ffb000",
          coral: "#f45b69",
          green: "#10b981",
          ink: "#101a42"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Poppins", "Inter", "sans-serif"]
      },
      boxShadow: {
        soft: "0 8px 30px rgba(24, 32, 65, .07)"
      }
    }
  },
  plugins: []
};
