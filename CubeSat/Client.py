import socket
import json
from datetime import datetime

HOST = "127.0.0.1"   # ground station IP (localhost for test)
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("[CubeSat] Connecting to ground station...")
client.connect((HOST, PORT))

# Step 1: Send beacon
beacon = {
    "type": "BEACON",
    "satellite_id": "SALSABIL-01",
    "timestamp": datetime.utcnow().isoformat(),
    "status": "READY"
}
client.send(json.dumps(beacon).encode())
print("[CubeSat] Beacon sent")

# Step 2: Receive handshake
response = client.recv(4096).decode()
response_data = json.loads(response)
print("[CubeSat] Handshake response:", response_data)

# Step 3: Confirm link
confirmation = {
    "type": "LINK_CONFIRM",
    "session_id": response_data["session_id"],
    "status": "CONFIRMED"
}
client.send(json.dumps(confirmation).encode())

print("[CubeSat] Link established successfully.")

client.close()