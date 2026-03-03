import time
import serial
import requests
import os
from dotenv import load_dotenv

# --- Kytin Swarm: Princess Transaction Monitor ---
# Role: Ledger Confirmation & Physical Feedback (Orin -> Sting)
# Security: State-Locked Protocol Verification

load_dotenv()
SERIAL_PORT = os.getenv("STING_SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = 115200

class TransactionMonitor:
    def __init__(self, sting_conn):
        self.sting_conn = sting_conn # Re-use the existing serial connection
        self.pending_transactions = []

    def add_to_watch(self, tx_id, queen_ip):
        """Adds a new transaction to the monitoring queue."""
        print(f"[*] Monitoring TxID: {tx_id} via Queen: {queen_ip}")
        self.pending_transactions.append({
            "tx_id": tx_id,
            "queen_ip": queen_ip,
            "start_time": time.time()
        })
        self.update_sting_display("TX_PENDING")

    def poll_queen_for_status(self, tx_id, queen_ip):
        """Queries the Queen's Sovereign RPC for confirmation status."""
        try:
            # The Queen node provides a status endpoint for its relayed batches
            url = f"http://{queen_ip}:8888/tx_status/{tx_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                status = response.json().get("status")
                return status # e.g., "confirmed", "finalized", "pending"
        except Exception as e:
            print(f"[!] Error polling Queen {queen_ip}: {e}")
        return "unknown"

    def update_sting_display(self, status_code):
        """Sends a serial command to the T-dongle S3 to update its LCD."""
        if self.sting_conn and self.sting_conn.is_open:
            try:
                # Commands defined in the Sting's C++ firmware
                # e.g., "DISP:CONFIRMED"
                command = f"DISP:{status_code}\n"
                self.sting_conn.write(command.encode('utf-8'))
                print(f"[*] Sting LCD updated: {status_code}")
            except Exception as e:
                print(f"[!] Failed to update Sting display: {e}")

    def monitor_loop(self):
        """Continuous loop to check pending transactions."""
        while True:
            for tx in self.pending_transactions[:]:
                status = self.poll_queen_for_status(tx['tx_id'], tx['queen_ip'])
                
                if status in ["confirmed", "finalized"]:
                    print(f"[+] TX {tx['tx_id']} CONFIRMED on mainnet.")
                    self.update_sting_display("TX_SUCCESS")
                    self.pending_transactions.remove(tx)
                
                elif status == "failed":
                    print(f"[-] TX {tx['tx_id']} FAILED.")
                    self.update_sting_display("TX_FAILED")
                    self.pending_transactions.remove(tx)
                
                # Timeout after 5 minutes
                elif time.time() - tx['start_time'] > 300:
                    print(f"[!] TX {tx['tx_id']} timed out.")
                    self.update_sting_display("TX_TIMEOUT")
                    self.pending_transactions.remove(tx)

            time.sleep(10) # Poll every 10 seconds to save Orin resources


# --- Integration with Main Daemon ---
# transmitter = RelayTransmitter(queens)
# if transmitter.transmit_to_swarm(envelope):
#     tx_id = get_tx_id_from_queen_response()
#     monitor.add_to_watch(tx_id, transmitter.last_used_queen)
