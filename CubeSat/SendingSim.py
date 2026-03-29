import time
import random
import json
import base64
from datetime import datetime

# -----------------------------
# Simulated CubeSat Camera
# -----------------------------
def take_snapshot():
    """
    Simulates taking a satellite image.
    In real CubeSat: this would trigger a camera module.
    """
    print("[CubeSat] Capturing image...")

    # Fake image payload (instead of real bytes)
    fake_image_data = f"IMAGE_DATA_{random.randint(1000,9999)}"

    encoded = base64.b64encode(fake_image_data.encode()).decode()

    return encoded


# -----------------------------
# Simulated Sensors
# -----------------------------
def read_sensors():
    """
    Simulated onboard telemetry sensors
    """
    return {
        "temperature_c": round(random.uniform(-10, 45), 2),
        "battery_v": round(random.uniform(3.6, 4.2), 2),
        "radiation_index": round(random.uniform(0.1, 5.0), 3),
        "orientation_deg": {
            "roll": random.randint(0, 360),
            "pitch": random.randint(0, 360),
            "yaw": random.randint(0, 360)
        }
    }


# -----------------------------
# Build Telemetry Packet
# -----------------------------
def build_packet(image_data, sensors):
    packet = {
        "satellite_id": "SALSABIL-CUBESAT-01",
        "timestamp": datetime.utcnow().isoformat(),
        "image_snapshot": image_data,
        "telemetry": sensors
    }
    return packet


# -----------------------------
# Simulated Transmission (LoRaWAN / Ground Station)
# -----------------------------
def transmit(packet):
    """
    In real system:
    - LoRaWAN uplink OR ground station relay
    - Here we just print or simulate send
    """
    print("\n[CubeSat] Transmitting packet...")
    time.sleep(1)

    # Simulate compression for low bandwidth
    compressed = json.dumps(packet)

    print("[GROUND STATION RECEIVED]")
    print(compressed[:300] + "...\n")  # truncate for readability


# -----------------------------
# Main CubeSat Loop
# -----------------------------
def cubesat_cycle():
    print("\n=== SALSABIL CUBESAT SIMULATION START ===\n")

    while True:
        # Step 1: Capture image
        image = take_snapshot()

        # Step 2: Read sensors
        sensors = read_sensors()

        # Step 3: Build packet
        packet = build_packet(image, sensors)

        # Step 4: Transmit
        transmit(packet)

        # Orbital delay simulation (e.g., passes every 10 seconds)
        time.sleep(10)


if __name__ == "__main__":
    cubesat_cycle()