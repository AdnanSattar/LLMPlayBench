/**
 * Main entry point
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/index.css";
import logger from "./lib/logger";

// Enable global error logging
logger.enableGlobalErrorLogging();

// Log application startup
logger.info("Application starting", {
  version: "1.0.0",
  environment: import.meta.env.MODE,
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
