/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'emerald': {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669',
          700: '#047857'
        }
      }
    },
  },
  plugins: [],
};
