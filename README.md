# Evaluation of RPL Objective Functions in Contiki

This repository contains the source code, simulation files, experiment logs, and FIT IoT-LAB node information used to evaluate two RPL Objective Functions: OF0 and MRHOF.

## Project Overview

The project compares OF0 and MRHOF in RPL using:

- Contiki-NG
- Cooja Simulator
- FIT IoT-LAB M3 nodes

The evaluation focuses on:

- Packet Delivery Ratio (PDR)
- End-to-End Delay
- Hop Count
- Preferred Parent Changes

Three network topologies are evaluated in Cooja:

- Line
- Grid
- Random

The implementation is also validated on FIT IoT-LAB using 15 M3 nodes at the Grenoble site.

## Repository Structure

```text
rpl-of0-mrhof-contiki/
├── cooja/
│   ├── of0/
│   ├── mrhof/
│   └── simulations/
├── fit-iotlab/
│   ├── of0/
│   └── mrhof/
├── logs/
│   ├── cooja/
│   └── fit-iotlab/
└── node-positions/
```

- `cooja/`: source code and simulation files used in Cooja.
- `fit-iotlab/`: source code used to compile firmware for FIT IoT-LAB M3 nodes.
- `logs/`: experiment logs collected from Cooja and FIT IoT-LAB.
- `node-positions/`: physical coordinates and node layout used in the FIT IoT-LAB experiment.

## Cooja Simulation

Each simulation uses 15 nodes:

- 1 RPL Root
- 14 UDP clients
- Routing protocol: RPL Lite
- Objective Functions: OF0 and MRHOF
- UDP sending interval: approximately 10 seconds with jitter
- Simulation duration: 5 minutes

OF0 and MRHOF are evaluated under the same topology and network configuration for each scenario.

## FIT IoT-LAB Experiment

The FIT IoT-LAB experiment uses 15 M3 nodes at the Grenoble site:

- Root: `m3-207`
- Clients: `m3-208` to `m3-221`
- Application: UDP Client/Server
- Routing: RPL Lite
- Duration: 5 minutes
- Objective Functions: OF0 and MRHOF

The same physical nodes are used for both Objective Functions.

## Build for FIT IoT-LAB

```bash
ARCH_PATH=../../../arch make TARGET=iotlab BOARD=m3 savetarget
ARCH_PATH=../../../arch make udp-server
ARCH_PATH=../../../arch make udp-client
```

OF0 and MRHOF are configured separately through `project-conf.h`.

## Log Collection on FIT IoT-LAB

Experiment logs are collected using `serial_aggregator`.

```bash
timeout 300 serial_aggregator -i <experiment_id> | tee <log_file>
```

The collected logs are used to analyze packet delivery and RPL routing behavior.

## Main Results

In the Cooja simulations, both OF0 and MRHOF achieved high Packet Delivery Ratio.

The main difference observed was routing stability:

- OF0 showed several Preferred Parent changes in the evaluated topologies.
- MRHOF did not show Preferred Parent changes after the initial DODAG formation in the evaluated scenarios.

End-to-End Delay and Hop Count were generally close between OF0 and MRHOF and did not show a consistent advantage for one Objective Function in every topology.

In the FIT IoT-LAB experiment, both OF0 and MRHOF achieved 100% uplink PDR. The selected M3 nodes used direct one-hop paths to the RPL Root during the measurement period.
