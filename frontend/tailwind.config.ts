import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}', './lib/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        accent: '#0f172a',
        panel: '#111827',
        success: '#16a34a',
        warning: '#f59e0b',
        danger: '#dc2626',
      },
    },
  },
  plugins: [],
};

export default config;
