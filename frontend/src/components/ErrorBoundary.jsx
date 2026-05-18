/**
 * Error Boundary Component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React from "react";
import { Box, Typography, Button, Paper } from "@mui/material";
import logger from "../lib/logger";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render shows the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to our logging service
    logger.error("Error caught by ErrorBoundary", {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
    });

    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });

    // If a reset handler was provided, call it
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI when an error occurs
      return (
        <Paper
          elevation={0}
          variant="outlined"
          sx={{
            p: 3,
            borderRadius: 2,
            bgcolor: (theme) =>
              theme.palette.mode === "dark"
                ? "rgba(255, 0, 0, 0.05)"
                : "rgba(255, 0, 0, 0.02)",
            borderColor: "error.light",
          }}
        >
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" color="error" gutterBottom>
              {this.props.title || "Something went wrong"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {this.props.message ||
                "We encountered an error while rendering this component. Try refreshing the page or contact support if the issue persists."}
            </Typography>
          </Box>

          {this.props.showDetails && this.state.error && (
            <Box
              sx={{
                my: 2,
                p: 2,
                bgcolor: (theme) =>
                  theme.palette.mode === "dark" ? "grey.900" : "grey.100",
                borderRadius: 1,
                overflowX: "auto",
              }}
            >
              <Typography
                variant="caption"
                component="pre"
                sx={{
                  fontFamily: "monospace",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </Typography>
            </Box>
          )}

          <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={this.handleReset}
              size="small"
            >
              {this.props.resetButtonText || "Try Again"}
            </Button>

            <Button
              variant="text"
              color="inherit"
              onClick={() => window.location.reload()}
              size="small"
            >
              Refresh Page
            </Button>
          </Box>
        </Paper>
      );
    }

    // When there's no error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;
