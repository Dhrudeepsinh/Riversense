"""
RiverSense — YOLOv8 Detection Push Script
==========================================
Run this alongside your YOLOv8 inference pipeline.
Each detection is instantly pushed to the Django dashboard.

Usage:
    python push_detection.py
"""

import requests
import time
import random  # Replace with actual YOLOv8 results

SERVER_URL = 'http://127.0.0.1:8000'
STATION    = 'gandhi_bridge'


def push_detection(station, trash_class, confidence, lat=23.0225, lng=72.5714):
    """
    Call this function from your YOLOv8 inference loop.

    Example integration:
        results = model(frame)
        for box in results[0].boxes:
            cls   = 'cluster' if int(box.cls) == 1 else 'solo'
            conf  = float(box.conf)
            push_detection(STATION, cls, conf)
    """
    try:
        response = requests.post(
            f'{SERVER_URL}/api/push/detection/',
            json={
                'station':    station,
                'trash_class': trash_class,
                'confidence': confidence,
                'latitude':   lat,
                'longitude':  lng,
            },
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[DETECTION] {result['trash_class'].upper()} at {result['station']} | conf:{confidence:.2f} | alert:{result['alert_level']} | {result['timestamp']}")
        else:
            print(f"[ERROR] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")


# ── TEST MODE (simulates detections) ─────────────────────
if __name__ == '__main__':
    print(f"RiverSense Detection Push — Station: {STATION}")
    print(f"Pushing to: {SERVER_URL}/api/push/detection/")
    print("-" * 50)

    while True:
        trash_class = random.choice(['solo', 'solo', 'cluster'])
        confidence  = round(random.uniform(0.55, 0.99), 3)
        push_detection(STATION, trash_class, confidence)
        time.sleep(8)
