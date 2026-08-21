#!/bin/bash

cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

echo "======================================"
echo " HEADWAY SWEEP - DELAY = 1000 ms"
echo "======================================"

run_headway () {

    HEADWAY=$1
    NAME=$2

    echo ""
    echo "======================================"
    echo "Running headway = ${HEADWAY} s"
    echo "======================================"

    timeout --signal=SIGINT --kill-after=5s 33s \
        ros2 launch platooning_pkg headway_sweep.launch.py \
        headway:=$HEADWAY \
        run_name:=$NAME \
        > "headway_${NAME}.log" 2>&1

    # Ensure no nodes remain from previous experiment
    pkill -f string_master_node 2>/dev/null || true
    pkill -f adaptive_slave_node 2>/dev/null || true

    sleep 2

    echo "Completed headway = ${HEADWAY} s"
}


run_headway 1.00 h100
run_headway 1.25 h125
run_headway 1.50 h150
run_headway 1.75 h175
run_headway 2.00 h200

echo ""
echo "======================================"
echo " ALL HEADWAY EXPERIMENTS COMPLETED"
echo "======================================"
