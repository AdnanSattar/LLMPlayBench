# 🤖 Supported Models Guide

This document provides detailed information about all supported models in LLMPlayBench.

## Model Categories

### T5-Based Models (Encoder-Decoder Architecture)

These models use the T5 (Text-to-Text Transfer Transformer) architecture, which is excellent for tasks like translation, summarization, and question answering.

#### google/flan-t5-small

- **Parameters**: 60M
- **Architecture**: Encoder-Decoder (T5)
- **Best for**: Translation, summarization, question answering
- **Memory**: ~240MB
- **Speed**: Fastest inference

**Example Usage:**

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/flan-t5-small",
    "prompt": "Translate to Spanish: Good morning, how are you?",
    "max_tokens": 50
  }'
```

### Causal Language Models (Decoder-Only Architecture)

These models use the GPT-style decoder-only architecture, optimized for text generation and conversation.

#### HuggingFaceTB/SmolLM2-135M-Instruct

- **Parameters**: 135M
- **Architecture**: Decoder-Only (GPT-style)
- **Best for**: Code generation, creative writing, instruction following
- **Memory**: ~540MB
- **Speed**: Fast

**Example Usage:**

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    "prompt": "Write a Python function to sort a list of numbers",
    "system_prompt": "You are a helpful coding assistant.",
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

#### facebook/MobileLLM-R1-140M

- **Parameters**: 140M
- **Architecture**: Decoder-Only (Mobile-optimized)
- **Best for**: Mobile applications, edge computing, general chat
- **Memory**: ~560MB
- **Speed**: Fast (mobile-optimized)

**Example Usage:**

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/MobileLLM-R1-140M",
    "prompt": "Explain machine learning in simple terms",
    "max_tokens": 150,
    "temperature": 0.5
  }'
```

#### google/gemma-3-270m

- **Parameters**: 270M
- **Architecture**: Decoder-Only (Gemma)
- **Best for**: General purpose, research, complex reasoning
- **Memory**: ~1.1GB
- **Speed**: Moderate

**Example Usage:**

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-3-270m",
    "prompt": "What are the advantages of renewable energy?",
    "system_prompt": "You are an environmental expert.",
    "max_tokens": 200,
    "temperature": 0.4
  }'
```

## Model Selection Guide

### For Translation Tasks

- **Best**: `google/flan-t5-small`
- **Why**: T5 architecture excels at text-to-text tasks

### For Code Generation

- **Best**: `HuggingFaceTB/SmolLM2-135M-Instruct`
- **Why**: Instruction-tuned for coding tasks

### For Mobile/Edge Applications

- **Best**: `facebook/MobileLLM-R1-140M`
- **Why**: Optimized for mobile deployment

### For General Purpose

- **Best**: `google/gemma-3-270m`
- **Why**: Larger model with better reasoning capabilities

## Performance Comparison

| Model | Parameters | Memory | Speed | Best Use Case |
|-------|------------|--------|-------|---------------|
| flan-t5-small | 60M | ~240MB | Fastest | Translation, Q&A |
| SmolLM2-135M | 135M | ~540MB | Fast | Code, Instructions |
| MobileLLM-140M | 140M | ~560MB | Fast | Mobile, Chat |
| gemma-3-270m | 270M | ~1.1GB | Moderate | General Purpose |

## Configuration Tips

### Memory Optimization

- Use `google/flan-t5-small` for minimal memory usage
- Use `facebook/MobileLLM-R1-140M` for balanced performance/memory

### Speed Optimization

- T5 models are fastest for text-to-text tasks
- Causal LMs are better for creative generation

### Quality vs Speed Trade-offs

- `google/flan-t5-small`: Fastest, good for simple tasks
- `HuggingFaceTB/SmolLM2-135M-Instruct`: Good balance
- `google/gemma-3-270m`: Best quality, slower inference

## Troubleshooting

### Model Loading Issues

- Ensure sufficient memory (check model sizes above)
- Models are cached in `./models` directory
- Use CPU fallback if GPU unavailable

### Performance Issues

- Start with smaller models for testing
- Adjust `max_tokens` based on your needs
- Use appropriate `temperature` values (0.1-0.7 for most tasks)

### Chat Template Issues

- Causal LM models use chat templates automatically
- T5 models use simple prompt formatting
- System prompts work with all models
