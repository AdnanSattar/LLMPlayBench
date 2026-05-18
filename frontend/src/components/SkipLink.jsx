/**
 * Skip Link Component for Keyboard Navigation
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React from "react";
import { styled } from "@mui/material/styles";

const StyledSkipLink = styled("a")(({ theme }) => ({
  position: "absolute",
  top: "-40px",
  left: 0,
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: theme.spacing(1, 2),
  zIndex: 9999,
  transition: "top 0.2s",
  textDecoration: "none",
  fontWeight: 500,
  borderRadius: "0 0 4px 0",
  "&:focus": {
    top: 0,
  },
}));

const SkipLink = ({ targetId, children = "Skip to content" }) => {
  return (
    <StyledSkipLink href={`#${targetId}`} className="skip-link">
      {children}
    </StyledSkipLink>
  );
};

export default SkipLink;
