#!/usr/bin/env python3
"""
Script to load all supported models into LLMPlayBench.

This script loads all the models so they appear in the /v1/models endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import time

import requests

# API configuration
API_BASE_URL = "http://localhost:8000"
ADMIN_API_KEY = "admin_api_key_replace_in_production"


def load_model(model_name, quantization="int8"):
    """Load a model using the admin endpoint."""
    print(f"🔄 Loading model: {model_name}")

    headers = {
        "X-API-Key": ADMIN_API_KEY,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/admin/reload_model",
            headers=headers,
            params={"model_name": model_name, "quantization": quantization},
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully loaded {model_name}")
            print(f"   Device: {result.get('device', 'unknown')}")
            return True
        else:
            print(f"❌ Failed to load {model_name}: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception loading {model_name}: {str(e)}")
        return False


def check_loaded_models():
    """Check which models are currently loaded."""
    print("\n📋 Checking currently loaded models...")

    try:
        response = requests.get(f"{API_BASE_URL}/v1/models")
        if response.status_code == 200:
            models = response.json()
            print(f"Found {len(models)} loaded models:")
            for model in models:
                print(f"  - {model['id']} ({model['quantization']})")
            return models
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception getting models: {str(e)}")
        return []


def main():
    """Load all supported models."""
    print("🚀 LLMPlayBench Model Loader")
    print("Loading all supported models...")

    # List of models to load (now with HF token support)
    models_to_load = [
        "google/flan-t5-small",  # Already loaded by default
        "HuggingFaceTB/SmolLM2-135M-Instruct",
        "facebook/MobileLLM-R1-140M",  # Now accessible with HF token
        "google/gemma-3-270m",  # Now accessible with HF token
    ]

    # Check current models first
    current_models = check_loaded_models()
    current_model_ids = [model["id"] for model in current_models]

    # Load each model
    loaded_count = 0
    for model_name in models_to_load:
        if model_name in current_model_ids:
            print(f"⏭️  {model_name} already loaded, skipping...")
            continue

        success = load_model(model_name)
        if success:
            loaded_count += 1

        # Brief pause between loads
        time.sleep(2)

    # Final check
    print(f"\n🎉 Loading complete!")
    print(f"Successfully loaded {loaded_count} new models")

    # Show final model list
    final_models = check_loaded_models()
    print(f"\n📊 Total models now available: {len(final_models)}")

    return final_models


if __name__ == "__main__":
    main()
