#!/usr/bin/env node

/**
 * IoT Sensor Simulator for Temperature and Humidity Monitoring
 * Simulates a Raspberry Pi with DHT22 sensor sending data via MQTT
 * 
 * Author: MSC Student - IoT Exercise Implementation
 * Course: Advanced Computer Systems Technologies
 * University: University of West Attica
 */

const fs = require('fs');
const path = require('path');
const mqtt = require('mqtt');

class SensorSimulator {
    /**
     * Simulates temperature and humidity sensors on an IoT device.
     * Publishes sensor data to MQTT broker with realistic variations and anomalies.
     */
    constructor(configFile = 'config.json') {
        // Setup logging
        this.logger = {
            info: (message) => console.log(`${new Date().toISOString()} - INFO - ${message}`),
            warn: (message) => console.log(`${new Date().toISOString()} - WARN - ${message}`),
            error: (message) => console.error(`${new Date().toISOString()} - ERROR - ${message}`),
            debug: (message) => console.debug(`${new Date().toISOString()} - DEBUG - ${message}`)
        };
        
        this.config = this._loadConfig(configFile);
        this.mqttClient = null;
        this.running = false;
        
        // Initialize sensor state variables
        this.tempBase = this._getRandomInRange(
            this.config.sensors.temperature.min_value,
            this.config.sensors.temperature.max_value
        );
        this.humidityBase = this._getRandomInRange(
            this.config.sensors.humidity.min_value,
            this.config.sensors.humidity.max_value
        );
    }
    
    _loadConfig(configFile) {
        /**
         * Load configuration from JSON file.
         */
        try {
            const configPath = path.resolve(configFile);
            const configData = fs.readFileSync(configPath, 'utf8');
            return JSON.parse(configData);
        } catch (error) {
            if (error.code === 'ENOENT') {
                this.logger.error(`Configuration file ${configFile} not found`);
            } else if (error instanceof SyntaxError) {
                this.logger.error(`Invalid JSON in configuration file ${configFile}`);
            } else {
                this.logger.error(`Error loading configuration: ${error.message}`);
            }
            throw error;
        }
    }
    
    _getRandomInRange(min, max) {
        /**
         * Get a random number within a specified range.
         */
        return min + Math.random() * (max - min);
    }
    
    _setupMqtt() {
        /**
         * Setup MQTT client connection.
         */
        const mqttUrl = `mqtt://${this.config.mqtt.broker_host}:${this.config.mqtt.broker_port}`;
        
        this.mqttClient = mqtt.connect(mqttUrl, {
            clientId: `sensor_simulator_${this.config.device.id}_${Math.random().toString(16).substr(2, 8)}`,
            clean: true,
            connectTimeout: 4000,
            reconnectPeriod: 1000
        });
        
        this.mqttClient.on('connect', () => {
            this.logger.info('Connected to MQTT Broker successfully');
        });
        
        this.mqttClient.on('error', (error) => {
            this.logger.error(`MQTT connection error: ${error.message}`);
        });
        
        this.mqttClient.on('disconnect', () => {
            this.logger.info('Disconnected from MQTT Broker');
        });
        
        this.mqttClient.on('close', () => {
            this.logger.info('MQTT connection closed');
        });
    }
    
    _generateSensorData() {
        /**
         * Generate realistic temperature and humidity sensor readings.
         * 
         * Returns:
         *   Object: Temperature and humidity values
         */
        // Time-based variation (simulates daily temperature cycle)
        const timeFactor = Math.sin(Date.now() / 3600000 * Math.PI / 12) * 3;  // 24-hour cycle
        
        // Generate temperature with noise and time variation
        const tempNoise = this._gaussianRandom(0, this.config.sensors.temperature.noise_factor);
        let temperature = this.tempBase + timeFactor + tempNoise;
        
        // Generate humidity with inverse correlation to temperature
        const humidityBase = this.humidityBase - (temperature - this.tempBase) * 2;
        const humidityNoise = this._gaussianRandom(0, this.config.sensors.humidity.noise_factor);
        let humidity = humidityBase + humidityNoise;
        
        // Apply realistic constraints
        temperature = Math.max(
            this.config.sensors.temperature.min_value - 5,
            Math.min(this.config.sensors.temperature.max_value + 5, temperature)
        );
        humidity = Math.max(0, Math.min(100, humidity));
        
        // Generate anomalies for testing fire detection
        if (this.config.simulation.enable_anomalies && 
            Math.random() < this.config.simulation.anomaly_probability) {
            
            const anomalyTypes = ['fire', 'humidity_drop', 'humidity_spike'];
            const anomalyType = anomalyTypes[Math.floor(Math.random() * anomalyTypes.length)];
            
            if (anomalyType === 'fire') {
                temperature += this._getRandomInRange(15, 25);  // Fire simulation
                humidity *= 0.6;  // Humidity drops in fire
                this.logger.warn('🔥 ANOMALY: Fire condition simulated!');
                
            } else if (anomalyType === 'humidity_drop') {
                humidity = this._getRandomInRange(5, 15);  // Very low humidity
                this.logger.warn('💧 ANOMALY: Low humidity condition simulated!');
                
            } else if (anomalyType === 'humidity_spike') {
                humidity = this._getRandomInRange(90, 100);  // Very high humidity
                this.logger.warn('💧 ANOMALY: High humidity condition simulated!');
            }
        }
        
        return {
            temperature: parseFloat(temperature.toFixed(1)),
            humidity: parseFloat(humidity.toFixed(1))
        };
    }
    
    _gaussianRandom(mean, stdev) {
        /**
         * Generate a random number with Gaussian distribution.
         * Using Box-Muller transform.
         */
        const u = 1 - Math.random(); // Converting [0,1) to (0,1]
        const v = Math.random();
        const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        return z * stdev + mean;
    }
    
