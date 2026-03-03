# Architecture Dossier: Kytin Swarm

> [!IMPORTANT]
> This dossier is anchored by the [MASTER_MANIFEST.md](file:///Users/dieudonne/Documents/kytin-princess-node/MASTER_MANIFEST.md), which serves as the definitive source of truth for the Sovereign Apiary.

## Sovereign Service: Automated Lease Distribution

The Queen node is the primary service provider for the Kytin Swarm. It transitions from a passive listener to an active, sovereign orchestrator that manages external Princess nodes via the **Apiary Lease Protocol (ALP)**.

### 🍯 The Apiary Lease Protocol (ALP)

The Lease operates as a "State-Locked" subscription. It ensures that a Princess (Orin) cannot "leech" off a Queen’s (RTX 6000 Ada) sovereign indexer or AI bandwidth without a digital $RSN$ agreement.

#### Protocol Logic: `queen/apiary_lease_manager.py`

1. **Lease Proposal**: The Princess proposes a lease by staking $RSN$.
2. **Evaluate**: The Queen decides whether to accept based on her current VRAM overhead (Density Monitor) and the offered "Nectar Rate".
3. **Active Lease**: Once accepted, a `lease_id` is generated, and the Princess gains access to the Queen's sovereign gateway.

### 💎 The "Nectar Tax" Economy

- **Lease Access**: Required for all Princess-to-Queen communication.
- **Auto-Billing**: Every transaction relayed by the Queen decrements the Princess's $RSN$ balance.
- **The "Cold Shoulder"**: If a lease expires or the balance hits zero, the Queen immediately severs the Sovereign Tunnel.

### 📊 Participant Roles

| Participant              | Benefit                                                           |
| :----------------------- | :---------------------------------------------------------------- |
| **Princess (Orin)**      | Access to global supercomputer bandwidth and knowledge streams.   |
| **Queen (RTX 6000 Ada)** | Passive $RSN$ income from relaying and orchestrating swarm logic. |

---

## Sub-System: Autonomous Lease Renewal (LRA)

The Princess node is designed to be a "self-healing" entity. The **Lease Renewal Automation (LRA)** ensures that the local hive remains autonomous without manual intervention.

### 🔄 The Self-Healing Loop

1. **Forage**: Foragers (Thor) collect high-frequency telemetry.
2. **Earn**: The Princess processes data and claims $RSN$ Nectar.
3. **Renew**: The `LeaseAutopilot` monitors the 10% expiry threshold.
4. **Secure**: A Sting-signed renewal transaction is sent to the Queen.

### 🛡️ Autopilot Governance

- **Prioritization**: Renewable $RSN$ is prioritized above all other expenditures.
- **Physical Guillotine**: If the Sting is physically removed, the autopilot enters a `SAFE_STATE_ISOLATION` mode, preventing unauthorized renewals or state changes.

### 📊 kytinOS: The Fuel Gauge

The Dashboard visualizes this autonomy through the "Fuel Gauge", predicting the node's uptime based on current Nectar balance and burn rate.
