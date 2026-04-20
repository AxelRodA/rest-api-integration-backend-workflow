/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        panel: "#101b2d",
        line: "#25324a",
        mint: "#37d7a4",
        amber: "#f4b860",
        coral: "#ff6b6b"
      },
      boxShadow: {
        glow: "0 20px 80px rgba(55, 215, 164, 0.12)"
      }
    }
  },
  plugins: []
};
