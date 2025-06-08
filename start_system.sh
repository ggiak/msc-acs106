#!/bin/bash

echo "🌡️  IoT Temperature & Humidity Monitoring System"
echo "=================================================="
echo "University of West Attica - MSC IoT Exercise"
echo "Advanced Computer Systems Technologies"
echo "=================================================="
echo

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "🚀 Starting IoT system infrastructure..."

# Start Docker containers
docker-compose up -d

echo "⏳ Waiting for services to initialize..."
sleep 10

# Check container status
echo "📊 Container Status:"
docker-compose ps

echo
echo "🔗 Service URLs:"
echo "   Node-RED Editor:  http://localhost:1880"
echo "   IoT Dashboard:    http://localhost:1880/ui"
echo

echo "🐍 Installing Python dependencies..."
cd iot-device
pip3 install -r requirements.txt
cd ..

echo
echo "✅ System startup complete!"
echo
echo "📋 Next Steps:"
echo "1. Open Node-RED editor: http://localhost:1880"
echo "2. Install dashboard nodes if needed (see installation guide)"
echo "3. Deploy flows in Node-RED"
echo "4. Start IoT simulator:"
echo "   cd iot-device"
echo "   python3 sensor_simulator.py"
echo "5. View dashboard: http://localhost:1880/ui"
echo
echo "🛠️  Troubleshooting:"
echo "   View logs: docker-compose logs"
echo "   Stop system: docker-compose down"
echo "   Restart: docker-compose restart"
