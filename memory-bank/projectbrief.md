# Project Brief: IoT Temperature & Humidity Monitoring System

## 1. Project Overview

This project implements a complete IoT solution for real-time temperature and humidity monitoring, featuring a fire detection system. It is designed for educational purposes within the MSC Advanced Computer Systems Technologies program at the University of West Attica. The system is containerized using Docker for portability and ease of deployment.

## 2. Core Requirements

- **Real-time Data Monitoring**: Continuously track temperature and humidity from a simulated IoT device.
- **Data Visualization**: Provide a web-based dashboard with live gauges and historical charts.
- **Fire Detection**: Implement a threshold-based alert system for high temperatures.
- **Containerized Deployment**: All services (MQTT broker, Node-RED) must run in Docker containers.
- **System Verification**: Include a test script to validate the functionality of all components.

## 3. System Architecture

The system consists of three main components:

1.  **IoT Device**: A Python script that simulates a temperature and humidity sensor and publishes data to an MQTT broker.
2.  **MQTT Broker**: An Eclipse Mosquitto server that handles message passing between the IoT device and the Node-RED server.
3.  **Node-RED Server**: A flow-based development tool that processes the sensor data, triggers alerts, and serves the web dashboard.

## 4. Key Technologies

- **Python**: For the IoT device simulator.
- **Docker**: For containerization and service orchestration.
- **Eclipse Mosquitto**: As the MQTT message broker.
- **Node-RED**: For data processing and visualization.
- **MQTT**: As the communication protocol.
- **JSON**: As the data serialization format.
