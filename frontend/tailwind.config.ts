import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'ic-page':         'var(--ic-page)',
        'ic-surface':      'var(--ic-surface)',
        'ic-surface-mid':  'var(--ic-surface-mid)',
        'ic-border':       'var(--ic-border)',
        'ic-accent':       'var(--ic-accent)',
        'ic-accent-light': 'var(--ic-accent-light)',
        'ic-tan':          'var(--ic-tan)',
        'ic-text':         'var(--ic-text)',
        'ic-muted':        'var(--ic-muted)',
        'ic-positive':     'var(--ic-positive)',
        'ic-warning':      'var(--ic-warning)',
        'ic-negative':     'var(--ic-negative)',
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        sans: ['DM Sans', 'sans-serif'],
        mono: ['DM Mono', 'monospace'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

export default config;
