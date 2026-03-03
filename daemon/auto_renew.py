import time
import requests
import os
from dotenv import load_dotenv

# --- Kytin Swarm: Princess Auto-Renewal Daemon ---
# Role: Ensuring 100% Uptime for the Local Hive
# Logic: Forage -> Earn -> Renew -> Secure

load_dotenv()
ORIN_ID = os.getenv("ORIN_ANCHOR_ID")
QUEEN_IP = os.getenv("QUEEN_IP", "localhost") # Primary Queen for management

class LeaseAutopilot:
    def __init__(self, threshold=0.10):
        self.threshold = threshold # Renew when 10% of lease time remains
        self.queen_url = f"http://{QUEEN_IP}:8888"

    def get_lease_status(self):
        """Queries the Queen for current lease health."""
        try:
            response = requests.get(f"{self.queen_url}/lease/status/{ORIN_ID}", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[!] Error reaching Queen at {QUEEN_IP}: {e}")
        return None

    def renew_lease(self):
        """
        Triggers the renewal process. 
        In production, this would involve the RSN_Wallet and Sting signing.
        """
        print("[!] Lease nearing expiry. Initializing Nectar Transfer...")
        
        # 1. Check local Nectar ($RSN) reserves (Simulated)
        # In a real system, we'd call the RSN_Wallet API
        print("[*] Checking RSN Wallet balance...")
        balance = 12.4 # Simulated balance
        
        if balance >= 1.0:
            # 2. Sign a 'Renewal Intent' using the Sting (Simulated)
            # This requires the StingGatekeeper to be active and authenticated
            print("[*] Requesting Sting Signature for Renewal...")
            signature = "RENEWAL_SIG_" + ORIN_ID + "_" + str(int(time.time()))
            
            # 3. Send to Queen
            payload = {
                "princess_id": ORIN_ID,
                "amount": 1.0,
                "signature": signature
            }
            try:
                response = requests.post(f"{self.queen_url}/lease/renew", json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"[✓] Lease successfully extended. New Expiry: {data['new_expiry']}")
                    return True
            except Exception as e:
                print(f"[!] Renewal request failed: {e}")
        else:
            print("[⚠️] Insufficient $RSN$ for Auto-Renew. Please deploy Foragers to earn Nectar.")
        
        return False

    def monitor_loop(self):
        """Continuous monitoring loop for the autopilot."""
        print(f"[*] Lease Autopilot active for {ORIN_ID}. Threshold: {self.threshold * 100}%")
        while True:
            status = self.get_lease_status()
            if status:
                print(f"[*] Lease Health: {status['time_remaining_pct']*100:.1f}% remaining | Balance: {status['rsn_balance']} RSN")
                
                if status['time_remaining_pct'] <= self.threshold:
                    self.renew_lease()
            
            # Poll every hour to save resources
            time.sleep(3600)

if __name__ == "__main__":
    autopilot = LeaseAutopilot()
    autopilot.monitor_loop()
