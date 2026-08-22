import os
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

original_path = os.path.join(
    BASE_DIR,
    "results",
    "delay",
    "slave1_string_delay1000.csv"
)

improved_path = os.path.join(
    BASE_DIR,
    "results",
    "improved_delay",
    "slave1_improved_delay1000.csv"
)

original = pd.read_csv(original_path)
improved = pd.read_csv(improved_path)

plt.figure(figsize=(10, 6))

# Focus on disturbance and recovery interval
mask_original = (
    (original["control_time"] >= 8.0) &
    (original["control_time"] <= 22.0)
)

mask_improved = (
    (improved["control_time"] >= 8.0) &
    (improved["control_time"] <= 22.0)
)

plt.plot(
    original.loc[mask_original, "control_time"],
    original.loc[mask_original, "distance_error"],
    label="Original (h = 1.00 s)",
    linewidth=2
)

plt.plot(
    improved.loc[mask_improved, "control_time"],
    improved.loc[mask_improved, "distance_error"],
    label="Improved (h = 1.25 s)",
    linewidth=2
)

# Zero-error reference
plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

# Master braking interval
plt.axvline(
    10,
    linestyle=":",
    linewidth=1
)

plt.axvline(
    15,
    linestyle=":",
    linewidth=1
)

plt.xlabel("Simulation Time (s)")
plt.ylabel("Spacing Error (m)")

plt.title(
    "Original vs Improved Configuration "
    "(Communication Delay = 1000 ms)"
)

plt.legend()

plt.grid(True, alpha=0.3)
plt.xlim(8, 22)

plt.tight_layout()

output_path = os.path.join(
    BASE_DIR,
    "results",
    "improved_delay",
    "original_vs_improved_delay1000.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved plot to: {output_path}")

plt.show()
