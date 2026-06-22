/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // KINZ brand palette — warm Tunisian desert + olive accent
        kinz: {
          50:  '#fbf7f0',
          100: '#f3e9d6',
          200: '#e2c79a',
          300: '#cba163',
          400: '#b07f3a',
          500: '#8a5e21',
          600: '#6a4818',
          700: '#4f3612',
          800: '#33240c',
          900: '#1c1407',
        },
        olive: '#0f766e',
        amber: '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
    },
  },
  plugins: [],
};
