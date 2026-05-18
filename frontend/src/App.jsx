/**
 * Main App component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useState, useEffect } from "react";
import { createTheme, CssBaseline } from "@mui/material";
import ErrorBoundary from "./components/ErrorBoundary";
import AccessibleThemeProvider from "./components/AccessibleThemeProvider";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Playground from "./pages/Playground";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  useEffect(() => {
    // Simple client-side routing
    const path = window.location.pathname;
    if (path.includes("playground")) {
      setCurrentPage("playground");
    } else {
      setCurrentPage("dashboard");
    }

    // Listen for navigation events
    const handleNavigation = () => {
      const newPath = window.location.pathname;
      if (newPath.includes("playground")) {
        setCurrentPage("playground");
      } else {
        setCurrentPage("dashboard");
      }
    };

    window.addEventListener("popstate", handleNavigation);

    return () => {
      window.removeEventListener("popstate", handleNavigation);
    };
  }, []);

  // Handle internal navigation without full page reload
  const navigate = (path) => {
    window.history.pushState({}, "", path);
    if (path.includes("playground")) {
      setCurrentPage("playground");
    } else {
      setCurrentPage("dashboard");
    }
  };

  // Theme mode with persistence (localStorage takes precedence over system)
  const prefersDark =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initialMode =
    (typeof window !== "undefined" && localStorage.getItem("lpb.theme")) ||
    (prefersDark ? "dark" : "light");
  const [mode, setMode] = useState(initialMode);
  const [density, setDensity] = useState(
    (typeof window !== "undefined" && localStorage.getItem("lpb.density")) ||
      "comfortable"
  );
  const reducedMotion =
    (typeof window !== "undefined" &&
      localStorage.getItem("lpb.reducedMotion") === "true") ||
    (typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches);

  const theme = React.useMemo(
    () =>
      createTheme({
        typography: {
          fontFamily:
            "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif",
          h5: { fontWeight: 700 },
          body1: { lineHeight: 1.6 },
        },
        palette: {
          mode,
          ...(mode === "dark"
            ? {
                background: { default: "#121417", paper: "#181b20" },
                text: { primary: "#e8eaed", secondary: "#b6beca" },
                divider: "#2a2f36",
              }
            : {
                background: { default: "#f3f4f6", paper: "#ffffff" },
                text: { primary: "#111827", secondary: "#4b5563" },
                divider: "#e6e8ec",
              }),
          primary: { main: "#1E3A8A" },
          secondary: { main: "#06B6D4" },
        },
        components: {
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 14,
                border: "1px solid",
                borderColor: mode === "dark" ? "#2a2f36" : "#e6e8ec",
                backgroundImage: "none",
                backgroundColor: mode === "dark" ? "#181b20" : "#ffffff",
                transition: reducedMotion ? "none" : undefined,
              },
            },
            defaultProps: { elevation: 0 },
          },
          MuiButton: {
            defaultProps: {
              variant: "contained",
              color: "primary",
              size: density === "compact" ? "small" : "medium",
            },
            styleOverrides: {
              root: {
                textTransform: "none",
                borderRadius: 10,
                paddingInline: density === "compact" ? 12 : 16,
              },
            },
          },
          MuiContainer: {
            defaultProps: { maxWidth: "lg" },
          },
          MuiAppBar: {
            styleOverrides: {
              colorDefault: {
                backgroundColor: mode === "dark" ? "#111418" : "#f3f4f6",
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: "none",
                transition: reducedMotion ? "none" : undefined,
              },
            },
          },
          MuiDivider: {
            styleOverrides: {
              root: { borderColor: mode === "dark" ? "#2a2f36" : "#e6e8ec" },
            },
          },
          MuiTable: {
            defaultProps: { size: density === "compact" ? "small" : "medium" },
          },
          MuiTextField: {
            defaultProps: { size: density === "compact" ? "small" : "medium" },
          },
          MuiSelect: {
            defaultProps: { size: density === "compact" ? "small" : "medium" },
          },
        },
      }),
    [mode, density, reducedMotion]
  );

  return (
    <AccessibleThemeProvider
      theme={theme}
      wcagLevel={reducedMotion ? "large" : "normal"}
    >
      <CssBaseline />
      <ErrorBoundary>
        <Layout
          mode={mode}
          onToggleTheme={() => {
            setMode((m) => {
              const next = m === "dark" ? "light" : "dark";
              if (typeof window !== "undefined")
                localStorage.setItem("lpb.theme", next);
              return next;
            });
          }}
          density={density}
          setDensity={(d) => {
            setDensity(d);
            if (typeof window !== "undefined")
              localStorage.setItem("lpb.density", d);
          }}
          reducedMotion={reducedMotion}
          setReducedMotion={(v) => {
            if (typeof v === "boolean") {
              if (typeof window !== "undefined")
                localStorage.setItem("lpb.reducedMotion", String(v));
            }
          }}
        >
          {currentPage === "dashboard" && (
            <ErrorBoundary
              title="Dashboard Error"
              message="We encountered an error while loading the dashboard. Please try again."
            >
              <Dashboard />
            </ErrorBoundary>
          )}
          {currentPage === "playground" && (
            <ErrorBoundary
              title="Playground Error"
              message="We encountered an error while loading the playground. Please try again."
            >
              <Playground />
            </ErrorBoundary>
          )}
        </Layout>
      </ErrorBoundary>
    </AccessibleThemeProvider>
  );
}

export default App;
