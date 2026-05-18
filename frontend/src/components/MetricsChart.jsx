/**
 * Metrics chart component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useMemo, useState } from "react";
import { Tabs, Tab, Box, Stack, Typography } from "@mui/material";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function MetricsChart({ data = [], className = "" }) {
  const [chartType, setChartType] = useState("latency"); // 'latency', 'tokens', 'tokensPerSec'

  if (!data || data.length === 0) {
    return (
      <div
        className={`dashboard-card flex items-center justify-center ${className}`}
      >
        <p className="text-gray-500">No metrics data available</p>
      </div>
    );
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return `${date.getHours()}:${date
      .getMinutes()
      .toString()
      .padStart(2, "0")}:${date.getSeconds().toString().padStart(2, "0")}`;
  };

  // Process data for charts
  const chartData = data
    .map((item) => ({
      timestamp: formatTimestamp(item.timestamp),
      latency: parseFloat(item.latency_s.toFixed(3)),
      tokens: Math.max(0, item.tokens),
      tokensPerSec: Math.max(0, parseFloat(item.tokens_per_sec.toFixed(2))),
      model: item.model.split("/").pop(), // Show only model name, not full path
    }))
    .reverse(); // Show most recent data on the right

  // Chart config based on selected metric
  const chartConfig = {
    latency: {
      title: "Latency (seconds)",
      key: "latency",
      color: "#2563eb", // blue-600
      yAxisLabel: "Seconds",
      domain: [0, "auto"],
    },
    tokens: {
      title: "Token Count",
      key: "tokens",
      color: "#059669", // emerald-600
      yAxisLabel: "Tokens",
      domain: [0, "auto"],
    },
    tokensPerSec: {
      title: "Tokens per Second",
      key: "tokensPerSec",
      color: "#d97706", // amber-600
      yAxisLabel: "Tokens/Sec",
      domain: [0, "auto"],
    },
  };

  const selectedConfig = chartConfig[chartType];

  // Stats helpers (avg, min, max, p50, p95)
  const computeStats = (values) => {
    if (!values.length) return null;
    const sorted = [...values].sort((a, b) => a - b);
    const avg = sorted.reduce((s, v) => s + v, 0) / sorted.length;
    const p = (q) =>
      sorted[Math.min(sorted.length - 1, Math.floor(q * (sorted.length - 1)))];
    return {
      avg,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      p50: p(0.5),
      p95: p(0.95),
    };
  };

  const stats = useMemo(() => {
    const key = selectedConfig.key;
    const vals = chartData.map((d) => Math.max(0, Number(d[key]) || 0));
    return computeStats(vals);
  }, [chartData, selectedConfig]);

  return (
    <div className={`dashboard-card ${className}`}>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ mb: 2 }}
      >
        <Typography variant="h6">{selectedConfig.title}</Typography>
        <Tabs
          value={chartType}
          onChange={(_, v) => setChartType(v)}
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab value="latency" label="Latency" />
          <Tab value="tokens" label="Tokens" />
          <Tab value="tokensPerSec" label="Tokens/Sec" />
        </Tabs>
      </Stack>

      <div className="metrics-chart-container" style={{ height: "300px" }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "tokens" ? (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                label={{
                  value: "Time",
                  position: "insideBottomRight",
                  offset: -10,
                }}
                scale="band"
              />
              <YAxis
                label={{
                  value: selectedConfig.yAxisLabel,
                  angle: -90,
                  position: "insideLeft",
                }}
                domain={selectedConfig.domain}
              />
              <Tooltip
                formatter={(value) => [value, selectedConfig.title]}
                labelFormatter={(label) => `Time: ${label}`}
              />
              <Legend />
              <Bar
                name={selectedConfig.title}
                dataKey={selectedConfig.key}
                fill={selectedConfig.color}
              />
            </BarChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                label={{
                  value: "Time",
                  position: "insideBottomRight",
                  offset: -10,
                }}
              />
              <YAxis
                label={{
                  value: selectedConfig.yAxisLabel,
                  angle: -90,
                  position: "insideLeft",
                }}
                domain={selectedConfig.domain}
              />
              <Tooltip
                formatter={(value) => [value, selectedConfig.title]}
                labelFormatter={(label) => `Time: ${label}`}
              />
              <Legend />
              <Line
                name={selectedConfig.title}
                type="monotone"
                dataKey={selectedConfig.key}
                stroke={selectedConfig.color}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      <Box sx={{ mt: 2 }}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Stat
            label="Avg"
            value={stats ? stats.avg : 0}
            suffix={chartType === "latency" ? "s" : ""}
            decimals={chartType === "tokens" ? 0 : 2}
          />
          <Stat
            label="Min"
            value={stats ? stats.min : 0}
            suffix={chartType === "latency" ? "s" : ""}
            decimals={chartType === "tokens" ? 0 : 2}
          />
          <Stat
            label="P50"
            value={stats ? stats.p50 : 0}
            suffix={chartType === "latency" ? "s" : ""}
            decimals={chartType === "tokens" ? 0 : 2}
          />
          <Stat
            label="P95"
            value={stats ? stats.p95 : 0}
            suffix={chartType === "latency" ? "s" : ""}
            decimals={chartType === "tokens" ? 0 : 2}
          />
          <Stat
            label="Max"
            value={stats ? stats.max : 0}
            suffix={chartType === "latency" ? "s" : ""}
            decimals={chartType === "tokens" ? 0 : 2}
          />
        </Stack>
      </Box>
    </div>
  );
}

export default MetricsChart;

function Stat({ label, value, suffix = "", decimals = 2 }) {
  const v = Math.max(0, Number(value) || 0);
  const formatted =
    decimals > 0 ? v.toFixed(decimals) : Math.round(v).toString();
  return (
    <Box
      sx={{
        p: 1.25,
        borderRadius: 1,
        bgcolor: "action.hover",
        textAlign: "center",
        minWidth: 96,
      }}
    >
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
        {formatted}
        {suffix}
      </Typography>
    </Box>
  );
}
