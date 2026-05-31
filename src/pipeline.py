import subprocess
import sys

steps = [
    ["python", "src/collector.py"],
    ["python", "src/cleaner.py"],
    ["python", "src/extractor.py"],
    ["python", "src/analyzer.py"],
]

for step in steps:
    print(f"\n>>> Running {step[1]}...")
    result = subprocess.run(step, check=True)
    print(f"✓ Done: {step[1]}")

print("\n✅ Pipeline complete.")