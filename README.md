# Fleet Management System

A multi-robot coordination system built with PyQt6 and NetworkX, designed to manage autonomous robots navigating through a predefined network topology.

## Overview

Core functionalities:
- Fleet management with real-time visualization
- Path planning and traffic coordination
- Collision avoidance system
- System monitoring and logging

## Technical Requirements

- Python 3.8+
- PyQt6 6.6.1
- NetworkX 3.2.1
- NumPy 1.26.0
- Matplotlib 3.7.1

## Setup

1. Python environment setup:
```bash
git clone https://github.com/Vismayavinodk/GoatPSGHackathon_22PT39
cd fleet-management-system
pip install -r requirements.txt
```

2. Run application:
```bash
python -m src.main
```

## Core Features

### Visualization
- Network topology representation
- Robot state visualization
- Path planning display
- Status monitoring

### Robot Control
- Vertex-based robot deployment
- Task assignment system
- State management
- Position tracking

### Traffic System
- Path planning algorithms
- Intersection management
- Collision prevention
- Occupancy tracking

### Monitoring
- Status tracking
- Event logging
- Error handling
- Performance metrics

## Interface Guide

### Basic Controls
- Vertex Click: Deploy robot
- Robot Click: Select unit
- Vertex Click (with selection): Set destination
- Control Panel: System management

### Interface Elements
- Network Nodes: Location markers (L0-Ln)
- Connections: Path segments
- Robot Units: Mobile agents (R0-Rn)
- Status Display: System state

### Robot States
- IDLE: Awaiting commands
- MOVING: In transit
- WAITING: Temporary hold
- BLOCKED: Path obstruction
- COMPLETE: Task finished
- ERROR: Malfunction

### System Panels
- Status: Current system state
- Logs: Operation history
- Controls: Management interface

## System Architecture

```
src/
├── main.py              # Entry point
├── controllers/         # System control
│   ├── fleet_manager.py    # Robot management
│   └── traffic_manager.py  # Traffic control
├── gui/                # Interface
│   └── fleet_gui.py       # GUI implementation
├── models/             # Core components
│   ├── robot.py          # Robot logic
│   └── nav_graph.py      # Network structure
└── utils/              # Support modules
    └── logger.py         # System logging
```

## Technical Implementation

### GUI Implementation
- PyQt6 NetworkView for graph rendering
- Status panel with robot state counters
- Log panel showing system events
- Control buttons for robot operations

### Robot System
- Vertex-to-vertex movement
- Path following with progress tracking
- Status-based color indicators
- Task queue management

### Traffic Control
- Edge occupancy checking
- Intersection blocking
- Robot state management (IDLE/MOVING/WAITING/BLOCKED)
- Basic collision prevention

### Core System
- Event-based logging
- Robot state updates
- Path assignment handling
- Error state management

## Development

Vismaya K
March 2024 
