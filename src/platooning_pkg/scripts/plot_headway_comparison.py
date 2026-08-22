import os
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results", "headway_sweep")

files = {
    "h = 1.00 s": "slave1_headway_h100.csv",
    "h = 1.25 s": "slave1_headway_h125.csv",
    "h = 1.50 s": "slave1_headway_h150.csv",
    "h = 1.75 s": "slave1_headway_h175.csv",
    "h = 2.00 s": "slave1_headway_h200.csv",
}

plt.figure(figsize=(10, 6))

for label, filename in files.items():

    path = os.path.join(RESULTS_DIR, filename)
    data = pd.read_csv(path)

    time = data["control_time"]

    # Focus on the Master disturbance and recovery
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
    "Effect of Time Headway on Slave 1 "
    "(Communication Delay = 1000 ms)"
)

plt.legend(
    title="Time Headway"
)

plt.grid(True, alpha=0.3)
plt.xlim(8, 22)

plt.tight_layout()

output_path = os.path.join(
    RESULTS_DIR,
    "headway_comparison_slave1.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved plot to: {output_path}")

plt.show()
