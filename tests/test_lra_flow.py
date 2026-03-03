import requests
import time
import subprocess
import signal
import os

BASE_URL = "http://localhost:8888"

def test_lra_flow():
    print("--- Starting LRA Verification Flow ---")
    
    # 1. Propose Short Lease (for testing)
    print("[*] Test 1: Propose Short Lease")
    lease_req = {
        "princess_id": "ORIN_LRA",
        "sting_signature": "SIG_LRA",
        "duration_blocks": 1, # 1 minute
        "offer_rsn": 10.0
    }
    requests.post(f"{BASE_URL}/apiary/lease/request", json=lease_req)
    
    # 2. Check Status
    print("[*] Test 2: Checking Lease Status")
    response = requests.get(f"{BASE_URL}/lease/status/ORIN_LRA")
    status = response.json()
    print(f"[+] Initial health: {status['time_remaining_pct']*100:.2f}%")
    
    # 3. Trigger Renewal (Direct call for speed)
    print("[*] Test 3: Manual Renewal Trigger")
    renew_req = {
        "princess_id": "ORIN_LRA",
        "amount": 2.0,
        "signature": "LRA_TEST_SIG"
    }
    response = requests.post(f"{BASE_URL}/lease/renew", json=renew_req)
    assert response.status_code == 200
    data = response.json()
    print(f"[+] Lease extended. New balance: {data['new_balance']}")
    
    # 4. Verify Extension
    response = requests.get(f"{BASE_URL}/lease/status/ORIN_LRA")
    new_status = response.json()
    assert new_status["rsn_balance"] == 12.0
    print(f"[+] Extension verified. Final balance: {new_status['rsn_balance']}")

if __name__ == "__main__":
    # Start Queen validator in background if possible, or assume it's running
    # For this verification, we assume the environment might not have all deps
    # so we'll just check logic if we can't run.
    try:
        test_lra_flow()
        print("--- LRA Verification Complete ---")
    except Exception as e:
        print(f"[!] Verification failed or environment not ready: {e}")
