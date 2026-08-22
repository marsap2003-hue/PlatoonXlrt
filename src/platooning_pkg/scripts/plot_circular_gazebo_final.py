import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


original_path = (
    "results/gazebo_circular_sync/"
    "gazebo_circular_original.csv"
)

improved_path = (
    "results/gazebo_circular_improved/"
    "gazebo_circular_improved.csv"
)

output_dir = "thesis_final_plots"
os.makedirs(output_dir, exist_ok=True)

original = pd.read_csv(original_path)
improved = pd.read_csv(improved_path)


# =========================================================
# 1. ORIGINAL VS IMPROVED SPACING ERROR
# =========================================================

fig, axes = plt.subplots(
    2,
    1,
    figsize=(10, 8),
    sharex=True
)

for i in range(1, 4):
    axes[0].plot(
        original["time"],
        original[f"error_slave{i}"],
        label=f"Slave {i}"
    )

axes[0].axvspan(
    10,
    15,
    alpha=0.15,
    label="Leader deceleration"
)

axes[0].set_ylabel("Spacing Error (m)")
axes[0].set_title(
    "Original Configuration – Constant Spacing"
)
axes[0].grid(True)
axes[0].legend()


for i in range(1, 4):
    axes[1].plot(
        improved["time"],
        improved[f"error_slave{i}"],
        label=f"Slave {i}"
    )

axes[1].axvspan(
    10,
    15,
    alpha=0.15,
    label="Leader deceleration"
)

axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Spacing Error (m)")
axes[1].set_title(
    "Improved Configuration – CTH, h = 1.25 s"
)
axes[1].grid(True)
axes[1].legend()

fig.suptitle(
    "Circular Gazebo Platoon: "
    "Original vs Improved Configuration"
)

fig.tight_layout()

fig.savefig(
    os.path.join(
        output_dir,
        "gazebo_circular_original_vs_improved.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# =========================================================
# 2. IMPROVED VEHICLE VELOCITIES
# =========================================================

fig, ax = plt.subplots(
    figsize=(10, 5.5)
)

ax.plot(
    improved["time"],
    improved["master_velocity"],
    label="Master"
)

for i in range(1, 4):
    ax.plot(
        improved["time"],
        improved[f"slave{i}_velocity"],
        label=f"Slave {i}"
    )

ax.axvspan(
    10,
    15,
    alpha=0.15,
    label="Leader deceleration"
)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Velocity (m/s)")
ax.set_title(
    "Vehicle Velocities – Improved Circular Gazebo Platoon"
)

ax.grid(True)
ax.legend()

fig.tight_layout()

fig.savefig(
    os.path.join(
        output_dir,
        "gazebo_circular_improved_velocities.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# =========================================================
# 3. ACTUAL VS DESIRED DISTANCES
# =========================================================

fig, ax = plt.subplots(
    figsize=(10, 5.5)
)

distance_columns = [
    "distance_master_slave1",
    "distance_slave1_slave2",
    "distance_slave2_slave3"
]

desired_columns = [
    "desired_distance_slave1",
    "desired_distance_slave2",
    "desired_distance_slave3"
]

for i in range(3):
    ax.plot(
        improved["time"],
        improved[distance_columns[i]],
        label=f"Actual distance {i + 1}"
    )

ax.plot(
    improved["time"],
    improved["desired_distance_slave1"],
    "--",
    linewidth=2,
    label="Desired distance"
)

ax.axvspan(
    10,
    15,
    alpha=0.15,
    label="Leader deceleration"
)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Inter-vehicle Distance (m)")

ax.set_title(
    "Inter-Vehicle Distances – "
    "Improved Circular Gazebo Platoon"
)

ax.grid(True)
ax.legend()

fig.tight_layout()

fig.savefig(
    os.path.join(
        output_dir,
        "gazebo_circular_improved_distances.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


print("Final circular Gazebo plots created:")
print(
    "  gazebo_circular_original_vs_improved.png"
)
print(
    "  gazebo_circular_improved_velocities.png"
)
print(
    "  gazebo_circular_improved_distances.png"
)
