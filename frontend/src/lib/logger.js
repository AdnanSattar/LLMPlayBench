/**
 * Logger service for frontend
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import log from "loglevel";
import apiClient from "./api";

// Configure log level based on environment
const LOG_LEVEL = import.meta.env.VITE_LOG_LEVEL || "info";

// Initialize logger
log.setLevel(LOG_LEVEL);

// Enable remote logging in production
const isProduction = import.meta.env.PROD;
const REMOTE_LOGGING_ENABLED =
  import.meta.env.VITE_REMOTE_LOGGING_ENABLED === "true";

// Add timestamp to logs
const originalFactory = log.methodFactory;
log.methodFactory = function (methodName, logLevel, loggerName) {
  const rawMethod = originalFactory(methodName, logLevel, loggerName);

  return function (message, ...args) {
    const timestamp = new Date().toISOString();
    let formattedMessage = `[${timestamp}] ${message}`;

    // For objects, stringify them for better visibility
    if (typeof message === "object" && message !== null) {
      formattedMessage = `[${timestamp}] ${JSON.stringify(message)}`;
    }

    rawMethod(formattedMessage, ...args);
  };
};

// Apply method factory
log.setLevel(log.getLevel());

// Remote logging function
async function sendToRemoteLogger(level, message, meta = {}) {
  if (isProduction && REMOTE_LOGGING_ENABLED) {
    try {
      await apiClient.post("/v1/clientlogs", {
        level,
        message,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        ...meta,
      });
    } catch (error) {
      // Avoid infinite loops by not logging this error
      console.error("Failed to send log to remote server:", error);
    }
  }
}

// Enhanced logger with remote capabilities
const logger = {
  trace: (message, meta = {}) => {
    log.trace(message);
    sendToRemoteLogger("trace", message, meta);
  },
  debug: (message, meta = {}) => {
    log.debug(message);
    sendToRemoteLogger("debug", message, meta);
  },
  info: (message, meta = {}) => {
    log.info(message);
    sendToRemoteLogger("info", message, meta);
  },
  warn: (message, meta = {}) => {
    log.warn(message);
    sendToRemoteLogger("warn", message, meta);
  },
  error: (message, meta = {}) => {
    log.error(message);
    sendToRemoteLogger("error", message, meta);
  },
  // Capture unhandled errors and rejections
  enableGlobalErrorLogging: () => {
    window.addEventListener("error", (event) => {
      const { message, filename, lineno, colno, error } = event;
      logger.error("Unhandled error", {
        message,
        source: filename,
        line: lineno,
        column: colno,
        stack: error?.stack,
      });
    });

    window.addEventListener("unhandledrejection", (event) => {
      logger.error("Unhandled promise rejection", {
        reason: event.reason?.message || event.reason,
        stack: event.reason?.stack,
      });
    });

    logger.info("Global error logging enabled");
  },
};

export default logger;
