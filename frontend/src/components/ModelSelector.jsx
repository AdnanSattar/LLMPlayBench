/**
 * Model selector component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useEffect, useState } from "react";
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
} from "@mui/material";
import { fetchModels } from "../lib/api";
import logger from "../lib/logger";

function ModelSelector({
  value,
  onChange,
  className = "",
  includeQuantization = false,
  refreshToken = 0,
}) {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantization, setQuantization] = useState("int8");

  useEffect(() => {
    const loadModels = async () => {
      try {
        setIsLoading(true);
        const modelData = await fetchModels();
        setModels(Array.isArray(modelData) ? modelData : []);
        setError(null);
      } catch (err) {
        setError("Failed to load models");
        logger.error("Error loading models", { error: err.message });
      } finally {
        setIsLoading(false);
      }
    };

    loadModels();
  }, [refreshToken]);

  const handleModelChange = (e) => {
    if (onChange) {
      onChange(e.target.value, includeQuantization ? quantization : undefined);
    }
  };

  const handleQuantizationChange = (e) => {
    const newQuant = e.target.value;
    setQuantization(newQuant);

    if (onChange && value) {
      onChange(value, newQuant);
    }
  };

  // Allow opening while loading; show skeleton only if desired externally

  if (error) {
    return <div className={`text-red-500 ${className}`}>{error}</div>;
  }

  return (
    <div className={className}>
      <FormControl fullWidth size="small">
        <InputLabel id="model-select-label">Model</InputLabel>
        <Select
          labelId="model-select-label"
          id="model-select"
          label="Model"
          value={value || ""}
          onChange={handleModelChange}
          disabled={false}
        >
          <MenuItem value="">Select a model</MenuItem>
          {(isLoading ? [] : models).map((m) => (
            <MenuItem key={m.id} value={m.id}>
              {m.id}
            </MenuItem>
          ))}
          {isLoading && <MenuItem disabled>Loading models…</MenuItem>}
        </Select>
      </FormControl>
    </div>
  );
}

export default ModelSelector;
