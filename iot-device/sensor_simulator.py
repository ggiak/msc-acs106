#!/usr/bin/env python3
"""
IoT Sensor Simulator for Temperature and Humidity Monitoring
Simulates a Raspberry Pi with DHT22 sensor sending data via MQTT

Author: MSC Student - IoT Exercise Implementation
Course: Advanced Computer Systems Technologies
University: University of West Attica
"""

import json
import time
import random
import math
import logging
from datetime import datetime
from typing import Dict, Any, Tuple
import paho.mqtt.client as mqtt
import numpy as np


class SensorSimulator:
    """
    Simulates temperature and humidity sensors on an IoT device.
    Publishes sensor data to MQTT broker with realistic variations and anomalies.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the sensor simulator with configuration.
        
        Args:
            config_file (str): Path to the configuration JSON file
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.config = self._load_config(config_file)
        self.mqtt_client = None
        self.running = False
        
        # Initialize sensor state variables
        self.temp_base = random.uniform(
            self.config["sensors"]["temperature"]["min_value"],
            self.config["sensors"]["temperature"]["max_value"]
        )
        self.humidity_base = random.uniform(
            self.config["sensors"]["humidity"]["min_value"],
            self.config["sensors"]["humidity"]["max_value"]
        )
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in configuration file {config_file}")
            raise
    
    def _setup_mqtt(self) -> None:
        """Setup MQTT client connection."""
        self.mqtt_client = mqtt.Client()
        
        # MQTT event handlers
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.logger.info("Connected to MQTT Broker successfully")
            else:
                self.logger.error(f"Failed to connect to MQTT Broker. Return code: {rc}")
        
        def on_disconnect(client, userdata, rc):
            self.logger.info("Disconnected from MQTT Broker")
        
        def on_publish(client, userdata, mid):
            self.logger.debug(f"Message published with mid: {mid}")
        
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_disconnect = on_disconnect
        self.mqtt_client.on_publish = on_publish
        
        # Connect to broker
        try:
            self.mqtt_client.connect(
                self.config["mqtt"]["broker_host"],
                self.config["mqtt"]["broker_port"],
                60
            )
            self.mqtt_client.loop_start()
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def _generate_sensor_data(self) -> Tuple[float, float]:
        """
        Generate realistic temperature and humidity sensor readings.
        
        Returns:
            Tuple[float, float]: Temperature and humidity values
        """
        # Time-based variation (simulates daily temperature cycle)
        time_factor = math.sin(time.time() / 3600 * math.pi / 12) * 3  # 24-hour cycle
        
        # Generate temperature with noise and time variation
        temp_noise = random.gauss(0, self.config["sensors"]["temperature"]["noise_factor"])
        temperature = self.temp_base + time_factor + temp_noise
        
        # Generate humidity with inverse correlation to temperature
        humidity_base = self.humidity_base - (temperature - self.temp_base) * 2
        humidity_noise = random.gauss(0, self.config["sensors"]["humidity"]["noise_factor"])
        humidity = humidity_base + humidity_noise
        
        # Apply realistic constraints
        temperature = max(
            self.config["sensors"]["temperature"]["min_value"] - 5,
            min(self.config["sensors"]["temperature"]["max_value"] + 5, temperature)
        )
        humidity = max(0, min(100, humidity))
        
        # Generate anomalies for testing fire detection
        if (self.config["simulation"]["enable_anomalies"] and 
            random.random() < self.config["simulation"]["anomaly_probability"]):
            
            anomaly_type = random.choice(["fire", "humidity_drop", "humidity_spike"])
            
            if anomaly_type == "fire":
                temperature += random.uniform(15, 25)  # Fire simulation
                humidity *= 0.6  # Humidity drops in fire
                self.logger.warning("🔥 ANOMALY: Fire condition simulated!")
                
            elif anomaly_type == "humidity_drop":
                humidity = random.uniform(5, 15)  # Very low humidity
                self.logger.warning("💧 ANOMALY: Low humidity condition simulated!")
                
            elif anomaly_type == "humidity_spike":
                humidity = random.uniform(90, 100)  # Very high humidity
                self.logger.warning("💧 ANOMALY: High humidity condition simulated!")
        
        return round(temperature, 1), round(humidity, 1)
    
    def _create_mqtt_payload(self, sensor_type: str, value: float, unit: str) -> str:
        """
        Create MQTT message payload in JSON format.
        
        Args:
            sensor_type (str): Type of sensor (temperature/humidity)
            value (float): Sensor reading value
            unit (str): Unit of measurement
            
        Returns:
            str: JSON formatted payload
        """
        payload = {
            "device_id": self.config["device"]["id"],
            "device_name": self.config["device"]["name"],
            "location": self.config["device"]["location"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "quality": "good"
        }
        
        # Add additional metadata for fire detection
        if sensor_type == "temperature":
            payload["fire_threshold"] = self.config["sensors"]["temperature"]["fire_threshold"]
            payload["fire_risk"] = value >= self.config["sensors"]["temperature"]["fire_threshold"]
        elif sensor_type == "humidity":
            payload["low_threshold"] = self.config["sensors"]["humidity"]["low_threshold"]
            payload["high_threshold"] = self.config["sensors"]["humidity"]["high_threshold"]
            payload["anomaly"] = (value <= self.config["sensors"]["humidity"]["low_threshold"] or 
                                value >= self.config["sensors"]["humidity"]["high_threshold"])
        
        return json.dumps(payload, indent=2)
    
    def _publish_sensor_data(self, temperature: float, humidity: float) -> None:
        """
        Publish sensor data to MQTT topics.
        
        Args:
            temperature (float): Temperature reading
            humidity (float): Humidity reading
        """
        if not self.mqtt_client:
            self.logger.error("MQTT client not initialized")
            return
        
        # Publish temperature data
        temp_payload = self._create_mqtt_payload(
            "temperature", 
            temperature, 
            self.config["sensors"]["temperature"]["unit"]
        )
        temp_result = self.mqtt_client.publish(
            self.config["mqtt"]["topic_temperature"],
            temp_payload,
            qos=self.config["mqtt"]["qos"],
            retain=self.config["mqtt"]["retain"]
        )
        
        # Publish humidity data
        humidity_payload = self._create_mqtt_payload(
            "humidity", 
            humidity, 
            self.config["sensors"]["humidity"]["unit"]
        )
        humidity_result = self.mqtt_client.publish(
            self.config["mqtt"]["topic_humidity"],
            humidity_payload,
            qos=self.config["mqtt"]["qos"],
            retain=self.config["mqtt"]["retain"]
        )
        
        # Log the published data
        self.logger.info(
            f"📊 Published: Temp={temperature}°C, Humidity={humidity}% "
            f"[Fire Risk: {temperature >= self.config['sensors']['temperature']['fire_threshold']}]"
        )
        
        if temp_result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.logger.error(f"Failed to publish temperature data: {temp_result.rc}")
        if humidity_result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.logger.error(f"Failed to publish humidity data: {humidity_result.rc}")
    
    def start_simulation(self) -> None:
        """Start the sensor simulation loop."""
        self.logger.info(f"🚀 Starting IoT Sensor Simulation for device: {self.config['device']['id']}")
        self.logger.info(f"📍 Location: {self.config['device']['location']}")
        self.logger.info(f"⏱️  Publishing interval: {self.config['simulation']['publish_interval']} seconds")
        
        self._setup_mqtt()
        self.running = True
        
        start_time = time.time()
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                
                # Generate and publish sensor data
                temperature, humidity = self._generate_sensor_data()
                self._publish_sensor_data(temperature, humidity)
                
                # Check if simulation duration is reached
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.config["simulation"]["simulation_duration"]:
                    self.logger.info(f"✅ Simulation completed after {elapsed_time:.1f} seconds ({iteration} iterations)")
                    break
                
                # Wait for next iteration
                time.sleep(self.config["simulation"]["publish_interval"])
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Simulation stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Simulation error: {e}")
        finally:
            self.stop_simulation()
    
    def stop_simulation(self) -> None:
        """Stop the sensor simulation and cleanup."""
        self.running = False
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        self.logger.info("🔌 Sensor simulation stopped and MQTT connection closed")


import os

def main():
    """Main function to run the sensor simulator."""
    print("🌡️  IoT Temperature & Humidity Sensor Simulator")
    print("=" * 50)
    print("University of West Attica - MSC IoT Exercise")
    print("Advanced Computer Systems Technologies")
    print("=" * 50)
    
    try:
        # Change to the script's directory to ensure config.json is found
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Create and start the sensor simulator
        simulator = SensorSimulator()
        simulator.start_simulation()
        
    except FileNotFoundError:
        print("❌ Error: config.json file not found!")
        print("Make sure the configuration file exists in the same directory.")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in config.json!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
