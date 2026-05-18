/**
 * Dashboard page
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useEffect, useState } from "react";
import { useTheme } from "@mui/material/styles";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Skeleton,
  Stack,
} from "@mui/material";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import MetricsChart from "../components/MetricsChart";
import RequestList from "../components/RequestList";
import ModelSelector from "../components/ModelSelector";
import {
  fetchMetrics,
  fetchMetricsSummary,
  runBenchmark,
  reloadModel,
  apiClient,
  isAdmin,
  checkIsAdmin,
} from "../lib/api";
import logger from "../lib/logger";

export default function Dashboard() {
  const [metrics, setMetrics] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState("");
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [adminVisible, setAdminVisible] = useState(false);
  const [loadingModelId, setLoadingModelId] = useState("");
  const theme = useTheme();
  const [modelsRefreshToken, setModelsRefreshToken] = useState(0);
  const [toast, setToast] = useState({
    open: false,
    message: "",
    severity: "info",
  });
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  const [docsNudgeShown, setDocsNudgeShown] = useState(
    localStorage.getItem("lpb.docsNudgeShown") === "true"
  );
  const availableModels = [
    "google/flan-t5-small",
    "HuggingFaceTB/SmolLM2-135M-Instruct",
    "google/gemma-3-270m",
    // Gated on Hugging Face; requires approved access + HF token
    "facebook/MobileLLM-R1-140M",
  ];

  useEffect(() => {
    // quick heuristic first
    setAdminVisible(isAdmin());
    // verify with backend to avoid showing for non-admin keys
    (async () => {
      const ok = await checkIsAdmin();
      setAdminVisible(ok);
    })();
    // Load metrics when component mounts or model filter changes
    loadMetrics();

    // Show docs nudge if not shown before
    if (!docsNudgeShown) {
      setTimeout(() => {
        setToast({
          open: true,
          message:
            "Models are cached in ./backend/models (HF_HOME). Check README for more details.",
          severity: "info",
        });
        localStorage.setItem("lpb.docsNudgeShown", "true");
        setDocsNudgeShown(true);
      }, 2000);
    }

    // Set up auto-refresh every 30 seconds
    const refreshInterval = setInterval(loadMetrics, 30000);

    return () => clearInterval(refreshInterval);
  }, [selectedModel, docsNudgeShown]);

  async function loadMetrics() {
    try {
      setLoading(true);
      setLastRefreshTime(Date.now());

      // Fetch metrics data
      const metricsData = await fetchMetrics(100, selectedModel);
      setMetrics(metricsData);

      // Fetch metrics summary
      const summaryData = await fetchMetricsSummary(selectedModel);
      setSummary(summaryData);

      setError(null);
    } catch (err) {
      setError("Failed to load metrics data");
      setToast({
        open: true,
        message: "Failed to load metrics. Backend may be unreachable.",
        severity: "error",
      });
      logger.error("Error loading metrics", { error: err.message });
    } finally {
      setLoading(false);
    }
  }

  // Check if metrics are stale (more than 60 seconds old)
  useEffect(() => {
    const checkStaleInterval = setInterval(() => {
      const now = Date.now();
      if (now - lastRefreshTime > 60000) {
        setToast({
          open: true,
          message: "Metrics data is stale. Click Refresh to update.",
          severity: "warning",
        });
      }
    }, 30000);

    return () => clearInterval(checkStaleInterval);
  }, [lastRefreshTime]);

  async function handleBenchmark() {
    if (!selectedModel || isBenchmarking) return;

    try {
      setIsBenchmarking(true);
      setBenchmarkResult(null);

      const result = await runBenchmark(selectedModel);
      setBenchmarkResult(result);

      // Refresh metrics after benchmark
      loadMetrics();
    } catch (err) {
      logger.error("Benchmark error", {
        error: err.message,
        model: selectedModel,
      });
    } finally {
      setIsBenchmarking(false);
    }
  }

  async function handleAdminLoad(modelId) {
    try {
      if (!modelId) return;
      setLoadingModelId(modelId);
      const res = await reloadModel(modelId, "int8");
      setToast({
        open: true,
        message: res?.message || `Loaded ${modelId}`,
        severity: "success",
      });
      // Give backend a moment then refresh metrics and models list via loadMetrics (uses model filter)
      await loadMetrics();
      // trigger ModelSelector to refetch /v1/models so new model appears
      setModelsRefreshToken((x) => x + 1);
    } catch (err) {
      logger.error("Admin load error", { error: err.message, model: modelId });
      const detail = err?.response?.data?.detail || err.message;
      const gated = /gated repo|403/i.test(String(detail))
        ? " – This model is gated on Hugging Face. Ensure access is approved and HF token is set."
        : "";
      setToast({
        open: true,
        message: `Failed to load ${modelId}: ${detail}${gated}`,
        severity: "error",
      });
    } finally {
      setLoadingModelId("");
    }
  }

  return (
    <>
      <Stack spacing={3} sx={{ px: 2, py: 3, maxWidth: 1200, mx: "auto" }}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5" fontWeight={700}>
              LLM Performance Dashboard
            </Typography>
          </Grid>
          <Grid item sx={{ display: "flex", gap: 1 }}>
            {adminVisible && (
              <select
                onChange={(e) => handleAdminLoad(e.target.value)}
                defaultValue=""
                style={{
                  background:
                    theme.palette.mode === "dark"
                      ? theme.palette.background.paper
                      : "#fff",
                  color:
                    theme.palette.mode === "dark"
                      ? theme.palette.text.primary
                      : theme.palette.text.primary,
                  border:
                    theme.palette.mode === "dark"
                      ? "1px solid rgba(255,255,255,0.2)"
                      : "1px solid rgba(0,0,0,0.2)",
                  borderRadius: 6,
                  padding: "8px 10px",
                  minWidth: 260,
                }}
                title="Load model into memory"
              >
                <option value="" disabled>
                  {loadingModelId
                    ? `Loading ${loadingModelId}...`
                    : "Load model (admin)"}
                </option>
                {availableModels.map((m) => (
                  <option
                    key={m}
                    value={m}
                    style={{
                      background:
                        theme.palette.mode === "dark" ? "#121212" : "#fff",
                      color: theme.palette.text.primary,
                    }}
                  >
                    {m}
                  </option>
                ))}
              </select>
            )}
            {adminVisible && (
              <Button
                variant="outlined"
                onClick={async () => {
                  try {
                    await apiClient.post("/v1/admin/clear_caches", null, {
                      headers: {
                        "X-API-Key": localStorage.getItem("lpb.apiKey") || "",
                      },
                    });
                    setToast({
                      open: true,
                      message: "Caches cleared",
                      severity: "success",
                    });
                  } catch (e) {
                    setToast({
                      open: true,
                      message: "Failed to clear caches",
                      severity: "error",
                    });
                  }
                }}
              >
                Clear caches
              </Button>
            )}
            <Button variant="outlined" onClick={loadMetrics}>
              Refresh
            </Button>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Grid container spacing={2} alignItems="flex-end">
              <Grid item xs={12} md={8}>
                <ModelSelector
                  value={selectedModel}
                  onChange={(m) => setSelectedModel(m)}
                  refreshToken={modelsRefreshToken}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  disabled={!selectedModel}
                  onClick={handleBenchmark}
                >
                  {isBenchmarking ? "Running Benchmark..." : "Run Benchmark"}
                </Button>
              </Grid>
            </Grid>

            {benchmarkResult && (
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption">Latency</Typography>
                      <Typography variant="h6">
                        {benchmarkResult.avg_time.toFixed(3)}s
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption">Tokens</Typography>
                      <Typography variant="h6">
                        {benchmarkResult.avg_tokens}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption">Tokens/Sec</Typography>
                      <Typography variant="h6">
                        {benchmarkResult.tokens_per_sec.toFixed(2)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption">Device</Typography>
                      <Typography variant="h6">
                        {benchmarkResult.device}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </CardContent>
        </Card>

        {summary ? (
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography
                    variant="caption"
                    title="Only counts requests where benchmarking was enabled"
                  >
                    Total Requests
                  </Typography>
                  <Typography variant="h5">{summary.total_requests}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="caption">Avg. Latency</Typography>
                  <Typography variant="h5">
                    {summary.overall_avg_latency.toFixed(3)}s
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="caption">Avg. Tokens</Typography>
                  <Typography variant="h5">
                    {Math.round(
                      summary.overall_avg_tokens &&
                        summary.overall_avg_tokens > 0
                        ? summary.overall_avg_tokens
                        : metrics.length
                        ? metrics.reduce(
                            (s, m) => s + Math.max(0, m.tokens),
                            0
                          ) / metrics.length
                        : 0
                    )}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="caption">Avg. TPS</Typography>
                  <Typography variant="h5">
                    {(summary.overall_avg_tps && summary.overall_avg_tps > 0
                      ? summary.overall_avg_tps
                      : metrics.length
                      ? metrics.reduce(
                          (s, m) => s + Math.max(0, m.tokens_per_sec || 0),
                          0
                        ) / metrics.length
                      : 0
                    ).toFixed(2)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Grid container spacing={2}>
            {Array.from({ length: 4 }).map((_, i) => (
              <Grid item xs={12} md={3} key={i}>
                <Card variant="outlined">
                  <CardContent>
                    <Skeleton variant="text" width={120} />
                    <Skeleton variant="rounded" height={32} />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Add benchmark status notice */}
        {metrics && metrics.length === 0 && !loading && (
          <Card
            variant="outlined"
            sx={{
              mb: 2,
              bgcolor: (theme) =>
                theme.palette.mode === "dark"
                  ? "rgba(255, 0, 0, 0.05)"
                  : "rgba(255, 0, 0, 0.02)",
            }}
          >
            <CardContent>
              <Typography color="error" variant="body2">
                <strong>No metrics data available.</strong> This could be
                because benchmarking is disabled. To collect metrics, enable
                benchmarking in the Playground by clicking the "Benchmark"
                toggle, or run a benchmark from this dashboard.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={7}>
            <Card variant="outlined" sx={{ height: 384 }}>
              <CardContent sx={{ height: 1 }}>
                {metrics && metrics.length > 0 ? (
                  <MetricsChart data={metrics} className="h-full" />
                ) : (
                  <Skeleton variant="rounded" height={320} />
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={5}>
            <Card variant="outlined" sx={{ height: 384 }}>
              <CardContent
                sx={{
                  height: 1,
                  p: 0,
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {metrics && metrics.length > 0 ? (
                  <RequestList items={metrics} maxHeight={320} />
                ) : (
                  <Skeleton variant="rounded" height={320} />
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>
      <Snackbar
        open={toast.open || Boolean(error)}
        onClose={() => {
          setToast((t) => ({ ...t, open: false }));
          setError(null);
        }}
        autoHideDuration={3500}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          severity={toast.open ? toast.severity : "error"}
          variant="filled"
          onClose={() => {
            setToast((t) => ({ ...t, open: false }));
            setError(null);
          }}
        >
          {toast.open ? toast.message : error}
        </Alert>
      </Snackbar>
    </>
  );
}
