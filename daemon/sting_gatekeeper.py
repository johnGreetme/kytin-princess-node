import serial
import time
import os
import secrets
import hashlib
import json
import requests
from dotenv import load_dotenv

# --- Kytin Swarm: Princess Node Gatekeeper ---
# Role: Hardware Root of Trust & State-Lock Enforcement
# Target: NVIDIA Jetson AGX Orin <-> Lilygo T-dongle S3 (The Sting)

# Load environment variables (Never hardcode secrets!)
load_dotenv()
ORIN_ANCHOR_ID = os.getenv("ORIN_ANCHOR_ID")
HIVE_SECRET = os.getenv("HIVE_SECRET")
SERIAL_PORT = os.getenv("STING_SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = 115200

# n8n Routing for State Changes
WEBHOOK_STATE_CHANGE = 'http://localhost:5678/webhook/sting-status-update'

class StingGatekeeper:
    def __init__(self):
        self.is_locked = True
        self.sting_conn = None
        self.current_session_hash = None

    def initialize_hardware(self):
        """Attempt to open the physical serial port to the Sting."""
        try:
            self.sting_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
            print(f"[+] Physical port open on {SERIAL_PORT}. Probing for Sting...")
            return True
        except serial.SerialException:
            print(f"[-] Sting not detected on {SERIAL_PORT}. Hive remains LOCKED.")
            self.lock_hive()
            return False

    def generate_challenge(self):
        """Create a randomized challenge string to prevent replay attacks."""
        return secrets.token_hex(16)

    def verify_sting(self):
        """Execute the Dual-Factor Physicality handshake."""
        if not self.sting_conn:
            return False

        challenge = self.generate_challenge()
        # Payload format expected by the C++ firmware on the ESP32-S3
        payload = f"REQ_AUTH:{challenge}_{ORIN_ANCHOR_ID}\n"
        
        try:
            self.sting_conn.write(payload.encode('utf-8'))
            time.sleep(0.5) # Wait for ESP32 hardware crypto to process
            
            if self.sting_conn.in_waiting > 0:
                response = self.sting_conn.readline().decode('utf-8').strip()
                return self.validate_response(response, challenge)
        except Exception as e:
            print(f"[!] Serial communication error: {e}")
            
        self.lock_hive()
        return False

    def validate_response(self, response, challenge):
        """Mathematically verify the Sting's signature."""
        if response.startswith("AUTH_SUCCESS:MINI_QUEEN:"):
            received_signature = response.split(":")[2]
            
            # Recreate the expected hash locally to verify the Sting's math
            expected_payload = challenge + HIVE_SECRET
            expected_hash = hashlib.sha256(expected_payload.encode()).hexdigest()
            
            if received_signature == expected_hash:
                print("[+] VALID STING DETECTED. State-Lock disengaged.")
                self.unlock_hive(expected_hash)
                return True
            else:
                print("[-] CRITICAL: Signature mismatch. Potential spoofing attempt.")
        else:
            print(f"[-] Handshake failed. Device responded: {response}")
            
        self.lock_hive()
        return False

    def unlock_hive(self, session_hash):
        """Elevate the Orin to Princess status and notify the Swarm."""
        if self.is_locked:
            self.is_locked = False
            self.current_session_hash = session_hash
            self.broadcast_state("UNLOCKED", session_hash)
            print("[*] The Skill is now accessible. Dashboard initialized.")

    def lock_hive(self):
        """Sever access to The Skill and lockdown the dashboard."""
        if not self.is_locked:
            self.is_locked = True
            self.current_session_hash = None
            self.broadcast_state("LOCKED", "NONE")
            print("[*] Protocol State-Locked. Awaiting physical Sting insertion.")

    def broadcast_state(self, state, session_hash):
        """Push the state change to n8n and the kytinOS dashboard."""
        payload = {
            "node_role": "PRINCESS",
            "state_lock": state,
            "session_hash": session_hash,
            "timestamp": int(time.time())
        }
        try:
            requests.post(WEBHOOK_STATE_CHANGE, json=payload, timeout=2)
        except requests.exceptions.RequestException:
            print("[!] Could not reach n8n webhook. Is Docker running?")

if __name__ == "__main__":
    gatekeeper = StingGatekeeper()
    
    print("=== Kytin Swarm: Princess Node Gatekeeper Active ===")
    
    # Infinite Daemon Loop
    while True:
        if gatekeeper.initialize_hardware():
            # If hardware is plugged in, verify its cryptographic identity
            gatekeeper.verify_sting()
            
            # Hold the loop while the Sting is connected
            while gatekeeper.sting_conn and gatekeeper.sting_conn.is_open:
                try:
                    # Simple ping to ensure device hasn't been yanked out
                    gatekeeper.sting_conn.write(b"PING\n")
                    time.sleep(2)
                except serial.SerialException:
                    print("[!] Sting physically removed!")
                    gatekeeper.sting_conn = None
                    gatekeeper.lock_hive()
                    break
        else:
            # Poll every 3 seconds if Sting is missing
            time.sleep(3)
