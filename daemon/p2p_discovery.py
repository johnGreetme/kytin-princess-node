import asyncio
import os
from kademlia.network import Server
from dotenv import load_dotenv

# --- Kytin Swarm: P2P Discovery Daemon ---
# Role: Sovereign Peer Discovery (Princess -> Queen)
# Technology: Kademlia DHT (Distributed Hash Table)

load_dotenv()
ORIN_ID = os.getenv("ORIN_ANCHOR_ID")
# A bootstrap node is just another Princess or Queen already in the swarm.
# For the very first boot, this will be your primary Queen's IP.
BOOTSTRAP_PEER = os.getenv("BOOTSTRAP_PEER_IP", "QUEEN_STATIC_IP_OR_DNS") 

class SwarmDiscovery:
    def __init__(self):
        self.server = Server()
        self.found_queens = []

    async def start(self):
        """Initialize the DHT server and join the Apiary mesh."""
        print(f"[*] Initializing Kytin P2P Discovery for Princess: {ORIN_ID}")
        await self.server.listen(8468) # Default Kytin P2P Port

        # Bootstrap into the network
        try:
            await self.server.bootstrap([(BOOTSTRAP_PEER, 8468)])
            print(f"[+] Successfully joined the Global Intelligence Network via {BOOTSTRAP_PEER}")
        except Exception as e:
            print(f"[!] Bootstrap failed. Operating as isolated Genesis node. {e}")

    async def announce_self(self):
        """Announce this Orin as an active Princess node seeking a Queen."""
        # Store the Princess ID and its local relay address in the global DHT
        await self.server.set(f"kytin_princess_{ORIN_ID}", "ACTIVE_STATUS")
        print(f"[*] Broadcast: Princess {ORIN_ID} is online and seeking Queen assistance.")

    async def find_queens(self):
        """Search the DHT for nodes registered as Queens (RTX 6000 Ada)."""
        print("[*] Searching DHT for available Queen nodes...")
        # In a mature swarm, we look for the key 'active_queen_nodes'
        queen_list = await self.server.get("active_queen_nodes")
        
        if queen_list:
            self.found_queens = queen_list.split(",")
            print(f"[+] Found {len(self.found_queens)} Queens available for Nectar Relay.")
            return self.found_queens
        else:
            print("[-] No Queens found in the DHT. Scanning for peer-to-peer relay...")
            return []

    async def heartbeat(self):
        """Keep the Princess's presence alive in the global mesh."""
        while True:
            await self.announce_self()
            await asyncio.sleep(300) # Re-announce every 5 minutes

async def main():
    discovery = SwarmDiscovery()
    await discovery.start()
    
    # Run the heartbeat and search concurrently
    await asyncio.gather(
        discovery.heartbeat(),
        discovery.find_queens()
    )

if __name__ == "__main__":
    asyncio.run(main())
