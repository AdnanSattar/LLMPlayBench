"""
Model loading and management service.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os
import time
import traceback

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline,
)

from ..core.config import settings
from ..core.logging import app_logger
from .model_cache_service import (
    cache_model_metrics,
    cache_model_response,
    get_cached_metrics,
    get_cached_response,
)

# Model cache dictionary
MODEL_CACHE = {}


def _get_model_class(model_name: str):
    """
    Determine the appropriate model class based on model name.

    Args:
        model_name: HuggingFace model name or path

    Returns:
        Model class to use
    """
    # Map model names to their appropriate classes
    model_mappings = {
        "google/flan-t5-small": AutoModelForSeq2SeqLM,
        "HuggingFaceTB/SmolLM2-135M-Instruct": AutoModelForCausalLM,
        "facebook/MobileLLM-R1-140M": AutoModelForCausalLM,
        "google/gemma-3-270m": AutoModelForCausalLM,
    }

    # Check for exact match first
    if model_name in model_mappings:
        return model_mappings[model_name]

    # Check for partial matches
    for pattern, model_class in model_mappings.items():
        if pattern in model_name or model_name in pattern:
            return model_class

    # Default to causal LM for unknown models
    app_logger.warning(
        "Unknown model type, defaulting to AutoModelForCausalLM", model=model_name
    )
    return AutoModelForCausalLM


def load_model(model_name: str, quant: str = "int8"):
    """
    Load model and tokenizer with specified quantization.

    Args:
        model_name: HuggingFace model name or path
        quant: Quantization level (int8, int4, none)

    Returns:
        Tuple of (tokenizer, model)
    """
    key = f"{model_name}::{quant}"
    if key in MODEL_CACHE:
        app_logger.debug(
            "Model already loaded from cache", model=model_name, quant=quant
        )
        return MODEL_CACHE[key]

    app_logger.info(
        "Loading model", model=model_name, quant=quant, cache_dir=settings.CACHE_DIR
    )

    # Make sure cache dir exists
    os.makedirs(settings.CACHE_DIR, exist_ok=True)

    # Determine the appropriate model class
    model_class = _get_model_class(model_name)

    # Always use CPU-safe loading to avoid accelerate/bitsandbytes requirements
    # Quantization hints are ignored in this CPU-only build.
    try:
        app_logger.debug("Loading tokenizer", model=model_name)
        # Use HF token if available
        hf_token = os.getenv("HF_TOKEN")
        tokenizer_kwargs = {"cache_dir": settings.CACHE_DIR}
        if hf_token:
            tokenizer_kwargs["token"] = hf_token

        tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)

        # Add pad token if not present (required for some models)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        app_logger.debug(
            "Loading model", model=model_name, model_class=model_class.__name__
        )
        # Use HF token if available
        model_kwargs = {"cache_dir": settings.CACHE_DIR}
        if hf_token:
            model_kwargs["token"] = hf_token

        model = model_class.from_pretrained(
            model_name,
            **model_kwargs,
            # Ensure no device_map auto that triggers accelerate
        )
        model.to("cpu")
        app_logger.debug("Model loaded to CPU", model=model_name)
    except Exception as e:
        app_logger.warning(
            "Model loading failed, retrying", model=model_name, error=str(e)
        )
        traceback.print_exc()
        # Retry once more in case of transient issues
        tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = model_class.from_pretrained(model_name, **model_kwargs)
        model.to("cpu")
        app_logger.info("Model loaded successfully on retry", model=model_name)

    # Warmup: dummy forward pass
    try:
        app_logger.debug("Running model warmup", model=model_name)
        # Use different warmup strategies based on model type
        if model_class == AutoModelForSeq2SeqLM:
            # For T5-style models, use encoder-decoder format
            inputs = tokenizer("Hello", return_tensors="pt").to(model.device)
            _ = model.generate(**inputs, max_new_tokens=1)
        else:
            # For causal LM models, use chat template if available
            try:
                # Try to use chat template for instruction-tuned models
                messages = [{"role": "user", "content": "Hello"}]
                if hasattr(tokenizer, "apply_chat_template"):
                    inputs = tokenizer.apply_chat_template(
                        messages,
                        add_generation_prompt=True,
                        tokenize=True,
                        return_tensors="pt",
                    ).to(model.device)
                else:
                    inputs = tokenizer("Hello", return_tensors="pt").to(model.device)
                _ = model.generate(**inputs, max_new_tokens=1)
            except Exception:
                # Fallback to simple text generation
                inputs = tokenizer("Hello", return_tensors="pt").to(model.device)
                _ = model.generate(**inputs, max_new_tokens=1)
        app_logger.debug("Model warmup completed", model=model_name)
    except Exception as e:
        app_logger.warning("Model warmup failed", model=model_name, error=str(e))
        # Ignore warmup errors
        pass

    MODEL_CACHE[key] = (tokenizer, model)
    app_logger.info(
        "Model cached successfully",
        model=model_name,
        quant=quant,
        cache_size=len(MODEL_CACHE),
    )
    return tokenizer, model


def generate_response(
    tokenizer,
    model,
    prompt,
    max_tokens,
    temperature=None,
    system_prompt=None,
    top_p=None,
    top_k=None,
    model_name=None,
    quantization="int8",
    use_cache=True,
):
    """
    Generate a response using the appropriate method for the model type.

    Supports Redis caching to avoid regenerating identical responses.

    Args:
        tokenizer: HuggingFace tokenizer
        model: HuggingFace model
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        system_prompt: Optional system prompt
        top_p: Optional nucleus sampling parameter (0.0-1.0)
        top_k: Optional top-k sampling parameter
        model_name: Optional model name for caching
        quantization: Model quantization level for caching
        use_cache: Whether to use Redis caching (default: True)

    Returns:
        Generated text response
    """
    # Try to get from cache first if caching is enabled and model_name is provided
    if use_cache and model_name:
        cached_response = get_cached_response(
            model_name,
            prompt,
            max_tokens,
            temperature,
            system_prompt,
            top_p,
            top_k,
            quantization,
        )
        if cached_response:
            app_logger.info(
                "Using cached response",
                model=model_name,
                prompt_length=len(prompt),
                cache_hit=True,
            )
            return cached_response.get("text", "")

    # Start timing for metrics
    start_time = time.time()

    # Compose final prompt with optional system instruction
    final_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

    # Check if this is a causal LM model (needs chat template)
    if hasattr(model, "config") and hasattr(model.config, "model_type"):
        model_type = model.config.model_type
        is_causal = model_type in ["gpt2", "llama", "mistral", "gemma", "qwen"]
    else:
        # Fallback: check if tokenizer has apply_chat_template
        is_causal = hasattr(tokenizer, "apply_chat_template")

    if is_causal and hasattr(tokenizer, "apply_chat_template"):
        # Use chat template for instruction-tuned models
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            inputs = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=True, return_tensors="pt"
            ).to(model.device)
        except Exception as e:
            app_logger.warning(
                "Chat template failed, using simple prompt", error=str(e)
            )
            inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)
    else:
        # Use simple prompt encoding
        inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)

    # Generate response
    gen_kwargs = {"max_new_tokens": max_tokens}
    if temperature is not None:
        gen_kwargs.update(
            {
                "do_sample": temperature > 0,
                "temperature": max(0.0, float(temperature)),
            }
        )
    # Apply repetition controls for causal LMs
    try:
        from ..core.config import settings as _s  # type: ignore
    except Exception:
        _s = None
    try:
        is_encoder_decoder = getattr(model.config, "is_encoder_decoder", False)
        _is_causal = not bool(is_encoder_decoder)
    except Exception:
        _is_causal = True
    if _is_causal:
        # Use provided top_p/top_k if available, otherwise use defaults from settings
        _top_p = (
            top_p if top_p is not None else getattr(_s, "TOP_P", 0.9) if _s else 0.9
        )
        _top_k = top_k if top_k is not None else getattr(_s, "TOP_K", 50) if _s else 50

        gen_kwargs.update(
            {
                "repetition_penalty": (
                    getattr(_s, "REPETITION_PENALTY", 1.2) if _s else 1.2
                ),
                "no_repeat_ngram_size": (
                    getattr(_s, "NO_REPEAT_NGRAM_SIZE", 3) if _s else 3
                ),
            }
        )

        # Only add top_p if it's not None (allows disabling)
        if top_p is not None:
            gen_kwargs["top_p"] = _top_p

        # Only add top_k if it's not None (allows disabling)
        if top_k is not None:
            gen_kwargs["top_k"] = _top_k

    # Support both tensor and BatchEncoding/dict inputs
    if isinstance(inputs, dict) or hasattr(inputs, "keys"):
        outputs = model.generate(**inputs, **gen_kwargs)
    else:
        outputs = model.generate(inputs, **gen_kwargs)

    # Decode response
    if is_causal and hasattr(tokenizer, "apply_chat_template"):
        # For chat models, decode only the new tokens
        try:
            if isinstance(inputs, dict) or hasattr(inputs, "get"):
                input_ids = inputs.get("input_ids")
            else:
                input_ids = inputs
            input_length = (
                input_ids.shape[1] if hasattr(input_ids, "shape") else len(input_ids[0])
            )
        except Exception:
            input_length = 0
        response_tokens = outputs[0][input_length:]
        text = tokenizer.decode(response_tokens, skip_special_tokens=True)
    else:
        # For T5-style models, decode the full output
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the input prompt from the output for T5 models
        if final_prompt in text:
            text = text.replace(final_prompt, "").strip()

    # Cache the response if caching is enabled and model_name is provided
    if use_cache and model_name:
        generation_time = time.time() - start_time
        response_data = {
            "text": text,
            "model": model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system_prompt": system_prompt,
            "top_p": top_p,
            "top_k": top_k,
            "quantization": quantization,
            "generation_time": generation_time,
        }
        cache_model_response(
            model_name,
            prompt,
            max_tokens,
            text,
            response_data,
            temperature,
            system_prompt,
            top_p,
            top_k,
            quantization,
        )

    return text


def list_loaded_models():
    """
    List all loaded models in the cache.

    Returns:
        List of model info dictionaries
    """
    entries = []
    for key in MODEL_CACHE.keys():
        model_name, quant = key.split("::")
        entries.append({"id": model_name, "quantization": quant})
    return entries


def unload_model(model_name: str, quant: str = "int8"):
    """
    Unload a model from the cache.

    Args:
        model_name: Model name
        quant: Quantization level

    Returns:
        Success status
    """
    key = f"{model_name}::{quant}"
    if key in MODEL_CACHE:
        app_logger.info("Unloading model from cache", model=model_name, quant=quant)
        del MODEL_CACHE[key]
        # Force CUDA memory cleanup if applicable
        try:
            torch.cuda.empty_cache()
        except Exception:
            # CUDA not available, ignore
            pass
        app_logger.info(
            "Model unloaded successfully",
            model=model_name,
            remaining_cache_size=len(MODEL_CACHE),
        )
        return True
    app_logger.warning(
        "Model not found in cache for unloading", model=model_name, quant=quant
    )
    return False
