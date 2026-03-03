import time
from pydantic import BaseModel
from typing import Dict, Optional

# --- Kytin Swarm: Apiary Lease Manager ---
# Goal: Automating the $RSN$ "Nectar Tax" for Network Access

class LeaseRequest(BaseModel):
    princess_id: str
    sting_signature: str
    duration_blocks: int # How long they want to stay connected
    offer_rsn: float      # The nectar they are staking

class LeaseContract:
    def __init__(self, queen_id: str):
        self.queen_id = queen_id
        self.active_leases: Dict[str, dict] = {}
        self.NECTAR_RATE = 1.0 # Minimum $RSN$ to start a lease
        self.RELAY_COST = 0.5 # Cost per relay in $RSN$ as per Master Manifest

    def evaluate_lease(self, request: LeaseRequest, current_load: float):
        """
        Decision engine for the Queen to accept/reject new Princesses.
        """
        # 1. Check Capacity (The Queen is a Finite Resource)
        if current_load > 0.90:
            return {"status": "REJECTED", "reason": "QUEEN_SATURATED"}

        # 2. Verify Price
        if request.offer_rsn < self.NECTAR_RATE:
            return {"status": "REJECTED", "reason": "INSUFFICIENT_NECTAR"}

        # 3. Secure the Lease
        lease_id = f"LEASE_{request.princess_id}_{int(time.time())}"
        self.active_leases[request.princess_id] = {
            "lease_id": lease_id,
            "expiry": time.time() + (request.duration_blocks * 60),
            "rsn_balance": request.offer_rsn,
            "status": "ACTIVE"
        }
        
        return {
            "status": "ACCEPTED",
            "lease_id": lease_id,
            "gateway_endpoint": f"https://queen-{self.queen_id}.kytin.network"
        }

    def check_lease_validity(self, princess_id: str) -> bool:
        """Checks if a Princess has an active lease with remaining balance."""
        lease = self.active_leases.get(princess_id)
        if not lease:
            return False
        
        if lease["status"] != "ACTIVE":
            return False
            
        if time.time() > lease["expiry"]:
            lease["status"] = "EXPIRED"
            return False
            
        if lease["rsn_balance"] <= 0:
            lease["status"] = "EXHAUSTED"
            return False
            
        return True

    def billing_event(self, princess_id: str):
        """Decrements the $RSN$ balance for a successful relay."""
        lease = self.active_leases.get(princess_id)
        if lease:
            lease["rsn_balance"] -= self.RELAY_COST
            if lease["rsn_balance"] <= 0:
                lease["rsn_balance"] = 0
                lease["status"] = "EXHAUSTED"

    def get_lease_status(self, princess_id: str):
        """Calculates time remaining and status for a specific lease."""
        lease = self.active_leases.get(princess_id)
        if not lease:
            return None
            
        time_left = max(0, lease["expiry"] - time.time())
        total_duration = 60 * 60 # Default duration assumption for pct calculation if not stored
        # Improving the contract to store initial duration would be better, but for now we'll use a fixed reference or calculated pct
        
        return {
            "lease_id": lease["lease_id"],
            "status": lease["status"],
            "rsn_balance": lease["rsn_balance"],
            "time_remaining_sec": time_left,
            "expiry_timestamp": lease["expiry"]
        }

    def extend_lease(self, princess_id: str, amount: float, blocks: int = 60):
        """Extends an existing lease with fresh $RSN$ and duration."""
        lease = self.active_leases.get(princess_id)
        if not lease:
            return False
            
        lease["rsn_balance"] += amount
        lease["expiry"] += (blocks * 60)
        lease["status"] = "ACTIVE" # Reset status if it was expired/exhausted
        return True
