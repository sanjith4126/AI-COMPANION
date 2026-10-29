/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        companion: {
          bg: '#0B0F19',
          surface: '#1A2234',
          accent: '#7C3AED',
          accentLight: '#9333EA',
          text: '#F3F4F6',
          textSubtle: '#9CA3AF'
        }
      },
      animation: {
        'orb-idle': 'orb-pulse 4s ease-in-out infinite',
        'orb-listen': 'orb-ripple 1.5s cubic-bezier(0, 0.2, 0.8, 1) infinite',
        'orb-speak': 'orb-bounce 0.8s ease-in-out infinite alternate',
      },
      keyframes: {
        'orb-pulse': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8', boxShadow: '0 0 20px #7C3AED' },
          '50%': { transform: 'scale(1.05)', opacity: '1', boxShadow: '0 0 40px #9333EA' },
        },
        'orb-ripple': {
          '0%': { transform: 'scale(0.8)', opacity: '1', boxShadow: '0 0 0 0 rgba(124, 58, 237, 0.7)' },
          '100%': { transform: 'scale(1.4)', opacity: '0', boxShadow: '0 0 0 30px rgba(124, 58, 237, 0)' },
        },
        'orb-bounce': {
          '0%': { transform: 'scale(0.95)', boxShadow: '0 0 15px #7C3AED' },
          '100%': { transform: 'scale(1.15)', boxShadow: '0 0 35px #9333EA, 0 0 60px #7C3AED' },
        }
      }
    },
  },
  plugins: [],
}
