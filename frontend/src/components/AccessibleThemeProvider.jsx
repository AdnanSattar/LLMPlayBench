/**
 * Accessible Theme Provider Component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useMemo } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { meetsWcagAA, adjustColorForContrast } from "../lib/accessibility";

// Helper function to ensure a color meets WCAG AA contrast requirements
const ensureWcagContrast = (color, background, level = "normal") => {
  // Skip non-string color values or empty values
  if (
    typeof color !== "string" ||
    !color ||
    typeof background !== "string" ||
    !background
  ) {
    return color;
  }

  try {
    if (!meetsWcagAA(color, background, level)) {
      return adjustColorForContrast(color, background, level);
    }
    return color;
  } catch (error) {
    console.warn(`Error checking contrast: ${error.message}`, {
      color,
      background,
    });
    return color; // Return original color if there's an error
  }
};

const AccessibleThemeProvider = ({ children, theme, wcagLevel = "normal" }) => {
  // Create an accessible version of the theme
  const accessibleTheme = useMemo(() => {
    if (!theme) return null;

    // Clone the theme to avoid mutating the original
    const newTheme = createTheme({ ...theme });

    // Check and adjust text colors against their backgrounds
    if (newTheme.palette) {
      const { palette } = newTheme;

      // Primary text against paper background
      if (palette.text?.primary && palette.background?.paper) {
        palette.text.primary = ensureWcagContrast(
          palette.text.primary,
          palette.background.paper,
          wcagLevel
        );
      }

      // Secondary text against paper background
      if (palette.text?.secondary && palette.background?.paper) {
        palette.text.secondary = ensureWcagContrast(
          palette.text.secondary,
          palette.background.paper,
          wcagLevel
        );
      }

      // Primary text against default background
      if (palette.text?.primary && palette.background?.default) {
        palette.text.primary = ensureWcagContrast(
          palette.text.primary,
          palette.background.default,
          wcagLevel
        );
      }

      // Secondary text against default background
      if (palette.text?.secondary && palette.background?.default) {
        palette.text.secondary = ensureWcagContrast(
          palette.text.secondary,
          palette.background.default,
          wcagLevel
        );
      }

      // Primary button text against primary button background
      if (palette.primary?.contrastText && palette.primary?.main) {
        palette.primary.contrastText = ensureWcagContrast(
          palette.primary.contrastText,
          palette.primary.main,
          wcagLevel
        );
      }

      // Secondary button text against secondary button background
      if (palette.secondary?.contrastText && palette.secondary?.main) {
        palette.secondary.contrastText = ensureWcagContrast(
          palette.secondary.contrastText,
          palette.secondary.main,
          wcagLevel
        );
      }

      // Error text against paper background
      if (palette.error?.main && palette.background?.paper) {
        palette.error.main = ensureWcagContrast(
          palette.error.main,
          palette.background.paper,
          wcagLevel
        );
      }
    }

    return newTheme;
  }, [theme, wcagLevel]);

  // If theme is not ready yet, render nothing
  if (!accessibleTheme) {
    return null;
  }

  return <ThemeProvider theme={accessibleTheme}>{children}</ThemeProvider>;
};

export default AccessibleThemeProvider;
