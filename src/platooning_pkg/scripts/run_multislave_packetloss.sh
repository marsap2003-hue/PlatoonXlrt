#!/bin/bash

cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

echo "======================================"
echo " MULTI-VEHICLE PACKET LOSS EXPERIMENTS"
echo "======================================"

run_test () {

    LOSS=$1
    HEADWAY=$2
    NAME=$3

    echo ""
    echo "======================================"
    echo "Run: ${NAME}"
    echo "Loss: ${LOSS}"
    echo "Headway: ${HEADWAY}"
    echo "======================================"

    timeout --signal=SIGINT --kill-after=5s 33s \
        ros2 launch platooning_pkg multislave_packetloss.launch.py \
        loss:=$LOSS \
        headway:=$HEADWAY \
        run_name:=$NAME \
        seed:=1 \
        > "${NAME}.log" 2>&1

    pkill -f string_master_node 2>/dev/null || true
    pkill -f multi_slave_packetloss 2>/dev/null || true

    sleep 2

    echo "Completed: ${NAME}"
}


# Original controller: h = 1.0
run_test 0.00 1.00 original_loss0
run_test 0.10 1.00 original_loss10
run_test 0.20 1.00 original_loss20
run_test 0.40 1.00 original_loss40

# Improved candidate: h = 1.25
run_test 0.00 1.25 improved_loss0
run_test 0.10 1.25 improved_loss10
run_test 0.20 1.25 improved_loss20
run_test 0.40 1.25 improved_loss40


echo ""
echo "======================================"
echo " ALL PACKET LOSS EXPERIMENTS COMPLETED"
echo "======================================"
