/**
 * Layout component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useEffect, useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Container,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Stack,
  Alert,
} from "@mui/material";
import Snackbar from "@mui/material/Snackbar";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Switch from "@mui/material/Switch";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import { healthCheck } from "../lib/api";
import SkipLink from "./SkipLink";
import "../styles/accessibility.css";

function Layout({
  children,
  mode = "light",
  onToggleTheme,
  density = "comfortable",
  setDensity,
  reducedMotion = false,
  setReducedMotion,
}) {
  const [isDark, setIsDark] = useState(mode === "dark");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [apiBaseUrl, setApiBaseUrl] = useState(
    typeof window !== "undefined"
      ? localStorage.getItem("lpb.apiBaseUrl") || ""
      : ""
  );
  const [apiKey, setApiKey] = useState(
    typeof window !== "undefined"
      ? localStorage.getItem("lpb.apiKey") || ""
      : ""
  );
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [health, setHealth] = useState("unknown");
  const [healthToast, setHealthToast] = useState({
    open: false,
    message: "",
    severity: "error",
  });

  useEffect(() => {
    let t = null;
    let lastHealthState = health;

    const poll = async () => {
      const ok = await healthCheck();
      const newState = ok ? "ok" : "down";
      setHealth(newState);

      // Show toast only when health changes from ok to down
      if (lastHealthState === "ok" && newState === "down") {
        setHealthToast({
          open: true,
          message: "Backend is unreachable. Check server status or connection.",
          severity: "error",
        });
      }

      lastHealthState = newState;
    };

    poll();
    t = setInterval(poll, 15000);
    return () => t && clearInterval(t);
  }, []);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    setIsDark(mq.matches);
    const handler = (e) => setIsDark(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
  };
  return (
    <Box
      sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}
      className={reducedMotion ? "reduced-motion" : ""}
    >
      <SkipLink targetId="main-content" />
      <AppBar
        position="sticky"
        color="default"
        elevation={0}
        sx={{ borderBottom: 1, borderColor: "divider" }}
      >
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ color: "primary.main" }}
          >
            LLMPlayBench
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                bgcolor:
                  health === "ok"
                    ? "#22c55e"
                    : health === "down"
                    ? "#ef4444"
                    : "#f59e0b",
              }}
              title={`Health: ${health}`}
            />
            <Button href="/" size="small">
              Dashboard
            </Button>
            <Button href="/playground" size="small">
              Playground
            </Button>
            <Button
              href="https://github.com/AdnanSattar/LLMPlayBench"
              target="_blank"
              rel="noopener noreferrer"
              size="small"
            >
              GitHub
            </Button>
            <IconButton
              aria-label="Settings"
              onClick={() => setSettingsOpen(true)}
            >
              <span role="img" aria-label="gear">
                ⚙️
              </span>
            </IconButton>
            <Button
              onClick={() => {
                toggleTheme();
                if (onToggleTheme) onToggleTheme();
              }}
              size="small"
              variant="contained"
              startIcon={isDark ? <Brightness7Icon /> : <Brightness4Icon />}
            >
              {isDark ? "Light" : "Dark"}
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container
        component="main"
        id="main-content"
        sx={{ flex: 1, py: 3 }}
        tabIndex="-1"
      >
        {children}
      </Container>

      <Box
        component="footer"
        sx={{ borderTop: 1, borderColor: "divider", py: 2 }}
      >
        <Container>
          <Typography variant="body2" align="center" color="text.secondary">
            LLMPlayBench — Self-Hosted LLM Inference API + Benchmark Dashboard
          </Typography>
          <Typography
            variant="caption"
            align="center"
            display="block"
            color="text.secondary"
            sx={{ mt: 0.5 }}
          >
            Created by <a href="https://github.com/AdnanSattar">Adnan Sattar</a>
          </Typography>
        </Container>
      </Box>

      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="info">
              Settings are stored locally in this browser.
            </Alert>
            <TextField
              label="API Base URL"
              placeholder="http://localhost:8000"
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              helperText="Backend URL for API calls"
              fullWidth
            />
            <TextField
              label="API Key"
              placeholder="read-dev-key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              helperText="Sent as X-API-Key header"
              fullWidth
            />
            <FormControl size="small">
              <InputLabel id="density-label">Density</InputLabel>
              <Select
                labelId="density-label"
                label="Density"
                value={density}
                onChange={(e) => setDensity && setDensity(e.target.value)}
              >
                <MenuItem value="comfortable">Comfortable</MenuItem>
                <MenuItem value="compact">Compact</MenuItem>
              </Select>
            </FormControl>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Switch
                checked={Boolean(reducedMotion)}
                onChange={(e) =>
                  setReducedMotion && setReducedMotion(e.target.checked)
                }
              />
              <Typography variant="body2">Reduced motion</Typography>
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (typeof window !== "undefined") {
                if (apiBaseUrl)
                  localStorage.setItem("lpb.apiBaseUrl", apiBaseUrl);
                else localStorage.removeItem("lpb.apiBaseUrl");
                if (apiKey) localStorage.setItem("lpb.apiKey", apiKey);
                else localStorage.removeItem("lpb.apiKey");
                setSnackbarOpen(true);
                setTimeout(() => window.location.reload(), 600);
              }
            }}
          >
            Save & Reload
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbarOpen}
        message="Settings saved"
        autoHideDuration={1000}
        onClose={() => setSnackbarOpen(false)}
      />

      <Snackbar
        open={healthToast.open}
        autoHideDuration={6000}
        onClose={() => setHealthToast((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setHealthToast((prev) => ({ ...prev, open: false }))}
          severity={healthToast.severity}
          variant="filled"
        >
          {healthToast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Layout;
