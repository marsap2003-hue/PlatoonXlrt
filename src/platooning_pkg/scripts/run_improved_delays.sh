#!/bin/bash

cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

echo "======================================"
echo " IMPROVED CONTROLLER - h = 1.25 s"
echo "======================================"

run_test () {

    DELAY=$1
    NAME=$2

    echo ""
    echo "======================================"
    echo "Starting: ${NAME}"
    echo "Delay: ${DELAY} s"
    echo "Headway: 1.25 s"
    echo "======================================"

    timeout --signal=SIGINT --kill-after=5s 33s \
        ros2 launch platooning_pkg improved_delay.launch.py \
        delay:=$DELAY \
        run_name:=$NAME \
        > "improved_${NAME}.log" 2>&1

    pkill -f string_master_node 2>/dev/null || true
    pkill -f adaptive_slave_node 2>/dev/null || true

    sleep 2

    echo "Completed: ${NAME}"
}


run_test 0.0 delay0
run_test 0.2 delay200
run_test 0.5 delay500
run_test 1.0 delay1000


echo ""
echo "======================================"
echo " ALL IMPROVED EXPERIMENTS COMPLETED"
echo "======================================"
