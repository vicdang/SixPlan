import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          base: '#09090b',
          raised: '#18181b',
          overlay: '#27272a',
          border: '#3f3f46',
          muted: '#52525b',
        },
        text: {
          primary: '#fafafa',
          secondary: '#a1a1aa',
          muted: '#71717a',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          muted: '#312e81',
          foreground: '#ffffff',
        },
        status: {
          available: '#22c55e',
          occupied: '#ef4444',
          reserved: '#f59e0b',
          disabled: '#52525b',
          maintenance: '#f97316',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config
