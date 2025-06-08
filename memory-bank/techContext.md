# Technical Context: IoT Temperature & Humidity Monitoring System

## 1. Core Technologies

-   **Python 3**: Used for the `sensor_simulator.py` script. Requires the `paho-mqtt` and `numpy` libraries.
-   **Docker & Docker Compose**: Used to containerize and orchestrate the backend services (Mosquitto and Node-RED).
-   **Eclipse Mosquitto**: A lightweight, open-source MQTT broker.
-   **Node-RED**: A flow-based programming tool built on Node.js. Used for data processing and creating the web dashboard.

## 2. Development Environment

-   **Virtual Environment**: A Python virtual environment (`venv`) is required to manage the dependencies for the IoT simulator and test script. This is necessary to avoid conflicts with the system's Python installation.
-   **Editor/IDE**: Any text editor or IDE can be used. The project is not tied to a specific one.
-   **Terminal**: A command-line interface is needed to run the Docker commands and the Python scripts.

## 3. Component Specifications

### IoT Device Simulator

-   **Sensor Data Generation**: Simulates a DHT22 temperature and humidity sensor with realistic noise and time-based variations.
-   **MQTT Message Structure**:
    ```json
    {
      "device_id": "raspberry_pi_001",
      "timestamp": "2024-01-01T12:00:00Z",
      "sensor_type": "temperature|humidity",
      "value": 23.5,
      "unit": "°C|%"
    }
    ```

### MQTT Broker (Eclipse Mosquitto)

-   **Topic Structure**:
    ```
    sensors/temperature
    sensors/humidity
    ```
-   **Quality of Service (QoS)**: The system uses QoS 1 for at-least-once message delivery.

### Node-RED Processing Engine

-   **Fire Detection**: A function node implements a threshold-based fire detection algorithm.
-   **Data Storage**: A circular buffer in the Node-RED context stores the last 1000 sensor readings for historical charts.

## 4. Key Configuration Files

-   `docker-compose.yml`: Defines the Mosquitto and Node-RED services, their ports, volumes, and network configuration.
-   `iot-device/config.json`: Configures the IoT device simulator, including the MQTT broker address, topics, and sensor parameters.
-   `nodered/data/flows.json`: Contains the Node-RED flow definitions, which control the data processing and dashboard layout.
-   `mosquitto/config/mosquitto.conf`: The configuration file for the Mosquitto MQTT broker.

## 5. Testing

-   `test_system.py`: A Python script that provides a comprehensive suite of tests for all system components. It checks the Docker containers, MQTT broker, Node-RED API, and Python dependencies.

## 6. Security Considerations

### Current Implementation (Development)

-   **Authentication**: None (anonymous access).
-   **Encryption**: None (plaintext communication).

### Production Recommendations

-   Implement MQTT authentication with username and password.
-   Enable TLS encryption for all MQTT traffic.
-   Configure topic-based Access Control Lists (ACLs) to restrict access to sensitive topics.
-   Secure the Node-RED admin interface with a password.
