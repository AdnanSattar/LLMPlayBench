/**
 * API client for LLMPlayBench
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import axios from "axios";
import logger from "./logger";

// Allow runtime overrides via localStorage (set from Settings dialog)
const storedUrl =
  typeof window !== "undefined" ? localStorage.getItem("lpb.apiBaseUrl") : null;
const storedKey =
  typeof window !== "undefined" ? localStorage.getItem("lpb.apiKey") : null;
const storedWriteKey =
  typeof window !== "undefined"
    ? localStorage.getItem("lpb.apiKeyWrite")
    : null;
function resolveApiBaseUrl() {
  if (storedUrl) return storedUrl;
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) return envUrl;
  // Prod Docker: nginx proxies /v1 and /health to the backend on the same host.
  if (import.meta.env.PROD && typeof window !== "undefined") {
    return window.location.origin;
  }
  return "http://localhost:8000";
}

const API_URL = resolveApiBaseUrl();
const API_KEY = storedKey || import.meta.env.VITE_API_KEY || "read-dev-key";
const API_KEY_WRITE =
  storedWriteKey ||
  import.meta.env.VITE_API_KEY_WRITE ||
  import.meta.env.VITE_ADMIN_API_KEY ||
  (API_KEY === "read-dev-key" ? "admin-dev-key" : API_KEY);

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Ensure API key header is always attached (guards against missing env at runtime)
apiClient.interceptors.request.use((config) => {
  const key = API_KEY || import.meta.env.VITE_API_KEY || "read-dev-key";
  if (!config.headers["X-API-Key"]) {
    config.headers["X-API-Key"] = key;
  }
  return config;
});

export const fetchModels = async () => {
  try {
    logger.debug("Fetching available models");
    const response = await apiClient.get("/v1/models");
    logger.info(`Successfully fetched ${response.data?.length || 0} models`);
    return response.data;
  } catch (error) {
    logger.error("Error fetching models", {
      error: error.message,
      status: error.response?.status,
    });
    throw error;
  }
};

export const generateResponse = async (
  modelId,
  prompt,
  maxTokens = 128,
  temperature = 0.7,
  quantization = "int8",
  systemPrompt = null,
  { benchmark = false, topP = 0.9, topK = 50 } = {}
) => {
  try {
    logger.info("Generating response", {
      model: modelId,
      promptLength: prompt.length,
      maxTokens,
      temperature,
      topP,
      topK,
    });
    const response = await apiClient.post(
      `/v1/response${benchmark ? "?benchmark=true" : ""}`,
      {
        model: modelId,
        prompt,
        system_prompt: systemPrompt,
        max_tokens: maxTokens,
        temperature,
        quantization,
        top_p: topP,
        top_k: topK,
      },
      { headers: { "X-API-Key": API_KEY_WRITE } }
    );
    logger.info("Response generated successfully", {
      model: modelId,
      responseLength: response.data?.choices?.[0]?.text?.length || 0,
    });
    return response.data;
  } catch (error) {
    logger.error("Error generating response", {
      model: modelId,
      error: error.message,
      status: error.response?.status,
    });
    throw error;
  }
};

export const fetchMetrics = async (limit = 100, modelFilter = null) => {
  try {
    logger.debug("Fetching recent metrics", { limit, modelFilter });
    let url = "/v1/metrics/recent";
    const params = {};

    if (limit) params.limit = limit;
    if (modelFilter) params.model = modelFilter;

    const response = await apiClient.get(url, { params });
    logger.debug(`Fetched ${response.data?.metrics?.length || 0} metrics`);
    return response.data.metrics;
  } catch (error) {
    logger.error("Error fetching metrics", {
      error: error.message,
      status: error.response?.status,
    });
    throw error;
  }
};

export const fetchMetricsSummary = async (modelFilter = null) => {
  try {
    logger.debug("Fetching metrics summary", { modelFilter });
    let url = "/v1/metrics/summary";
    const params = {};

    if (modelFilter) params.model = modelFilter;

    const response = await apiClient.get(url, { params });
    logger.debug("Metrics summary fetched successfully");
    return response.data;
  } catch (error) {
    logger.error("Error fetching metrics summary", {
      error: error.message,
      status: error.response?.status,
    });
    throw error;
  }
};

export const runBenchmark = async (modelId, quantization = "int8") => {
  try {
    logger.info("Running benchmark", { model: modelId, quantization });
    const response = await apiClient.get("/v1/benchmarks", {
      params: {
        model: modelId,
        quantization,
      },
      headers: { "X-API-Key": API_KEY_WRITE },
    });
    logger.info("Benchmark completed", {
      model: modelId,
      avgLatency: response.data?.avg_time,
    });
    return response.data;
  } catch (error) {
    logger.error("Error running benchmark", {
      model: modelId,
      error: error.message,
      status: error.response?.status,
    });
    throw error;
  }
};

// Admin: reload model into memory
export const reloadModel = async (modelId, quantization = "int8") => {
  try {
    logger.info("Reloading model", { model: modelId, quantization });
    const response = await apiClient.post(
      "/v1/admin/reload_model",
      {},
      {
        params: { model_name: modelId, quantization },
        headers: { "X-API-Key": API_KEY_WRITE },
      }
    );
    logger.info("Model reloaded", {
      model: modelId,
      device: response.data?.device,
    });
    return response.data;
  } catch (error) {
    logger.error("Error reloading model", {
      model: modelId,
      error: error.message,
      status: error.response?.status,
      detail: error.response?.data,
    });
    throw error;
  }
};

export const isAdmin = () => {
  try {
    const key = API_KEY_WRITE || "";
    // Synchronous heuristic (kept as fallback); actual check uses checkIsAdmin() below
    return (
      key === "admin-dev-key" ||
      key === (import.meta.env.VITE_ADMIN_API_KEY || "")
    );
  } catch {
    return false;
  }
};

export const checkIsAdmin = async () => {
  try {
    const resp = await apiClient.get("/v1/auth/admin", {
      headers: { "X-API-Key": API_KEY_WRITE },
    });
    return resp.status === 200;
  } catch {
    return false;
  }
};

export const healthCheck = async () => {
  try {
    const resp = await apiClient.get("/health");
    return resp.status === 200;
  } catch {
    return false;
  }
};

export default apiClient;
