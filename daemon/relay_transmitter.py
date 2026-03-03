import requests
import json
import time
import os
from dotenv import load_dotenv

# --- Kytin Swarm: Princess Relay Transmitter ---
# Role: Secure Transmission (Princess -> Queen)
# Mechanism: Nectar-Incentivized Sovereign Relay

load_dotenv()
ORIN_ID = os.getenv("ORIN_ANCHOR_ID")

class RelayTransmitter:
    def __init__(self, discovered_queens):
        self.queens = discovered_queens # List of IPs from p2p_discovery.py
        self.last_used_queen = None

    def package_blind_packet(self, signed_tx_hex, sting_signature, challenge):
        """
        Creates the 'Blind Courier' envelope.
        The Queen sees the signature and the bounty, but the Orin's
        internal logic (The Skill) remains isolated.
        """
        return {
            "princess_id": ORIN_ID,
            "challenge": challenge,
            "signature": sting_signature,
            "payload": signed_tx_hex,
            "bounty_nectar": 0.0005, # The micro-toll for the Queen
            "timestamp": int(time.time()),
            "intent": "MAINNET_BROADCAST"
        }

    def transmit_to_swarm(self, packet):
        """
        Iterates through discovered Queens until a relay is accepted.
        """
        if not self.queens:
            print("[!] No Queens found in discovery. Transaction cached locally.")
            return False

        for queen_ip in self.queens:
            print(f"[*] Attempting relay via Queen: {queen_ip}...")
            try:
                # The Queen's endpoint defined in princess_validator.py
                url = f"http://{queen_ip}:8888/authorize_princess"
                response = requests.post(url, json=packet, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    print(f"[+] Relay Accepted! Queen {queen_ip} is broadcasting.")
                    print(f"[*] Gateway Token: {data.get('gateway_token')}")
                    self.last_used_queen = queen_ip
                    return True
                else:
                    print(f"[-] Queen {queen_ip} rejected relay: {response.text}")
            
            except requests.exceptions.RequestException as e:
                print(f"[!] Queen {queen_ip} unreachable: {e}")
                continue

        print("[!!!] CRITICAL: All discovered Queens failed to respond.")
        return False


# --- Integration Example ---
# This is how the main Daemon would trigger a broadcast
def trigger_genesis_broadcast(signed_hex, hardware_proof, challenge):
    # 1. Get the latest Queen list from the Discovery Daemon
    # (In production, this would pull from a shared state or DB)
    available_queens = ["192.168.1.50"] # Placeholder IP

    transmitter = RelayTransmitter(available_queens)
    
    # 2. Wrap the transaction in the State-Locked Envelope
    envelope = transmitter.package_blind_packet(signed_hex, hardware_proof, challenge)
    
    # 3. Send it to the Global Intelligence Network
    success = transmitter.transmit_to_swarm(envelope)
    
    if success:
        print("[*] Genesis Pulse complete. The Swarm is active.")
    else:
        print("[!] Broadcast Failed. Re-verifying Sting connection...")