    _createMqttPayload(sensorType, value, unit) {
        /**
         * Create MQTT message payload in JSON format.
         * 
         * Args:
         *   sensorType (string): Type of sensor (temperature/humidity)
         *   value (float): Sensor reading value
         *   unit (string): Unit of measurement
         *            
         * Returns:
         *   string: JSON formatted payload
         */
        const payload = {
            device_id: this.config.device.id,
            device_name: this.config.device.name,
            location: this.config.device.location,
            timestamp: new Date().toISOString(),
            sensor_type: sensorType,
            value: value,
            unit: unit,
            quality: 'good'
        };
        
        // Add additional metadata for fire detection
        if (sensorType === 'temperature') {
            payload.fire_threshold = this.config.sensors.temperature.fire_threshold;
            payload.fire_risk = value >= this.config.sensors.temperature.fire_threshold;
        } else if (sensorType === 'humidity') {
            payload.low_threshold = this.config.sensors.humidity.low_threshold;
            payload.high_threshold = this.config.sensors.humidity.high_threshold;
            payload.anomaly = (value <= this.config.sensors.humidity.low_threshold || 
                              value >= this.config.sensors.humidity.high_threshold);
        }
        
        return JSON.stringify(payload, null, 2);
    }
    
    _publishSensorData(temperature, humidity) {
        /**
         * Publish sensor data to MQTT topics.
         * 
         * Args:
         *   temperature (float): Temperature reading
         *   humidity (float): Humidity reading
         */
        if (!this.mqttClient) {
            this.logger.error('MQTT client not initialized');
            return;
        }
        
        // Publish temperature data
        const tempPayload = this._createMqttPayload(
            'temperature', 
            temperature, 
            this.config.sensors.temperature.unit
        );
        
        this.mqttClient.publish(
            this.config.mqtt.topic_temperature,
            tempPayload,
            { 
                qos: this.config.mqtt.qos,
                retain: this.config.mqtt.retain
            },
            (error) => {
                if (error) {
                    this.logger.error(`Failed to publish temperature data: ${error.message}`);
                }
            }
        );
        
        // Publish humidity data
        const humidityPayload = this._createMqttPayload(
            'humidity', 
            humidity, 
            this.config.sensors.humidity.unit
        );
        
        this.mqttClient.publish(
            this.config.mqtt.topic_humidity,
            humidityPayload,
            { 
                qos: this.config.mqtt.qos,
                retain: this.config.mqtt.retain
            },
            (error) => {
                if (error) {
                    this.logger.error(`Failed to publish humidity data: ${error.message}`);
                }
            }
        );
        
        // Log the published data
        this.logger.info(
            `📊 Published: Temp=${temperature}°C, Humidity=${humidity}% ` +
            `[Fire Risk: ${temperature >= this.config.sensors.temperature.fire_threshold}]`
        );
    }
    
    startSimulation() {
        /**
         * Start the sensor simulation loop.
         */
        this.logger.info(`🚀 Starting IoT Sensor Simulation for device: ${this.config.device.id}`);
        this.logger.info(`📍 Location: ${this.config.device.location}`);
        this.logger.info(`⏱️ Publishing interval: ${this.config.simulation.publish_interval} seconds`);
        
        this._setupMqtt();
        this.running = true;
        
        const startTime = Date.now();
        let iteration = 0;
        
        // Define the simulation interval
        const simulationInterval = setInterval(() => {
            if (!this.running) {
                clearInterval(simulationInterval);
                return;
            }
            
            iteration += 1;
            
            // Generate and publish sensor data
            const { temperature, humidity } = this._generateSensorData();
            this._publishSensorData(temperature, humidity);
            
            // Check if simulation duration is reached
            const elapsedTime = (Date.now() - startTime) / 1000;
            if (elapsedTime >= this.config.simulation.simulation_duration) {
                this.logger.info(`✅ Simulation completed after ${elapsedTime.toFixed(1)} seconds (${iteration} iterations)`);
                this.stopSimulation();
                clearInterval(simulationInterval);
            }
        }, this.config.simulation.publish_interval * 1000);
        
        // Handle process termination
        process.on('SIGINT', () => {
            this.logger.info('🛑 Simulation stopped by user');
            this.stopSimulation();
            clearInterval(simulationInterval);
            process.exit(0);
        });
    }
    
    stopSimulation() {
        /**
         * Stop the sensor simulation and cleanup.
         */
        this.running = false;
        if (this.mqttClient) {
            this.mqttClient.end();
        }
        this.logger.info('🔌 Sensor simulation stopped and MQTT connection closed');
    }
}

// Main function to run the sensor simulator
function main() {
    console.log('🌡️ IoT Temperature & Humidity Sensor Simulator');
    console.log('==================================================');
    console.log('University of West Attica - MSC IoT Exercise');
    console.log('Advanced Computer Systems Technologies');
    console.log('==================================================');
    
    try {
        // Change to the script's directory to ensure config.json is found
        process.chdir(path.dirname(require.main.filename));
        
        // Create and start the sensor simulator
        const simulator = new SensorSimulator();
        simulator.startSimulation();
        
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.error('❌ Error: config.json file not found!');
            console.error('Make sure the configuration file exists in the same directory.');
        } else if (error instanceof SyntaxError) {
            console.error('❌ Error: Invalid JSON format in config.json!');
        } else {
            console.error(`❌ Error: ${error.message}`);
        }
    }
}

// Run the main function if this script is executed directly
if (require.main === module) {
    main();
}

// Export the SensorSimulator class for potential reuse
module.exports = SensorSimulator;