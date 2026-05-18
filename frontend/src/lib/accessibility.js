/**
 * Accessibility utilities
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

/**
 * Calculate the relative luminance of an RGB color
 * Formula from WCAG 2.0: https://www.w3.org/TR/WCAG20/#relativeluminancedef
 *
 * @param {number} r - Red channel (0-255)
 * @param {number} g - Green channel (0-255)
 * @param {number} b - Blue channel (0-255)
 * @returns {number} - Relative luminance value between 0 and 1
 */
export const getLuminance = (r, g, b) => {
  // Convert RGB values to sRGB
  const sR = r / 255;
  const sG = g / 255;
  const sB = b / 255;

  // Calculate RGB values
  const R = sR <= 0.03928 ? sR / 12.92 : Math.pow((sR + 0.055) / 1.055, 2.4);
  const G = sG <= 0.03928 ? sG / 12.92 : Math.pow((sG + 0.055) / 1.055, 2.4);
  const B = sB <= 0.03928 ? sB / 12.92 : Math.pow((sB + 0.055) / 1.055, 2.4);

  // Calculate luminance
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
};

/**
 * Parse a color string (hex or rgba) into RGB components
 *
 * @param {string} color - Color string (e.g., "#FFFFFF", "#FFF", or "rgba(0, 0, 0, 0.87)")
 * @returns {Object} - Object containing r, g, b values (0-255)
 */
export const hexToRgb = (color) => {
  // Check if it's an rgba color
  const rgbaMatch = color.match(
    /rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)/
  );
  if (rgbaMatch) {
    return {
      r: parseInt(rgbaMatch[1], 10),
      g: parseInt(rgbaMatch[2], 10),
      b: parseInt(rgbaMatch[3], 10),
    };
  }

  // Handle hex colors
  // Remove # if present
  const hex = color.replace(/^#/, "");

  // Parse hex values
  let r, g, b;
  if (hex.length === 3) {
    // Short notation (#RGB)
    r = parseInt(hex[0] + hex[0], 16);
    g = parseInt(hex[1] + hex[1], 16);
    b = parseInt(hex[2] + hex[2], 16);
  } else if (hex.length === 6) {
    // Long notation (#RRGGBB)
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  } else {
    throw new Error(`Invalid color format: ${color}`);
  }

  return { r, g, b };
};

/**
 * Calculate contrast ratio between two colors
 * Formula from WCAG 2.0: https://www.w3.org/TR/WCAG20/#contrast-ratiodef
 *
 * @param {string} color1 - First color in hex or rgba format
 * @param {string} color2 - Second color in hex or rgba format
 * @returns {number} - Contrast ratio between 1 and 21
 */
export const getContrastRatio = (color1, color2) => {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  const luminance1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const luminance2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

  // Determine lighter and darker luminance
  const lighter = Math.max(luminance1, luminance2);
  const darker = Math.min(luminance1, luminance2);

  // Calculate contrast ratio
  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Check if a color combination meets WCAG AA contrast requirements
 *
 * @param {string} foreground - Foreground color in hex or rgba format
 * @param {string} background - Background color in hex or rgba format
 * @param {string} level - 'normal' for normal text, 'large' for large text
 * @returns {boolean} - Whether the combination meets WCAG AA requirements
 */
export const meetsWcagAA = (foreground, background, level = "normal") => {
  const ratio = getContrastRatio(foreground, background);

  // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
  return level === "large" ? ratio >= 3 : ratio >= 4.5;
};

/**
 * Adjust a color to meet WCAG AA contrast requirements
 *
 * @param {string} foreground - Foreground color in hex or rgba format
 * @param {string} background - Background color in hex or rgba format
 * @param {string} level - 'normal' for normal text, 'large' for large text
 * @returns {string} - Adjusted foreground color that meets requirements
 */
export const adjustColorForContrast = (
  foreground,
  background,
  level = "normal"
) => {
  // If already meets requirements, return as is
  if (meetsWcagAA(foreground, background, level)) {
    return foreground;
  }

  // Parse colors
  const fgRgb = hexToRgb(foreground);
  const bgRgb = hexToRgb(background);

  // Determine if we need to lighten or darken
  const fgLuminance = getLuminance(fgRgb.r, fgRgb.g, fgRgb.b);
  const bgLuminance = getLuminance(bgRgb.r, bgRgb.g, bgRgb.b);

  const shouldLighten = fgLuminance <= bgLuminance;

  // Adjust color incrementally until it meets requirements
  let adjustedR = fgRgb.r;
  let adjustedG = fgRgb.g;
  let adjustedB = fgRgb.b;

  const step = shouldLighten ? 5 : -5;
  let iterations = 0;
  const maxIterations = 50; // Safety limit

  while (
    !meetsWcagAA(
      rgbToHex(adjustedR, adjustedG, adjustedB),
      background,
      level
    ) &&
    iterations < maxIterations
  ) {
    // Adjust RGB values
    adjustedR = Math.max(0, Math.min(255, adjustedR + step));
    adjustedG = Math.max(0, Math.min(255, adjustedG + step));
    adjustedB = Math.max(0, Math.min(255, adjustedB + step));

    iterations++;
  }

  return rgbToHex(adjustedR, adjustedG, adjustedB);
};

/**
 * Convert RGB values to hex color string
 *
 * @param {number} r - Red channel (0-255)
 * @param {number} g - Green channel (0-255)
 * @param {number} b - Blue channel (0-255)
 * @returns {string} - Hex color string (e.g., "#FFFFFF")
 */
export const rgbToHex = (r, g, b) => {
  return `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`;
};

/**
 * Convert a single RGB component to hex
 *
 * @param {number} c - RGB component (0-255)
 * @returns {string} - Two-character hex string
 */
const componentToHex = (c) => {
  const hex = Math.max(0, Math.min(255, Math.round(c))).toString(16);
  return hex.length === 1 ? `0${hex}` : hex;
};
