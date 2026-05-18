#!/usr/bin/env python3
"""
Test script for the new models added to LLMPlayBench.

This script demonstrates how to use the new models:
1. SmolLM2-135M-Instruct
2. MobileLLM-R1-140M
3. google/gemma-3-270m

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import json
import time

import requests

# API configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "read-dev-key"


def test_model(model_name, prompt, system_prompt=None, max_tokens=100, temperature=0.7):
    """Test a model with the given prompt."""
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name}")
    print(f"{'='*60}")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if system_prompt:
        payload["system_prompt"] = system_prompt

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/v1/response", headers=headers, json=payload
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response time: {end_time - start_time:.2f}s")
            print(f"📝 Response: {result['choices'][0]['text']}")
            print(f"📊 Usage: {result['usage']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def main():
    """Run tests for all new models."""
    print("🚀 LLMPlayBench New Models Test")
    print("Testing the newly added models...")

    # Test prompts
    test_cases = [
        {
            "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
            "prompt": "Write a Python function to calculate the factorial of a number.",
            "system_prompt": "You are a helpful coding assistant. Provide clean, well-documented code.",
            "max_tokens": 200,
            "temperature": 0.3,
        },
        {
            "model": "facebook/MobileLLM-R1-140M",
            "prompt": "Explain quantum computing in simple terms that a beginner can understand.",
            "max_tokens": 150,
            "temperature": 0.5,
        },
        {
            "model": "google/gemma-3-270m",
            "prompt": "What are the benefits of renewable energy?",
            "system_prompt": "You are an environmental expert. Provide detailed, accurate information.",
            "max_tokens": 180,
            "temperature": 0.4,
        },
        {
            "model": "google/flan-t5-small",
            "prompt": "Translate to French: Hello, how are you today?",
            "max_tokens": 50,
            "temperature": 0.7,
        },
    ]

    for test_case in test_cases:
        test_model(**test_case)
        time.sleep(1)  # Brief pause between tests

    print(f"\n{'='*60}")
    print("🎉 All tests completed!")
    print("Check the responses above to verify the models are working correctly.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
