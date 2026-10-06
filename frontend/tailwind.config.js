/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
      colors: {
        graph: {
          repo: "#f59e0b",     // Yellow/Amber strictly for Repository nodes in graph & legends
          pkg: "#10b981",      // Emerald for Package nodes
          cve: "#f43f5e",      // Crimson for CVE nodes
        }
      }
    },
  },
  plugins: [],
}
