import time
import json
import random
import hashlib
from datetime import datetime

# -----------------------------
# Ground Station (Simulated)
# -----------------------------
class GroundStation:
    def __init__(self, station_id):
        self.station_id = station_id
        self.active_sessions = {}

    def receive_beacon(self, beacon):
        print(f"\n[GROUND] Beacon received from {beacon['satellite_id']}")

        # Decide if satellite is in range (simulated)
        in_range = random.choice([True, True, True, False])

        if in_range:
            print("[GROUND] Satellite in range. Initiating handshake...")
            return self.initiate_handshake(beacon)
        else:
            print("[GROUND] Satellite out of range.")
            return None

    def initiate_handshake(self, beacon):
        session_id = f"SESSION-{random.randint(1000,9999)}"

        # Generate session key (mock crypto)
        raw_key = f"{beacon['satellite_id']}{self.station_id}{time.time()}"
        session_key = hashlib.sha256(raw_key.encode()).hexdigest()[:16]

        session = {
            "session_id": session_id,
            "session_key": session_key,
            "satellite_id": beacon["satellite_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "ACTIVE"
        }

        self.active_sessions[session_id] = session

        print(f"[GROUND] Session established: {session_id}")
        return session


# -----------------------------
# CubeSat (Simulated)
# -----------------------------
class CubeSat:
    def __init__(self, satellite_id):
        self.satellite_id = satellite_id
        self.session = None

    # 1. Broadcast beacon
    def broadcast_beacon(self):
        beacon = {
            "satellite_id": self.satellite_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "BEACON",
            "battery": round(random.uniform(60, 100), 2),
            "status": "SEARCHING_GROUND_STATION"
        }

        print(f"\n[CubeSat] Broadcasting beacon: {self.satellite_id}")
        return beacon

    # 2. Receive handshake response
    def receive_handshake(self, session):
        if session:
            print("[CubeSat] Handshake accepted.")
            self.session = session
            return True
        else:
            print("[CubeSat] No ground station response.")
            return False

    # 3. Confirm session
    def confirm_connection(self):
        if not self.session:
            return False

        confirmation = {
            "satellite_id": self.satellite_id,
            "session_id": self.session["session_id"],
            "status": "LINK_CONFIRMED",
            "timestamp": datetime.utcnow().isoformat()
        }

        print("[CubeSat] Link confirmed with ground station.")
        return confirmation


# -----------------------------
# Full Connection Cycle
# -----------------------------
def connection_cycle():
    cube = CubeSat("SALSABIL-CUBESAT-01")
    ground = GroundStation("TUN-GS-01")

    print("\n=== SALSABIL SPACE LINK ESTABLISHMENT ===")

    # Step 1: CubeSat beacon
    beacon = cube.broadcast_beacon()

    time.sleep(1)

    # Step 2: Ground station receives beacon
    session = ground.receive_beacon(beacon)

    time.sleep(1)

    # Step 3: CubeSat receives handshake
    cube.receive_handshake(session)

    time.sleep(1)

    # Step 4: Final confirmation
    confirmation = cube.confirm_connection()

    if confirmation:
        print("\n=== LINK ESTABLISHED SUCCESSFULLY ===")
        print(json.dumps(confirmation, indent=2))
    else:
        print("\n=== LINK FAILED ===")


if __name__ == "__main__":
    connection_cycle()