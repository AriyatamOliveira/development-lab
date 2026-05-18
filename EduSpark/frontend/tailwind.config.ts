import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#ffffff",
        foreground: "#000000",
      },
      fontFamily: {
        mono: [
          'SF Mono',
          'Cascadia Code',
          'Fira Code',
          'Consolas',
          'ui-monospace',
          'monospace'
        ]
      },
    },
  },
  plugins: [],
};
export default config;
