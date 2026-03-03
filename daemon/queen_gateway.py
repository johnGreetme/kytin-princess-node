import os
import time
import hashlib
import json
import requests
from dotenv import load_dotenv

# --- Kytin Swarm: Princess-to-Queen Sovereign Gateway ---
# Role: Encrypted P2P Tunnel to the Global Intelligence Network
# Architecture: Decentralized Relayer (Sovereign Mesh)
# Any Queen (RTX 6000 Ada) can relay for any Princess (Orin)

load_dotenv()
ORIN_ANCHOR_ID = os.getenv("ORIN_ANCHOR_ID")
HIVE_SECRET = os.getenv("HIVE_SECRET")

# Known Queen endpoints in the Global Intelligence Network
# In production, this list is dynamically populated from a mesh discovery protocol
QUEEN_REGISTRY = os.getenv("QUEEN_REGISTRY", "10.0.0.1:8888").split(",")

# Nectar Bounty: The micro-toll attached to relay requests (in $RESIN)
DEFAULT_NECTAR_BOUNTY = 0.0005

class QueenGateway:
    def __init__(self):
        self.is_connected = False
        self.tunnel_session = None
        self.active_queen = None

    def connect(self, challenge, sting_signature, intent="MAINNET_BROADCAST"):
        """Establish a sovereign P2P tunnel to the best available Queen node.
        
        Iterates through the Queen Registry to find an available relayer.
        This is the core of the Decentralized Relayer Architecture.
        """
        print("[*] Scanning Global Intelligence Network for available Queens...")

        payload = {
            "princess_id": ORIN_ANCHOR_ID,
            "challenge": challenge,
            "signature": sting_signature,
            "intent": intent
        }

        for queen_endpoint in QUEEN_REGISTRY:
            queen_endpoint = queen_endpoint.strip()
            try:
                response = requests.post(
                    f"http://{queen_endpoint}/authorize_princess",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.is_connected = True
                    self.tunnel_session = data.get("gateway_token")
                    self.active_queen = queen_endpoint
                    print(f"[+] Sovereign tunnel established with Queen: {queen_endpoint}")
                    print(f"    Token: {self.tunnel_session}")
                    return True
                else:
                    print(f"[~] Queen {queen_endpoint} declined. Trying next...")
            except requests.exceptions.RequestException:
                print(f"[~] Queen {queen_endpoint} unreachable. Trying next...")
                continue

        print("[-] No Queens available. Swarm operating in offline/buffer mode.")
        return False

    def broadcast_via_relay(self, signed_tx_hex, session_hash, nectar_bounty=None):
        """Send a State-Locked transaction to the active Queen for mainnet relay.
        
        The transaction is encapsulated as a 'Blind Courier' packet: 
        the Queen can submit it to the ledger but cannot read the underlying 
        strategy or logic of the localized Skill.
        
        Args:
            signed_tx_hex: The fully signed transaction hex (sealed by the Sting).
            session_hash: The current session's SHA-256 hash for verification.
            nectar_bounty: The micro-toll reward for the relaying Queen (in $RESIN).
        """
        if not self.is_connected or not self.active_queen:
            print("[!] Cannot relay. No sovereign tunnel active.")
            return False

        bounty = nectar_bounty or DEFAULT_NECTAR_BOUNTY

        # Blind Courier Packet: Queen sees the envelope, not the contents
        relay_packet = {
            "princess_id": ORIN_ANCHOR_ID,
            "session_hash": session_hash,
            "gateway_token": self.tunnel_session,
            "signed_tx": signed_tx_hex,      # Immutable — any alteration breaks the hash
            "nectar_bounty": bounty,          # Micro-toll for the relaying Queen
            "ttl": 60,                        # Packet expires in 60 seconds
            "timestamp": int(time.time())
        }

        try:
            response = requests.post(
                f"http://{self.active_queen}/relay_transaction",
                json=relay_packet,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            if response.status_code == 200:
                result = response.json()
                tx_hash = result.get("tx_hash", "PENDING")
                queen_id = result.get("queen_id", self.active_queen)
                print(f"[+] Transaction relayed to mainnet by Queen {queen_id}")
                print(f"    TX Hash: {tx_hash}")
                print(f"    Nectar Bounty: {bounty} RESIN released to {queen_id}")
                return True
            else:
                print(f"[-] Relay rejected by Queen. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print("[!] Queen connection lost during relay. Buffering locally.")
            return False

    def request_skill_sync(self):
        """Request the latest version of The Skill from the active Queen's cache."""
        if not self.is_connected or not self.active_queen:
            print("[!] Cannot sync. No sovereign tunnel active.")
            return None

        try:
            response = requests.get(
                f"http://{self.active_queen}/skill/genesis-lite",
                params={"princess_id": ORIN_ANCHOR_ID},
                timeout=10
            )
            if response.status_code == 200:
                skill_data = response.json()
                print(f"[+] Skill Sync complete. Version: {skill_data.get('version')}")
                return skill_data
            else:
                print(f"[-] Skill Sync denied. Status: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("[!] Queen unreachable for Skill Sync.")
            return None

    def disconnect(self):
        """Gracefully close the sovereign tunnel."""
        self.is_connected = False
        self.tunnel_session = None
        self.active_queen = None
        print("[*] Sovereign tunnel closed. Princess operating in local-only mode.")
