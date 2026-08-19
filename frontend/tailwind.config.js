module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        accent: {
          violet: '#8b5cf6',
          indigo: '#6366f1',
          cyan:   '#06b6d4',
          pink:   '#ec4899',
        },
        dark: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          850: '#131929',
          900: '#0d0d24',
          950: '#0a0a1a',
        },
        secondary: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Space Grotesk', 'Inter', 'sans-serif'],
        mono:  ['Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-main':   'linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #06b6d4 100%)',
        'gradient-subtle': 'linear-gradient(135deg, rgba(139,92,246,0.15), rgba(99,102,241,0.15))',
      },
      animation: {
        'fade-in':      'fadeIn 0.6s ease-out both',
        'fade-in-up':   'fadeInUp 0.7s ease-out both',
        'slide-left':   'slideInLeft 0.5s ease-out both',
        'float':        'float 3s ease-in-out infinite',
        'pulse-glow':   'pulseGlow 2s ease-in-out infinite',
        'shimmer':      'shimmer 1.5s linear infinite',
        'spin-slow':    'spin 3s linear infinite',
        'typing':       'typing 1.2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInUp: {
          '0%':   { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%':   { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(139,92,246,0.3)' },
          '50%':      { boxShadow: '0 0 40px rgba(139,92,246,0.6)' },
        },
        shimmer: {
          'from': { backgroundPosition: '-200% 0' },
          'to':   { backgroundPosition:  '200% 0' },
        },
        typing: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.3' },
        },
      },
      boxShadow: {
        'glow-violet': '0 0 30px rgba(139, 92, 246, 0.4)',
        'glow-cyan':   '0 0 30px rgba(6, 182, 212, 0.4)',
        'glass':       '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
        'card-hover':  '0 16px 48px rgba(0,0,0,0.5)',
      },
      borderRadius: {
        'xl2': '16px',
        'xl3': '20px',
      },
      backdropBlur: {
        xs: '4px',
      },
    },
  },
  plugins: [],
};
