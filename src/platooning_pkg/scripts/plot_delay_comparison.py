import os
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results", "delay")

files = {
    "0 ms": "slave1_string_baseline_new.csv",
    "200 ms": "slave1_string_delay200.csv",
    "500 ms": "slave1_string_delay500.csv",
    "1000 ms": "slave1_string_delay1000.csv",
}

plt.figure(figsize=(10, 6))

for label, filename in files.items():

    path = os.path.join(RESULTS_DIR, filename)
    data = pd.read_csv(path)

    # All final datasets use control_time
    time = data["control_time"]

    # Focus on the controlled Master disturbance,
    # excluding the initialization transient.
    mask = (time >= 8.0) & (time <= 22.0)

    plt.plot(
        time[mask],
        data.loc[mask, "distance_error"],
        label=label,
        linewidth=2
    )

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
plt.title("Effect of Communication Delay on Slave 1")

plt.legend(
    title="Communication Delay"
)

plt.grid(True, alpha=0.3)

plt.xlim(8, 22)

plt.tight_layout()

output_path = os.path.join(
    RESULTS_DIR,
    "delay_comparison_slave1.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved plot to: {output_path}")

plt.show()
