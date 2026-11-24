import React from "react";
import ReactDOM from "react-dom/client";
import { registerSW } from "virtual:pwa-register";
import AppRouter from "./app/router";
import AppProviders from "./app/providers/AppProviders";
import "./styles/styles.css";

registerSW({ immediate: true });
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppProviders>
      <AppRouter />
    </AppProviders>
  </React.StrictMode>,
);
