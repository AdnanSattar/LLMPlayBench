/**
 * Request list component
 *
 * Author: Adnan Sattar
 * Email: adnansattar09@gmail.com
 * GitHub: https://github.com/AdnanSattar
 * LinkedIn: https://www.linkedin.com/in/adnansattar09/
 */

import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Divider,
} from "@mui/material";

function RequestList({ items = [], className = "", maxHeight = 344 }) {
  const [selected, setSelected] = useState(null);
  if (!items || items.length === 0) {
    return (
      <TableContainer component={Paper} className={className}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Recent Requests</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>No request history available</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <>
      <TableContainer
        component={Paper}
        className={className}
        sx={{ maxHeight: "100%", height: 1 }}
      >
        <Table
          size="small"
          stickyHeader
          sx={{ tableLayout: "fixed", width: "100%" }}
        >
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: "30%" }}>Time</TableCell>
              <TableCell sx={{ width: "34%" }}>Model</TableCell>
              <TableCell sx={{ width: "18%" }}>Latency</TableCell>
              <TableCell sx={{ width: "18%" }}>Tokens</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => {
              const date = new Date(item.timestamp * 1000);
              const timeString = date.toLocaleTimeString();
              const modelName = item.model.split("/").pop();
              return (
                <TableRow
                  key={item.id}
                  hover
                  onClick={() => setSelected(item)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell sx={{ whiteSpace: "nowrap" }}>
                    {timeString}
                  </TableCell>
                  <TableCell
                    title={item.model}
                    sx={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    <Chip
                      size="small"
                      label={modelName}
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap" }}>
                    {item.latency_s.toFixed(3)}s
                  </TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap" }}>
                    {Math.max(0, item.tokens)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Request Details</DialogTitle>
        <DialogContent>
          {selected && (
            <DialogContentText component="div">
              <div>
                <strong>Time:</strong>{" "}
                {new Date(selected.timestamp * 1000).toLocaleString()}
              </div>
              <div>
                <strong>Model:</strong> {selected.model}
              </div>
              <div>
                <strong>Latency:</strong> {selected.latency_s.toFixed(3)}s
              </div>
              <div>
                <strong>Tokens:</strong> {Math.max(0, selected.tokens)}
              </div>
              {selected.tokens_per_sec !== undefined && (
                <div>
                  <strong>Tokens/Sec:</strong>{" "}
                  {Math.max(0, selected.tokens_per_sec).toFixed(2)}
                </div>
              )}
              {selected.prompt_length !== undefined && (
                <div>
                  <strong>Prompt Length:</strong> {selected.prompt_length}
                </div>
              )}
              {selected.request_id && (
                <div>
                  <strong>Request ID:</strong> {selected.request_id}
                </div>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Generation Parameters */}
              <div>
                <strong>Generation Parameters:</strong>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "8px",
                    marginTop: "4px",
                  }}
                >
                  <Chip
                    size="small"
                    label={`Temperature: ${
                      selected.temperature !== null &&
                      selected.temperature !== undefined
                        ? selected.temperature
                        : 0.7
                    }`}
                    variant="outlined"
                  />
                  <Chip
                    size="small"
                    label={`Top-P: ${
                      selected.top_p !== null && selected.top_p !== undefined
                        ? selected.top_p
                        : 0.9
                    }`}
                    variant="outlined"
                  />
                  <Chip
                    size="small"
                    label={`Top-K: ${
                      selected.top_k !== null && selected.top_k !== undefined
                        ? selected.top_k
                        : 50
                    }`}
                    variant="outlined"
                  />
                </div>
              </div>

              {/* System Prompt */}
              {selected.system_prompt && (
                <div style={{ marginTop: "12px" }}>
                  <strong>System Prompt:</strong>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 1,
                      mt: 1,
                      maxHeight: "80px",
                      overflow: "auto",
                      bgcolor: "background.paper",
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                        fontSize: "0.85rem",
                      }}
                    >
                      {selected.system_prompt}
                    </pre>
                  </Paper>
                </div>
              )}

              {/* Prompt section */}
              {selected.prompt && (
                <div style={{ marginTop: "16px" }}>
                  <strong>Prompt:</strong>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 1,
                      mt: 1,
                      maxHeight: "150px",
                      overflow: "auto",
                      bgcolor: "background.paper",
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                      }}
                    >
                      {selected.prompt}
                    </pre>
                  </Paper>
                </div>
              )}

              {/* Response section */}
              {selected.response && (
                <div style={{ marginTop: "16px" }}>
                  <strong>Response:</strong>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 1,
                      mt: 1,
                      maxHeight: "200px",
                      overflow: "auto",
                      bgcolor: "background.paper",
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                      }}
                    >
                      {selected.response}
                    </pre>
                  </Paper>
                </div>
              )}
            </DialogContentText>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default RequestList;
