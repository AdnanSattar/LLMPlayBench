/**
 * Playground page
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useEffect, useState } from "react";
import ModelSelector from "../components/ModelSelector";
import { generateResponse, healthCheck } from "../lib/api";
import logger from "../lib/logger";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Slider,
  Button,
  Stack,
  Box,
  Switch,
  Chip,
  CircularProgress,
} from "@mui/material";
import LoadingState from "../components/LoadingState";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

export default function Playground() {
  const [model, setModel] = useState("");
  const [quantization, setQuantization] = useState("int8");
  const [prompt, setPrompt] = useState("");
  const [systemPrompt, setSystemPrompt] = useState(
    "You are a helpful assistant.",
  );
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [maxTokens, setMaxTokens] = useState(128);
  const [temperature, setTemperature] = useState(0.7);
  const [topP, setTopP] = useState(0.9);
  const [topK, setTopK] = useState(50);
  const [responseTime, setResponseTime] = useState(null);
  const [benchmark, setBenchmark] = useState(true);
  const [health, setHealth] = useState("unknown");
  const [previousResponses, setPreviousResponses] = useState([]);
  const [toast, setToast] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  useEffect(() => {
    // Load previous responses from localStorage
    try {
      const savedResponses = localStorage.getItem("lpb.previousResponses");
      if (savedResponses) {
        setPreviousResponses(JSON.parse(savedResponses));
      }
    } catch (err) {
      console.error("Failed to load previous responses", err);
    }

    // Set up health check polling
    let t = null;
    const poll = async () => {
      const ok = await healthCheck();
      setHealth(ok ? "ok" : "down");
    };
    poll();
    t = setInterval(poll, 15000);
    return () => t && clearInterval(t);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setOutput("");

      const startTime = Date.now();
      const response = await generateResponse(
        model,
        prompt,
        maxTokens,
        temperature,
        quantization,
        systemPrompt,
        { benchmark, topP, topK },
      );
      const endTime = Date.now();
      setResponseTime((endTime - startTime) / 1000); // in seconds

      // Extract text from the response
      const responseText =
        response.choices?.[0]?.text || JSON.stringify(response, null, 2);
      setOutput(responseText);

      // Save to previous responses
      const newResponse = {
        id: `resp-${Date.now()}`,
        timestamp: Date.now(),
        model,
        prompt,
        response: responseText,
        systemPrompt,
        temperature,
        topP,
        topK,
        maxTokens,
        responseTime: (endTime - startTime) / 1000, // Store response time in seconds
      };

      const updatedResponses = [newResponse, ...previousResponses.slice(0, 9)]; // Keep last 10
      setPreviousResponses(updatedResponses);

      // Save to localStorage
      try {
        localStorage.setItem(
          "lpb.previousResponses",
          JSON.stringify(updatedResponses),
        );
      } catch (err) {
        console.error("Failed to save response history", err);
      }
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err.message ||
        "Failed to generate response";
      setError(msg);
      const notLoadedHint = /not loaded|not found in cache/i.test(String(msg))
        ? " – Load the model from the Dashboard (admin dropdown) first."
        : "";
      setToast({
        open: true,
        message: `${msg}${notLoadedHint}`,
        severity: "error",
      });
      logger.error("Error generating response", {
        error: msg,
        model,
      });
    } finally {
      setLoading(false);
    }
  }

  function handleModelChange(modelId, quantizationValue) {
    setModel(modelId);
    if (quantizationValue) {
      setQuantization(quantizationValue);
    }
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        LLM Playground
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Model Settings
              </Typography>

              <ModelSelector
                value={model}
                onChange={handleModelChange}
                includeQuantization={true}
              />

              <TextField
                label="Max Tokens"
                type="number"
                fullWidth
                margin="normal"
                value={maxTokens}
                inputProps={{ min: 1, max: 2048 }}
                onChange={(e) => setMaxTokens(parseInt(e.target.value) || 1)}
              />

              <Typography variant="caption" color="text.secondary">
                Temperature
              </Typography>
              <Grid container alignItems="center" spacing={1}>
                <Grid item xs>
                  <Slider
                    value={temperature}
                    min={0}
                    max={1}
                    step={0.1}
                    onChange={(_, v) => setTemperature(v)}
                  />
                </Grid>
                <Grid item>
                  <Typography variant="body2">{temperature}</Typography>
                </Grid>
              </Grid>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                gutterBottom
              >
                Controls randomness (0 = deterministic, 1 = creative)
              </Typography>

              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ flexGrow: 1 }}
                >
                  Top-P
                </Typography>
                <Switch
                  size="small"
                  checked={topP !== null}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setTopP(0.9); // Default value when enabled
                    } else {
                      setTopP(null); // Disable top-p
                    }
                  }}
                />
              </Box>
              {topP !== null && (
                <>
                  <Grid container alignItems="center" spacing={1}>
                    <Grid item xs>
                      <Slider
                        value={topP || 0.9}
                        min={0}
                        max={1}
                        step={0.05}
                        onChange={(_, v) => setTopP(v)}
                        disabled={topP === null}
                      />
                    </Grid>
                    <Grid item>
                      <Typography variant="body2">{topP || 0.9}</Typography>
                    </Grid>
                  </Grid>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                    gutterBottom
                  >
                    Nucleus sampling: higher values = more diverse outputs
                  </Typography>
                </>
              )}

              <Box sx={{ display: "flex", alignItems: "center", mb: 1, mt: 2 }}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ flexGrow: 1 }}
                >
                  Top-K
                </Typography>
                <Switch
                  size="small"
                  checked={topK !== null}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setTopK(50); // Default value when enabled
                    } else {
                      setTopK(null); // Disable top-k
                    }
                  }}
                />
              </Box>
              {topK !== null && (
                <>
                  <Grid container alignItems="center" spacing={1}>
                    <Grid item xs>
                      <Slider
                        value={topK || 50}
                        min={1}
                        max={100}
                        step={1}
                        onChange={(_, v) => setTopK(v)}
                        disabled={topK === null}
                      />
                    </Grid>
                    <Grid item>
                      <Typography variant="body2">{topK || 50}</Typography>
                    </Grid>
                  </Grid>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                    gutterBottom
                  >
                    Limits token selection to top K most likely tokens
                  </Typography>
                </>
              )}

              <Card
                variant="outlined"
                sx={{ mb: 2, bgcolor: "background.paper" }}
              >
                <CardContent sx={{ pb: 1 }}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    System Prompt
                  </Typography>
                  <TextField
                    multiline
                    minRows={2}
                    fullWidth
                    placeholder="You are a helpful assistant."
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    variant="outlined"
                    size="small"
                    InputProps={{
                      sx: {
                        fontSize: "0.875rem",
                        backgroundColor: (theme) =>
                          theme.palette.mode === "dark"
                            ? "rgba(255, 255, 255, 0.05)"
                            : "rgba(0, 0, 0, 0.02)",
                      },
                    }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 1, display: "block" }}
                  >
                    Instructions to control the assistant's behavior and persona
                  </Typography>
                </CardContent>
              </Card>

              <Button
                fullWidth
                variant="contained"
                disabled={!prompt.trim() || !model || loading}
                onClick={handleSubmit}
                startIcon={
                  loading ? (
                    <CircularProgress
                      size={18}
                      color="inherit"
                      className="motion-safe"
                    />
                  ) : null
                }
              >
                {loading ? "Generating..." : "Generate Response"}
              </Button>
              {/* Benchmark toggle with explanation */}
              <Card
                variant="outlined"
                sx={{
                  mt: 2,
                  mb: 1,
                  bgcolor: benchmark
                    ? (theme) =>
                        theme.palette.mode === "dark"
                          ? "rgba(0, 255, 0, 0.05)"
                          : "rgba(0, 255, 0, 0.05)"
                    : (theme) =>
                        theme.palette.mode === "dark"
                          ? "rgba(255, 0, 0, 0.05)"
                          : "rgba(255, 0, 0, 0.02)",
                }}
              >
                <CardContent sx={{ py: 1, px: 2, "&:last-child": { pb: 1 } }}>
                  <Grid
                    container
                    alignItems="center"
                    justifyContent="space-between"
                  >
                    <Grid item>
                      <Button
                        size="small"
                        color={benchmark ? "success" : "error"}
                        variant={benchmark ? "contained" : "outlined"}
                        onClick={() => setBenchmark((b) => !b)}
                        sx={{ mr: 2 }}
                      >
                        Benchmark {benchmark ? "ON" : "OFF"}
                      </Button>
                    </Grid>
                    <Grid item sx={{ flexGrow: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {benchmark
                          ? "Benchmarking enabled: Responses will be recorded in metrics dashboard."
                          : "Benchmarking disabled: Responses will NOT appear in metrics dashboard."}
                      </Typography>
                    </Grid>
                    <Grid item>
                      <Typography
                        variant="caption"
                        color={health === "ok" ? "success.main" : "error.main"}
                      >
                        {health === "ok"
                          ? "Backend healthy"
                          : "Backend unreachable"}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={9}>
          <Stack spacing={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Prompt
                </Typography>
                <TextField
                  multiline
                  minRows={6}
                  fullWidth
                  placeholder="Enter your prompt here..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />

                {previousResponses.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Previous Prompts
                    </Typography>
                    <Box
                      sx={{
                        maxHeight: 150,
                        overflow: "auto",
                        border: "1px solid",
                        borderColor: "divider",
                        borderRadius: 1,
                      }}
                    >
                      {previousResponses.map((item) => (
                        <Box
                          key={item.id}
                          sx={{
                            p: 1,
                            cursor: "pointer",
                            "&:hover": { bgcolor: "action.hover" },
                            borderBottom: "1px solid",
                            borderColor: "divider",
                          }}
                          onClick={() => {
                            // Set prompt and parameters
                            setPrompt(item.prompt);
                            setSystemPrompt(
                              item.systemPrompt ||
                                "You are a helpful assistant.",
                            );
                            setTemperature(item.temperature || 0.7);
                            if (item.topP) setTopP(item.topP);
                            if (item.topK) setTopK(item.topK);
                            setMaxTokens(item.maxTokens || 128);

                            // Set response and metrics
                            setOutput(item.response || "");
                            setError(null);

                            // Always set response time to ensure metrics are displayed
                            // Use stored responseTime or a default value (1.0s)
                            setResponseTime(item.responseTime || 1.0);

                            // Make sure we're not in loading state
                            setLoading(false);
                          }}
                        >
                          <Typography
                            variant="body2"
                            noWrap
                            title={item.prompt}
                          >
                            {item.prompt.substring(0, 60)}
                            {item.prompt.length > 60 ? "..." : ""}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            display="block"
                          >
                            {new Date(item.timestamp).toLocaleString()} ·{" "}
                            {item.model.split("/").pop()}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <Grid
                  container
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Grid item>
                    <Typography variant="subtitle1" fontWeight={600}>
                      Response
                    </Typography>
                  </Grid>
                  <Grid item>
                    {responseTime && !loading && (
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <Chip
                          size="small"
                          label={`Generated in ${responseTime.toFixed(2)}s`}
                          color="primary"
                          variant="outlined"
                        />
                        {output && (
                          <Chip
                            size="small"
                            label={`${output.split(/\s+/).length} tokens`}
                            color="secondary"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    )}
                  </Grid>
                </Grid>

                <Box
                  sx={{
                    mt: 1,
                    p: 2,
                    borderRadius: 1,
                    bgcolor: (t) =>
                      t.palette.mode === "dark" ? "#0f1214" : "#fafafa",
                    minHeight: 160,
                  }}
                >
                  {error ? (
                    <Typography color="error">{error}</Typography>
                  ) : loading ? (
                    <LoadingState
                      variant="default"
                      height={120}
                      text="Generating response..."
                    />
                  ) : output ? (
                    <Typography whiteSpace="pre-wrap">{output}</Typography>
                  ) : (
                    <Typography color="text.secondary" variant="body2">
                      Response will appear here.
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
      <Snackbar
        open={toast.open}
        onClose={() => setToast((t) => ({ ...t, open: false }))}
        autoHideDuration={3500}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          severity={toast.severity}
          variant="filled"
          onClose={() => setToast((t) => ({ ...t, open: false }))}
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
