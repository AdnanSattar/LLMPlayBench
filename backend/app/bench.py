import time
import statistics


def benchmark_model(tokenizer, model, prompt: str, max_tokens: int, n_runs: int = None):
    from os import getenv

    n = int(n_runs or getenv("N_RUNS", 3))
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    times = []
    token_counts = []
    for _ in range(n):
        start = time.time()
        outputs = model.generate(**inputs, max_new_tokens=max_tokens)
        end = time.time()
        gen_time = end - start
        num_tokens = outputs[0].shape[-1] - inputs["input_ids"].shape[-1]
        times.append(gen_time)
        token_counts.append(num_tokens)

    avg_time = statistics.mean(times)
    avg_tokens = statistics.mean(token_counts)
    tokens_per_sec = avg_tokens / avg_time if avg_time > 0 else 0.0

    return {
        "avg_time": avg_time,
        "avg_tokens": avg_tokens,
        "tokens_per_sec": tokens_per_sec,
    }
