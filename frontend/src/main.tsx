import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "./app/App";
import { AppThemeProvider } from "./app/theme";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppThemeProvider>
      <App />
    </AppThemeProvider>
  </React.StrictMode>,
);
