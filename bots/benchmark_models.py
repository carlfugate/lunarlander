#!/usr/bin/env python3
"""Benchmark Ollama models for Lunar Lander"""
import requests
import time
import subprocess

def get_installed_models():
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]
    return [line.split()[0] for line in lines if line.strip()]

def benchmark_model(model, prompt):
    """Test model speed"""
    times = []
    for i in range(5):
        start = time.time()
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 30}
                },
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.0f}ms")
        except Exception as e:
            print(f"  Run {i+1}: FAILED ({e})")
            times.append(None)
    
    valid = [t for t in times if t is not None]
    if valid:
        return sum(valid) / len(valid)
    return None

if __name__ == "__main__":
    prompt = """Lander: Alt=450m Speed=3.2 Vx=1.5 Vy=2.8 Angle=5° Fuel=950 XErr=-45m

Safe: Speed<5, Angle<17°
Strategy: High(>300m)→fall. Med(150-300)→thrust if Vy>5. Low(<150)→thrust if Speed>4.

Reply JSON: ["thrust_on"/"thrust_off", "rotate_left"/"rotate_right"/"rotate_stop"]
"""
    
    models = get_installed_models()
    print(f"Testing {len(models)} models with Lunar Lander prompt...\n")
    
    results = []
    for model in models:
        print(f"Testing {model}:")
        avg = benchmark_model(model, prompt)
        if avg:
            results.append((model, avg))
            print(f"  Average: {avg:.0f}ms\n")
        else:
            print(f"  FAILED\n")
    
    print("\n=== RESULTS ===")
    results.sort(key=lambda x: x[1])
    for model, avg in results:
        hz = 1000 / avg if avg < 500 else 0
        status = "✓" if avg < 100 else "⚠" if avg < 200 else "✗"
        print(f"{status} {model:20s} {avg:6.0f}ms  (max {hz:.1f}Hz)")
    
    print("\n✓ = Good for 10Hz")
    print("⚠ = Good for 5Hz")
    print("✗ = Too slow (2-3Hz max)")
