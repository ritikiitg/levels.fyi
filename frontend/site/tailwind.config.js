/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Google Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        paper: { DEFAULT: '#FFFFFF', soft: '#F8F9FA', mid: '#F1F3F4' },
        ink:   { 950: '#121317', 700: '#3C4043', 500: '#5F6368', 300: '#9AA0A6', 100: '#E8EAED' },
        gbg:   { DEFAULT: '#1A73E8', hover: '#1557B0' },
        gred:  '#EA4335',
        gyel:  '#FBBC04',
        ggrn:  '#34A853',
        brand: { DEFAULT: '#1A73E8', dark: '#121317' },
      },
    },
  },
  plugins: [],
};
