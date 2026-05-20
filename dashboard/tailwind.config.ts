import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        graphite: "#0B0F14",
        midnight: "#101722",
        panel: "#161D27",
        panel2: "#1C2430",
        steel: "#232D3A",
        control: "#2C3745",
        control2: "#3E4A5A",
        silver: "#D7DCE3",
        muted: "#9DA8B5",
        accent: "#7E8FA8",
        success: "#5FAE7B",
        warning: "#D0A25A",
        critical: "#C96B6B"
      },
      boxShadow: {
        panel: "0 18px 60px rgba(0,0,0,.36), inset 0 1px 0 rgba(255,255,255,.05)",
        control: "0 14px 22px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.12)",
        press: "inset 0 4px 9px rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.04)"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Arial"]
      }
    }
  },
  plugins: []
};

export default config;
