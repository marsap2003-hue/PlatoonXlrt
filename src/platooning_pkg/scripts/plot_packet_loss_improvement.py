import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

original_path = os.path.join(
    BASE_DIR,
    "results/packet_loss/original_h100/slave1_original_loss40.csv"
)

improved_path = os.path.join(
    BASE_DIR,
    "results/packet_loss/improved_h125/slave1_improved_loss40.csv"
)

original = pd.read_csv(original_path)
improved = pd.read_csv(improved_path)

mask_original = (
    (original["time"] >= 8.0) &
    (original["time"] <= 22.0)
)

mask_improved = (
    (improved["time"] >= 8.0) &
    (improved["time"] <= 22.0)
)

plt.figure(figsize=(10, 6))

plt.plot(
    original.loc[mask_original, "time"],
    original.loc[mask_original, "distance_error"],
    label="Original (h = 1.00 s)",
    linewidth=2
)

plt.plot(
    improved.loc[mask_improved, "time"],
    improved.loc[mask_improved, "distance_error"],
    label="Improved (h = 1.25 s)",
    linewidth=2
)

plt.axhline(0, linestyle="--", linewidth=1)

plt.axvline(10, linestyle=":", linewidth=1)
plt.axvline(15, linestyle=":", linewidth=1)

plt.xlabel("Simulation Time (s)")
plt.ylabel("Spacing Error (m)")

plt.title(
    "Original vs Improved Configuration "
    "(Packet Loss = 40%)"
)

plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(8, 22)

plt.tight_layout()

output_path = os.path.join(
    BASE_DIR,
    "results/packet_loss",
    "original_vs_improved_loss40.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved plot to: {output_path}")

plt.show()
