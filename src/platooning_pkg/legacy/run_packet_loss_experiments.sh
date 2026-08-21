#!/bin/bash

cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

echo "======================================"
echo " PACKET LOSS EXPERIMENTS"
echo "======================================"

run_experiment () {

    LOSS=$1
    LABEL=$2
    RUN=$3
    SEED=$4

    RUN_NAME="loss${LABEL}_run${RUN}"

    echo ""
    echo "======================================"
    echo "Starting: $RUN_NAME"
    echo "Packet loss: $LOSS"
    echo "Random seed: $SEED"
    echo "======================================"

    # Start Master in background
    ros2 run platooning_pkg master_node > "${RUN_NAME}_master.log" 2>&1 &
    MASTER_PID=$!

    # Small delay so Master starts first
    sleep 0.5

    # Start Slave in background
    ros2 run platooning_pkg slave_node --ros-args \
        -p packet_loss_probability:=$LOSS \
        -p random_seed:=$SEED \
        -p run_name:=$RUN_NAME \
        > "${RUN_NAME}_slave.log" 2>&1 &

    SLAVE_PID=$!

    # Wait until both nodes finish automatically
    wait $MASTER_PID
    wait $SLAVE_PID

    echo "Completed: $RUN_NAME"

    # Give ROS a moment before next experiment
    sleep 1
}


# ----------------------------
# 10% packet loss
# Run 1 already completed
# ----------------------------

run_experiment 0.10 10 2 2
run_experiment 0.10 10 3 3
run_experiment 0.10 10 4 4
run_experiment 0.10 10 5 5


# ----------------------------
# 20% packet loss
# ----------------------------

run_experiment 0.20 20 1 1
run_experiment 0.20 20 2 2
run_experiment 0.20 20 3 3
run_experiment 0.20 20 4 4
run_experiment 0.20 20 5 5


# ----------------------------
# 40% packet loss
# ----------------------------

run_experiment 0.40 40 1 1
run_experiment 0.40 40 2 2
run_experiment 0.40 40 3 3
run_experiment 0.40 40 4 4
run_experiment 0.40 40 5 5


echo ""
echo "======================================"
echo " ALL EXPERIMENTS COMPLETED"
echo "======================================"
