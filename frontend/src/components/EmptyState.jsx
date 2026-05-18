/**
 * Empty State Component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React from "react";
import { Box, Typography, Button, Paper } from "@mui/material";
import PropTypes from "prop-types";

const EmptyState = ({
  title = "No data available",
  message = "There's nothing to display here yet.",
  icon = null,
  actionText = "",
  onAction = null,
  variant = "default",
  height = "auto",
  width = "100%",
}) => {
  // Different empty state variants
  const renderVariant = () => {
    const baseStyles = {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      textAlign: "center",
      padding: 3,
      width,
      height: height !== "auto" ? height : 200,
    };

    switch (variant) {
      case "card":
        return (
          <Paper
            variant="outlined"
            sx={{
              ...baseStyles,
              bgcolor: (theme) =>
                theme.palette.mode === "dark" ? "background.paper" : "#fafafa",
            }}
          >
            {renderContent()}
          </Paper>
        );

      case "subtle":
        return (
          <Box
            sx={{
              ...baseStyles,
              bgcolor: "transparent",
            }}
          >
            {renderContent()}
          </Box>
        );

      case "default":
      default:
        return <Box sx={baseStyles}>{renderContent()}</Box>;
    }
  };

  // Content to show inside the empty state container
  const renderContent = () => (
    <>
      {icon && <Box sx={{ mb: 2, color: "text.secondary" }}>{icon}</Box>}

      <Typography variant="h6" color="text.primary" gutterBottom>
        {title}
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {message}
      </Typography>

      {actionText && onAction && (
        <Button
          variant="outlined"
          color="primary"
          onClick={onAction}
          size="small"
        >
          {actionText}
        </Button>
      )}
    </>
  );

  return renderVariant();
};

EmptyState.propTypes = {
  title: PropTypes.string,
  message: PropTypes.string,
  icon: PropTypes.node,
  actionText: PropTypes.string,
  onAction: PropTypes.func,
  variant: PropTypes.oneOf(["default", "card", "subtle"]),
  height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  width: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};

export default EmptyState;
