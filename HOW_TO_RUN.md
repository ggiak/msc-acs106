# How to Run the IoT System - Quick Start Guide

## 🚀 Step-by-Step Instructions

### Prerequisites (One-time setup)
1. **Install Docker Desktop**
   - Download from: https://docs.docker.com/get-docker/
   - Make sure Docker is running (you should see the Docker icon in your system tray)

2. **Install Python 3**
   - Download from: https://www.python.org/downloads/
   - Make sure `python3` and `pip3` are available in your terminal

### Running the System

#### Method 1: Automated Startup (Recommended)
```bash
# Make the startup script executable (first time only)
chmod +x start_system.sh

# Run the automated startup script
./start_system.sh
```

#### Method 2: Manual Step-by-Step

**Step 1: Start the Infrastructure**
```bash
docker-compose up -d
```

**Step 2: Wait for Services (about 30 seconds)**
```bash
# Check if containers are running
docker-compose ps
```

**Step 3: Install Python Dependencies**
```bash
# Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r iot-device/requirements.txt
pip install requests paho-mqtt numpy
```

**Step 4: Access Node-RED Editor**
- Open your web browser
- Go to: http://localhost:1880
- You should see the Node-RED interface with pre-configured flows
- Click the **"Deploy"** button (red button in the top-right corner)

**Step 5: Start the IoT Device Simulator**
```bash
# Open a new terminal window, activate the virtual environment, and start the simulator
source venv/bin/activate
python3 iot-device/sensor_simulator.py
```

**Step 6: View the Dashboard**
- Open your web browser
- Go to: http://localhost:1880/ui
- You should see the IoT dashboard with gauges and charts updating in real-time

## 🎯 What You Should See

### 1. Terminal Output (IoT Simulator)
```
🌡️  IoT Temperature & Humidity Sensor Simulator
==================================================
University of West Attica - MSC IoT Exercise
Advanced Computer Systems Technologies
==================================================
2024-01-01 12:00:00,123 - INFO - 🚀 Starting IoT Sensor Simulation
2024-01-01 12:00:01,200 - INFO - Connected to MQTT Broker successfully
2024-01-01 12:00:01,250 - INFO - 📊 Published: Temp=23.2°C, Humidity=65.4% [Fire Risk: False]
```

### 2. Node-RED Editor (http://localhost:1880)
- Flow diagram with connected nodes
- Green "connected" status under MQTT nodes
- No error messages in the debug panel

### 3. Dashboard (http://localhost:1880/ui)
- Temperature gauge showing current temperature
- Humidity gauge showing current humidity
- Line charts showing historical data trends
- Alert notifications when temperature > 40°C

## ⚠️ Troubleshooting

### Problem: Docker containers won't start
**Solution:**
```bash
# Make sure Docker Desktop is running
docker info

# If Docker isn't running, start Docker Desktop application
```

### Problem: "Cannot connect to MQTT broker"
**Solution:**
```bash
# Check container status
docker-compose ps

# Restart containers if needed
docker-compose restart

# View logs for issues
docker-compose logs
```

### Problem: Dashboard shows "Cannot GET /ui"
**Solution:**
1. Go to Node-RED editor: http://localhost:1880
2. Click the hamburger menu (three lines) → Manage palette
3. Go to "Install" tab
4. Search for "node-red-dashboard"
5. Click "Install" next to "node-red-dashboard"
6. Wait for installation to complete
7. Click "Deploy" button
8. Try dashboard again: http://localhost:1880/ui

### Problem: No data in dashboard
**Solution:**
1. Make sure IoT simulator is running: `python3 sensor_simulator.py`
2. Check Node-RED flows are deployed (click Deploy button)
3. Verify MQTT connection (green status in Node-RED)

### Problem: Python import errors
**Solution:**
```bash
# Make sure you have activated the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r iot-device/requirements.txt
pip install requests paho-mqtt numpy
```

## 🛑 How to Stop the System

### Stop IoT Simulator
- Press `Ctrl+C` in the terminal running the simulator

### Stop Docker Containers
```bash
docker-compose down
```

## 🔄 How to Restart the System

```bash
docker-compose restart
```

## 📊 Testing Fire Detection

To test the fire detection system:

1. Edit `iot-device/config.json`
2. Change `"fire_threshold": 40.0` to `"fire_threshold": 20.0`
3. Or change `"anomaly_probability": 0.05` to `"anomaly_probability": 0.3`
4. Restart the IoT simulator
5. Watch for fire alerts in the dashboard

## 🎓 For Academic Submission

Your system demonstrates:
- ✅ IoT device with sensors (simulated Raspberry Pi)
- ✅ MQTT message broker (Mosquitto)
- ✅ Node-RED server with dashboard
- ✅ Fire detection service
- ✅ Real-time data visualization
- ✅ Docker containerization

All requirements from the course assignment are fulfilled!
