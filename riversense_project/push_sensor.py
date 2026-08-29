"""
RiverSense — Hardware Sensor Push Script
=========================================
Run this on your Raspberry Pi / Arduino / test machine to push
sensor readings directly to the Django dashboard in real time.

Usage:
    python push_sensor.py

The data will instantly appear on the live dashboard UI.
"""

import requests
import time
import random  # Replace with actual sensor readings

# ── CONFIG ────────────────────────────────────────────────
SERVER_URL = 'http://127.0.0.1:8000'   # Change to your server IP if remote
STATION    = 'ellis_bridge'             # Change to your station
INTERVAL   = 5                          # Push every 5 seconds

# ── FUNCTION TO READ SENSORS ──────────────────────────────
def read_sensors():
    return {
        'station':          STATION,
        'ph':               round(random.uniform(6.8, 8.4), 2),   # Replace with ph_sensor.read()
        'dissolved_oxygen': round(random.uniform(4.5, 9.0), 1),   # Replace with do_sensor.read()
        'turbidity':        round(random.uniform(5.0, 80.0), 1),  # Replace with turb_sensor.read()
        'temperature':      round(random.uniform(24.0, 34.0), 1), # Replace with temp_sensor.read()
        'water_level':      round(random.uniform(1.5, 4.5), 2),   # Replace with level_sensor.read()
        'bod':              round(random.uniform(2.0, 12.0), 1),  # Replace with bod_sensor.read()
        'conductivity':     round(random.uniform(200, 800), 1),   # Replace with cond_sensor.read()
        'tds':              round(random.uniform(150, 600), 0),   # Replace with tds_sensor.read()
    }


# ── PUSH TO DASHBOARD ─────────────────────────────────────
def push_to_dashboard(data):
    try:
        response = requests.post(
            f'{SERVER_URL}/api/push/sensor/',
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Saved → ID:{result['id']} | {result['station']} | {result['timestamp']}")
        else:
            print(f"[ERROR] Status {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to {SERVER_URL}. Is the Django server running?")
    except Exception as e:
        print(f"[ERROR] {e}")


# ── MAIN LOOP ─────────────────────────────────────────────
if __name__ == '__main__':
    print(f"RiverSense Sensor Push — Station: {STATION}")
    print(f"Pushing to: {SERVER_URL}/api/push/sensor/")
    print(f"Interval: every {INTERVAL} seconds")
    print("-" * 50)

    while True:
        data = read_sensors()
        print(f"Reading → pH:{data['ph']} DO:{data['dissolved_oxygen']} Turb:{data['turbidity']} Temp:{data['temperature']}°C Level:{data['water_level']}m")
        push_to_dashboard(data)
        time.sleep(INTERVAL)
