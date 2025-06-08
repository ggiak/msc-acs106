#!/usr/bin/env python3
"""
System Test Script for IoT Temperature & Humidity Monitoring System
Tests all components and verifies system functionality
"""

import subprocess
import time
import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

def test_docker_containers():
    """Test if Docker containers are running"""
    print("🔍 Testing Docker containers...")
    try:
        result = subprocess.run(['docker-compose', 'ps'],
                              capture_output=True,
                              text=True,
                              timeout=10)
        if result.returncode == 0:
            print("✅ Docker containers status:")
            print(result.stdout)
            return True
        else:
            print("❌ Docker containers not running properly")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error checking Docker containers: {e}")
        return False

def test_mqtt_broker():
    """Test MQTT broker connectivity"""
    print("\n🔍 Testing MQTT broker...")
    
    connected = False
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            connected = True
            print("✅ MQTT broker connection successful")
        else:
            print(f"❌ MQTT broker connection failed with code {rc}")
    
    def on_message(client, userdata, msg):
        print(f"📨 Test message received: {msg.topic}")
    
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        if connected:
            # Test publish/subscribe
            client.subscribe("test/topic")
            client.publish("test/topic", "Test message")
            time.sleep(1)
            
        client.loop_stop()
        client.disconnect()
        
        return connected
        
    except Exception as e:
        print(f"❌ MQTT broker test failed: {e}")
        return False

def test_nodered_api():
    """Test Node-RED API endpoints"""
    print("\n🔍 Testing Node-RED API...")
    try:
        # Test Node-RED settings endpoint
        response = requests.get("http://localhost:1880/settings", timeout=10)
        if response.status_code == 200:
            print("✅ Node-RED API accessible")
            
            # Test dashboard endpoint
            dashboard_response = requests.get("http://localhost:1880/ui", timeout=10)
            if dashboard_response.status_code == 200:
                print("✅ Node-RED Dashboard accessible")
                return True
            else:
                print("❌ Node-RED Dashboard not accessible")
                return False
        else:
            print(f"❌ Node-RED API not accessible (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Node-RED API test failed: {e}")
        return False

def test_iot_device_config():
    """Test IoT device configuration"""
    print("\n🔍 Testing IoT device configuration...")
    try:
        with open('iot-device/config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['device', 'mqtt', 'sensors', 'simulation']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing configuration key: {key}")
                return False
        
        print("✅ IoT device configuration valid")
        print(f"   Device ID: {config['device']['id']}")
        print(f"   Location: {config['device']['location']}")
        print(f"   Publish interval: {config['simulation']['publish_interval']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ IoT device configuration test failed: {e}")
        return False

def test_python_dependencies():
    """Test Python dependencies"""
    print("\n🔍 Testing Python dependencies...")
    try:
        import paho.mqtt.client
        import numpy
        print("✅ All Python dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("🧪 IoT SYSTEM TEST REPORT")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Docker Containers", test_docker_containers),
        ("MQTT Broker", test_mqtt_broker),
        ("Node-RED API", test_nodered_api),
        ("IoT Device Config", test_iot_device_config),
        ("Python Dependencies", test_python_dependencies)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        results[test_name] = test_func()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for operation.")
        print("\n📋 Next steps:")
        print("1. Start the IoT simulator: cd iot-project/iot-device && python3 sensor_simulator.py")
        print("2. Open dashboard: http://localhost:1880/ui")
        print("3. Monitor data flow and alerts")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        if not results.get("Docker Containers"):
            print("- Run: docker-compose up -d")
        if not results.get("Python Dependencies"):
            print("- Run: pip3 install -r requirements.txt")
        if not results.get("MQTT Broker"):
            print("- Check: docker-compose logs mosquitto")
        if not results.get("Node-RED API"):
            print("- Check: docker-compose logs nodered")
    
    return passed == total

if __name__ == "__main__":
    print("🌡️  IoT System Test Suite")
    print("University of West Attica - MSC IoT Exercise")
    print("=" * 60)
    
    success = generate_test_report()
    exit(0 if success else 1)
