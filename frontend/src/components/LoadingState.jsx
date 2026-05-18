/**
 * Loading State Component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React from "react";
import {
  Box,
  Skeleton,
  Typography,
  Paper,
  CircularProgress,
} from "@mui/material";
import PropTypes from "prop-types";

const LoadingState = ({
  variant = "default",
  height = "auto",
  width = "100%",
  text = "Loading...",
  showText = true,
  skeletonCount = 3,
  animation = "pulse",
}) => {
  // Different loading state variants
  const renderVariant = () => {
    switch (variant) {
      case "text":
        return (
          <Box sx={{ width }}>
            {Array(skeletonCount)
              .fill(0)
              .map((_, i) => (
                <Skeleton
                  key={i}
                  animation={animation}
                  height={24}
                  sx={{ mb: 1 }}
                />
              ))}
          </Box>
        );

      case "card":
        return (
          <Paper
            variant="outlined"
            sx={{ p: 2, width, height: height !== "auto" ? height : 200 }}
          >
            <Skeleton
              animation={animation}
              height={24}
              width="60%"
              sx={{ mb: 2 }}
            />
            <Skeleton animation={animation} height={100} sx={{ mb: 1 }} />
            <Skeleton animation={animation} height={24} width="40%" />
          </Paper>
        );

      case "table":
        return (
          <Box sx={{ width }}>
            <Skeleton animation={animation} height={40} sx={{ mb: 1 }} />
            {Array(skeletonCount)
              .fill(0)
              .map((_, i) => (
                <Skeleton
                  key={i}
                  animation={animation}
                  height={48}
                  sx={{ mb: 0.5 }}
                />
              ))}
          </Box>
        );

      case "chart":
        return (
          <Box sx={{ width, height: height !== "auto" ? height : 200 }}>
            <Skeleton
              animation={animation}
              variant="rectangular"
              height="100%"
              sx={{ borderRadius: 1 }}
            />
          </Box>
        );

      case "spinner":
        return (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width,
              height: height !== "auto" ? height : 200,
            }}
          >
            <CircularProgress size={40} thickness={4} />
            {showText && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                {text}
              </Typography>
            )}
          </Box>
        );

      case "default":
      default:
        return (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width,
              height: height !== "auto" ? height : 100,
            }}
          >
            <CircularProgress size={24} thickness={4} />
            {showText && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 1 }}
              >
                {text}
              </Typography>
            )}
          </Box>
        );
    }
  };

  return renderVariant();
};

LoadingState.propTypes = {
  variant: PropTypes.oneOf([
    "default",
    "text",
    "card",
    "table",
    "chart",
    "spinner",
  ]),
  height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  width: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  text: PropTypes.string,
  showText: PropTypes.bool,
  skeletonCount: PropTypes.number,
  animation: PropTypes.oneOf(["pulse", "wave", false]),
};

export default LoadingState;
