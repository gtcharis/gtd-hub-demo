import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  base: "/gtd-hub-demo/",
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/gtdhub-icon.svg"],
      manifest: {
        name: "GTD Hub — Gender-Transformative Digital Hub",
        short_name: "GTD Hub",
        description: "A safe, inclusive space for support, mentorship, learning and action.",
        theme_color: "#6b0fa8",
        background_color: "#ffffff",
        display: "standalone",
        orientation: "portrait-primary",
        start_url: "/gtd-hub-demo/",
        scope: "/gtd-hub-demo/",
        icons: [
          { src: "./icons/gtdhub-icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any maskable" }
        ]
      },
      workbox: {
        navigateFallback: "index.html",
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        runtimeCaching: [
          {
            urlPattern: /\/api\//,
            handler: "NetworkOnly"
          }
        ]
      },
      devOptions: { enabled: false }
    })
  ],
  server: { host: "0.0.0.0" }
});
