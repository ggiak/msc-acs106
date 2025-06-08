# IoT Sensor Simulator

A Node.js implementation of an IoT sensor simulator for temperature and humidity monitoring. This simulator mimics a Raspberry Pi with DHT22 sensor sending data via MQTT.

## Features

- Simulates temperature and humidity sensors with realistic variations
- Publishes sensor data to MQTT broker
- Configurable sensor parameters and simulation settings
- Generates anomalies for testing fire detection systems
- Time-based variations to simulate daily temperature cycles

## Prerequisites

- Node.js (version 14.0.0 or higher)
- npm (Node Package Manager)
- MQTT broker (e.g., Mosquitto) running locally or remotely

## Installation

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Install dependencies:

```bash
npm install
```

## Configuration

The simulator uses a `config.json` file for configuration. You can modify this file to change:

- Device information (ID, name, location)
- MQTT broker settings (host, port, topics)
- Sensor parameters (min/max values, thresholds)
- Simulation settings (interval, duration, anomalies)

Example configuration:

```json
{
  "device": {
    "id": "raspberry_pi_001",
    "name": "IoT Temperature & Humidity Sensor",
    "location": "Laboratory Room 101"
  },
  "mqtt": {
    "broker_host": "localhost",
    "broker_port": 1883,
    "topic_temperature": "sensors/temperature",
    "topic_humidity": "sensors/humidity",
    "qos": 1,
    "retain": false
  },
  "sensors": {
    "temperature": {
      "unit": "°C",
      "min_value": 15.0,
      "max_value": 35.0,
      "noise_factor": 0.5,
      "fire_threshold": 25.0
    },
    "humidity": {
      "unit": "%",
      "min_value": 30.0,
      "max_value": 80.0,
      "noise_factor": 2.0,
      "low_threshold": 20.0,
      "high_threshold": 85.0
    }
  },
  "simulation": {
    "publish_interval": 5,
    "simulation_duration": 3600,
    "enable_anomalies": true,
    "anomaly_probability": 0.05
  }
}
```

## Usage

Run the simulator:

```bash
npm start
```

Or directly:

```bash
node sensor_simulator.js
```

The simulator will:
1. Load the configuration from `config.json`
2. Connect to the MQTT broker
3. Start generating and publishing sensor data at the configured interval
4. Run for the configured duration or until manually stopped (Ctrl+C)

## MQTT Payload Format

The simulator publishes JSON payloads with the following structure:

### Temperature Payload

```json
{
  "device_id": "raspberry_pi_001",
  "device_name": "IoT Temperature & Humidity Sensor",
  "location": "Laboratory Room 101",
  "timestamp": "2023-05-15T14:30:45.123Z",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "°C",
  "quality": "good",
  "fire_threshold": 25.0,
  "fire_risk": false
}
```

### Humidity Payload

```json
{
  "device_id": "raspberry_pi_001",
  "device_name": "IoT Temperature & Humidity Sensor",
  "location": "Laboratory Room 101",
  "timestamp": "2023-05-15T14:30:45.123Z",
  "sensor_type": "humidity",
  "value": 45.2,
  "unit": "%",
  "quality": "good",
  "low_threshold": 20.0,
  "high_threshold": 85.0,
  "anomaly": false
}
```

## License

MIT