import os
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results",
    "packet_loss",
    "original_h100"
)

files = {
    "0%": "slave1_original_loss0.csv",
    "10%": "slave1_original_loss10.csv",
    "20%": "slave1_original_loss20.csv",
    "40%": "slave1_original_loss40.csv",
}

plt.figure(figsize=(10, 6))

for label, filename in files.items():

    path = os.path.join(RESULTS_DIR, filename)
    data = pd.read_csv(path)

    time = data["time"]

    # Focus on disturbance and recovery interval
    mask = (time >= 8.0) & (time <= 22.0)

    plt.plot(
        time[mask],
        data.loc[mask, "distance_error"],
        label=label,
        linewidth=2
    )

# Zero spacing-error reference
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
    "Effect of Packet Loss on Slave 1 "
    "(Original Configuration, h = 1.00 s)"
)

plt.legend(
    title="Packet Loss Probability"
)

plt.grid(True, alpha=0.3)
plt.xlim(8, 22)

plt.tight_layout()

output_path = os.path.join(
    RESULTS_DIR,
    "packet_loss_comparison_slave1.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved plot to: {output_path}")

plt.show()
