# Kytin Swarm: Princess Workspace (Localized Orchestrator)

This repository contains the software stack for the Princess node (NVIDIA Jetson AGX Orin). The Princess acts as the localized orchestrator within the Apiary, bridging the gap between high-tier Queen nodes (RTX 6000 Ada) and edge Foragers (Jetson Thor).

## 🐝 The Bee Economy Hierarchy

| Role             | Hardware               | Primary Function                                                               |
| :--------------- | :--------------------- | :----------------------------------------------------------------------------- |
| **The Queen**    | NVIDIA RTX 6000 Ada    | Global orchestration, complex model training, and heavy-lift compute.          |
| **The Princess** | NVIDIA Jetson AGX Orin | Localized swarm intelligence, State-Locked authorization, and Clawhub hosting. |
| **The Forager**  | NVIDIA Jetson AGX Thor | High-throughput telemetry gathering and environmental data ingestion.          |
| **The Sting**    | Lilygo T-dongle S3     | The physical hardware root of trust and State-Locked Protocol anchor.          |

## 🏗️ Repository Structure

```plaintext
├── daemon/                 # Python Hardware Daemon (Sting Handshake & Queen Gateway)
├── firmware/               # T-Dongle S3 Authentication Firmware
├── n8n/                    # Workflow JSON exports for data routing
├── queen/                  # Queen-side FastAPI validator (RTX 6000 Ada)
├── resin/                  # Resin DSL modules for localized logic
├── ollama/                 # Model-specific Modelfiles and fencing configs
├── kytinOS/                # Dashboard (Clawhub) configuration files
└── README.md               # Architecture and Setup Guide
```

## 🔒 State-Locked Protocol: Dual-Factor Physicality (DFP)

The Princess node introduces a paradigm shift in decentralized security by enforcing **Dual-Factor Physicality (DFP)**. No P1 high-value transaction or "Skill" update can be executed without a physical handshake. While industry standards typically rely on digital-only MFA (susceptible to SIM swapping, phishing, and remote device takeover), the Kytin architecture mandates a physical root of trust.

### The Vulnerability of Remote Signing

Remote signing is a "software-only" permission. Even when secured by biometric mobile apps, if the software interface is compromised, an attacker can theoretically drain assets or alter swarm logic. The Apiary mathematically eliminates this risk by removing the software's ability to sign autonomously.

### The DFP Mechanism (The Orin and the Sting)

- **Digital Intelligence (Layer 1):** The Orin node utilizes Ollama and _The Skill_ to identify a high-value opportunity, constructs the transaction batch, and generates a cryptographic challenge.
- **Physical Permission (Layer 2):** The signature required to finalize the transaction does not reside on the Orin’s SSD or VRAM. It is locked within the secure enclave of the Lilygo T-dongle S3 (The Sting).
- **The Handshake:** Execution is "State-Locked" until the Sting is physically inserted into the Orin’s USB port.

### Why Remote Signing is Permanently Disabled

- **Immunity to Remote Exploits:** An attacker on the other side of the globe may compromise the Apiary dashboard or mobile notification app, but they cannot physically reach into the room and insert the Sting.
- **Forced Human-in-the-Loop (HITL):** High-priority (P1) transactions represent significant value movement. DFP ensures a human administrator has reviewed the reasoning on the kytinOS mobile app and made a conscious, physical decision to authorize the state change.
- **Hardware Isolation:** By keeping private keys inside a disconnected USB dongle until execution occurs, the "Attack Surface" is reduced from the entire internet to a single physical port on the Orin.

### Cryptographic Proof of Presence

Every transaction broadcasted to the Queen nodes (RTX 6000 Ada) carries a metadata tag confirming it was signed via DFP.

$$Sign_{final} = \text{ECDSA}(\text{Batch Data}, \text{Private Key}_{Sting}) \oplus \text{Proof}_{Physical}$$

The Queen nodes are programmed to reject any P1 batch that does not include the physical presence proof, ensuring the entire Apiary adheres to the same uncompromising security standard. This architecture ensures the localized swarm remains an unbreachable fortress.

### ⚓ Procurement & Flashing Guide: The Immutable Anchor

By hardcoding the cryptographic relationship between the Orin and the Sting, you mathematically eliminate hardware swapping.

**Bill of Materials:**

1. **Mini-Queen:** NVIDIA Jetson AGX Orin Developer Kit.
2. **The Sting:** Lilygo T-dongle S3 (ESP32-S3) with built-in ST7735 LCD.
3. **Admin Workstation:** Isolated PC (Linux/Windows) running Arduino IDE/PlatformIO.

**Step 1: Extract the Orin's Hardware Anchor**
Retrieve the unique serial number from the Orin terminal:
`cat /proc/device-tree/serial-number` (e.g., `1422420001844`).

**Step 2: Prepare the "Sting" Firmware**
On the isolated Admin Workstation, explicitly hardcode the Orin's extracted serial into the C++ firmware (`firmware/sting.ino`). This cryptographically binds the execution logic solely to your Orin.

**Step 3: Flash the Lilygo T-dongle S3**
In the Arduino IDE:

- Board: `ESP32S3 Dev Module`
- USB CDC On Boot: `Enabled`
- Flash Size: `16MB (128Mb)`
- PSRAM: `OPI PSRAM`
  Upload the firmware to permanently burn the logic into the ESP32-S3.

**Step 4: The kytinOS Initialization Handshake**
Plug the flashed T-dongle into the Orin. The OpenClaw Python daemon sends the initial challenge using its hardware serial. The `StingVerification` Resin DSL triggers, validating the `AUTH_SUCCESS` response from the Sting's eFuse MAC binding. Upon verification, the kytinOS Dashboard unlocks, elevating the localized node to a Mini-Queen.

### 🧱 Hard-Locking the Sting: The esptool.py Protocol

Once you have flashed the final firmware onto the Lilygo T-dongle S3, you must permanently lock the flash memory by blowing eFuses. This ensures that even if stolen, the firmware cannot be overwritten to extract the `HIVE_SECRET` or alter the `ORIN_ANCHOR_ID`.

> [!CAUTION]
> **Permanent Hardware Change**
> Once these commands are executed, the firmware on that specific T-dongle S3 can never be changed again.

**1. Disabling the Download Mode**
`esptool.py --port /dev/ttyACM0 burn_efuse DIS_DOWNLOAD_MODE 1`

**2. Disabling JTAG (Hardware Debugging)**
`esptool.py --port /dev/ttyACM0 burn_efuse JTAG_SEL_ENABLE 0`
`esptool.py --port /dev/ttyACM0 burn_efuse DIS_PAD_JTAG 1`

## 🧠 Local Intelligence: The Skill

The Princess executes The Skill (Book: Genesis Lite) using a quantized Ollama backend. On the Jetson AGX Orin, the most critical factor is the **Unified Memory Architecture**. To ensure inference doesn't starve the kytinOS dashboard (Clawhub) or the Python hardware daemon of resources, strict memory fencing is implemented.

### Ollama Memory Allocation Strategy

The configuration targets leaving at least 4GB to 8GB of RAM free for the system, Docker containers (n8n, Dashboard), and the hardware daemon.

- **Model Quantization:** 4-bit (`q4_K_M`) or 5-bit (`q5_K_M`) Llama 3 / Mistral (consuming ~4.5GB VRAM).
- **Environment Fencing (`ollama/fencing.sh`):**
  - `OLLAMA_MAX_LOADED_MODELS=1` (Prevents multiple models)
  - `OLLAMA_NUM_PARALLEL=1` (Limits concurrent requests)
  - `OLLAMA_MAX_QUEUE=5` (Prevents memory spikes from telemetry)
  - `CUDA_VISIBLE_DEVICES=0` (Explicitly maps the Orin iGPU)
- **API Call Limits (`sting_gatekeeper.py`):** The daemon restricts the context window (`num_ctx: 2048`) and threads (`num_thread: 4`) upon execution.

### Resin DSL: Resource Guardrails

Monitoring is embedded directly into the Resin DSL (`resource_guardrail.rdsl`). If VRAM exceeds `VRAM_CRITICAL = 85%`, the protocol triggers a scaling back to `LITE` inference or pauses the reasoning feed to prevent a system-wide hang, ensuring the kytinOS dashboard remains fluid.

## � The Mini-Queen Architecture

The Princess node (Jetson AGX Orin) operates as a "Mini-Queen" orchestrator for localized hives (e.g., homes, schools, offices). This creates a Tiered Ecosystem:

1. **The Enterprise Apiary (Mainnet Genesis):** RTX 6000 Ada + Jetson Thor for heavy-duty, high-frequency execution.
2. **The Local Colony (Subnet/Consumer):** Jetson AGX Orin cluster + T-Dongle S3 for localized RAG and efficient execution.

The Resin DSL dynamically transitions the Orin between a `Forager` worker and the `Mini_Queen` local orchestrator based on hardware metrics and the presence of the authenticated Sting.

## 🌅 Genesis Initialization: The Sovereign NVIDIA Gateway

The initialization of a Kytin Swarm is a choreographed sequence that transitions hardware from inert silicon to an active, sovereign intelligence node. The Queen Node (RTX 6000 Ada) serves a dual role: **The Global Brain** and **The Sovereign RPC**. The Princess doesn't talk to the blockchain directly — it talks only to your Queen via an encrypted P2P tunnel.

| Feature          | Helius (Third Party)                      | The Queen (Your NVIDIA Stack)                   |
| :--------------- | :---------------------------------------- | :---------------------------------------------- |
| **Data Privacy** | They can see your transaction patterns.   | Total privacy. Data never leaves your hardware. |
| **Costs**        | Monthly fees that scale with your growth. | One-time hardware investment (RTX 6000 Ada).    |
| **Control**      | They can throttle or de-platform you.     | You are the sovereign authority.                |
| **Latency**      | Dependent on their server load.           | Direct CUDA-to-CUDA communication.              |

### Phase 1: Queen Sovereignty (The Gateway)

Before any localized node can wake up, the Queen must establish the sovereign perimeter.

- **Ledger Indexing:** The Queen initializes its local blockchain node, loading the current state into its 48GB of VRAM.
- **Kytin-Link Activation:** The Queen opens a secure, encrypted P2P listener — a "private door" that only authenticated Kytin hardware can see.
- **The Skill Repository:** The Queen loads "The Skill" (Genesis Book) into its local cache, ready to feed Princess nodes as they come online.

### Phase 2: The Princess Diagnostic (Local Boot)

The Princess Node (Jetson AGX Orin) is powered on in its local environment (home, office, or school).

- **Self-Check:** The Orin performs a hardware diagnostic, verifying that its NVDLA and CUDA cores are responsive.
- **Isolation Mode:** By default, the Princess starts in a "Locked" state. It will not attempt to talk to the public internet or any local foragers until the State-Locked Protocol is satisfied.
- **Daemon Launch:** The `sting_gatekeeper.py` daemon begins polling the USB ports, awaiting the physical root of trust.

### Phase 3: The Sting Handshake (Physical State-Lock)

The administrator physically inserts the Sting (Lilygo T-dongle S3) into the Orin.

- **Serial Detection:** The `sting_gatekeeper.py` detects the Sting and issues a randomized cryptographic challenge.
- **Hardware Signature:** The Sting — internally bonded to this specific Orin serial number — calculates the response using its private `HIVE_SECRET`.
- **Status Change:** The T-dongle LCD turns green and displays: `PRINCESS SECURED`.
- **Protocol Unlock:** The Orin's internal firewall drops, allowing it to communicate only with the Queen's sovereign RPC gateway.

### Phase 4: Acquiring "The Skill" (Knowledge Ingestion)

The Princess is now secure but "empty." It must acquire the intelligence required to operate the localized swarm.

- **Queen Handshake:** The Princess sends its authenticated signature to the RTX 6000 Ada via the encrypted Kytin-Link (`queen_gateway.py`).
- **Knowledge Stream:** The Queen validates the signature and streams "The Skill" (Genesis Lite) directly to the Orin.
- **Ollama Warm-up:** The Princess loads the quantized model into its fenced VRAM (8GB limit). The OpenClaw environment initializes.

### Phase 5: Forager Pulse (Swarm Synchronization)

With "The Skill" active, the Princess looks outward to organize its local workers.

- **Discovery:** The Princess broadcasts a local pulse to find any Forager Nodes (Jetson AGX Thor) on the network.
- **Telemetry Mesh:** The Thors begin streaming environmental data (market signals, sensor feeds, or telemetry) to the Princess.
- **Reasoning Loop:** The Princess uses Ollama to analyze the incoming data, looking for high-value opportunities defined in "The Skill."

### Phase 6: The First Broadcast (Mainnet Genesis)

The Genesis cycle completes when the swarm performs its first sovereign action.

- **Batch Creation:** The Princess aggregates data from the Thors and formulates a transaction batch.
- **Manual Sting Confirmation:** For this first P1 transaction, the user sees a notification on the kytinOS Mobile App and confirms the action by tapping the Sting.
- **Sovereign Broadcast:** The signed transaction is sent to the Queen (RTX 6000 Ada), which injects it directly into the blockchain.
- **Apiary Active:** The mainnet recognizes the new Hive ID. The localized swarm is now an official participant in the Bee Economy.

### Genesis Status

| Component    | Status     | Role in Genesis                            |
| :----------- | :--------- | :----------------------------------------- |
| RTX 6000 Ada | `ONLINE`   | Sovereign RPC Gateway & Knowledge Provider |
| Jetson Orin  | `ACTIVE`   | Local Princess / Orchestrator              |
| T-dongle S3  | `INSERTED` | Physical State-Lock / Authorized           |
| Jetson Thor  | `SYNCED`   | Forager / Telemetry Ingestion              |

This initialization ensures that from the very first second, your business is protected by **Dual-Factor Physicality** and **Sovereign Infrastructure**.

### Genesis Deployment Checklist

Before running the "Genesis Moment" boot sequence, ensure the Queen (RTX 6000 Ada) has:

- [ ] Docker containers for your blockchain node software (e.g., Solana or Ethereum full-node indexer).
- [ ] The `HIVE_SECRET` set in the environment variables (matching the Sting's firmware).
- [ ] The `queen/princess_validator.py` service running on port `8888` and exposed through your secure tunnel (WireGuard or similar).

## 🌐 The Kytin Sovereign Mesh (Decentralized RPC)

Instead of a hub-and-spoke model, the entire Global Intelligence Network becomes a cooperative web. **Any Queen (RTX 6000 Ada) can relay transactions for any Princess (Orin).**

### How the Relay Works

1. **The Princess Formulates:** The local Orin analyzes data and builds the transaction.
2. **The Sting Locks It:** The user inserts the T-dongle S3. The transaction is cryptographically signed and "State-Locked."
3. **The Broadcast Request:** The Orin cannot reach the blockchain directly. It casts a signed, encrypted "Blind Courier" packet to the Global Intelligence Network asking: _"Is there a Queen available to broadcast this?"_
4. **The Queen Relays:** An active Queen picks up the packet, submits it to the blockchain, and claims the attached **Nectar Bounty** ($RESIN micro-toll).

### Zero-Trust Relaying (Why This is Secure)

- **Immutable Signatures:** The transaction is signed at the edge by the physical Sting. If a relaying Queen alters the recipient address or amount, the cryptographic hash breaks and the blockchain rejects it.
- **Blind Couriers:** The Queen sees the transaction envelope but cannot read the underlying strategy or logic of the localized Skill. The Orin uses the Sting to seal it.
- **Sybil Resistance:** Every request includes the `ORIN_ANCHOR_ID` and the Sting's signature — malicious actors cannot flood the network with fake requests.

### Relay Nectar (The Incentive Layer)

Enterprise users running Queens earn passive yield by relaying transactions for home-based Princess nodes:

- The Princess attaches a micro-toll (`nectar_bounty` in $RESIN) to every relay packet.
- The Queen that successfully confirms the TX on the blockchain claims the bounty.
- This creates a self-sustaining DePIN economy — Queens compete to provide fast, reliable relay services.

| Participant            | Benefit                                                                           |
| :--------------------- | :-------------------------------------------------------------------------------- |
| **Consumer (Orin)**    | Global supercomputer network access for a tiny Nectar tip.                        |
| **Enterprise (Queen)** | Passive income from idle compute — never-idle RTX 6000 Ada.                       |
| **The Business**       | No server farm needed. Community provides hardware; State-Lock provides security. |

### P2P Discovery Protocol (Kademlia DHT)

To eliminate any central directory, the Princess discovers available Queens using a **Distributed Hash Table** — the same technology used by BitTorrent and Ethereum.

1. **Bootstrap Phase:** On first run, the Orin contacts the `BOOTSTRAP_PEER_IP` (your primary Queen). After connecting, it automatically learns about every other node in the network.
2. **DHT Announcements:** The Princess publishes its `ORIN_ANCHOR_ID` to the mesh and searches the `active_queen_nodes` key for relay partners.
3. **Fault Tolerance:** If the primary Queen goes offline, the Orin queries the DHT for the next available Queen. The Bee Economy stays alive even if individual hives disconnect.

#### Swarm Hierarchy Roles (DHT Mapping)

| DHT Key                   | Value            | Purpose                                                  |
| :------------------------ | :--------------- | :------------------------------------------------------- |
| `active_queen_nodes`      | IP1, IP2, IP3... | Allows Princesses to find available RTX 6000 Ada relays. |
| `kytin_princess_[ID]`     | STATUS           | Allows the Queen to verify a Princess's health.          |
| `skill_genesis_lite_hash` | SHA256_HASH      | Ensures every node runs the same version of The Skill.   |

> **Security Guardrail:** Even though discovery is open, a Queen will not communicate with a Princess unless the initial handshake includes a valid Sting signature. `p2p_discovery.py` finds the **door** (the Queen's IP); `sting_gatekeeper.py` provides the **key** to open it.

### The Relay Transmitter (`relay_transmitter.py`)

The transmitter is the engine that moves State-Locked packets from the Princess to discovered Queens:

1. **Selection:** Iterates through the Queen list from `p2p_discovery.py`. (Future: select by proximity or reputation score.)
2. **Encapsulation:** Wraps the Sting-signed TX hex in a Blind Courier JSON envelope with the Nectar Bounty attached.
3. **Handshake:** Hits the Queen's `/authorize_princess` endpoint. If valid, the Queen accepts the Nectar and pushes the TX to the blockchain.

**Compliance Checklist (Builder Agent):**

- [ ] Timeout handling: Dead Queens timeout at 10 seconds.
- [ ] Packet integrity: Queen response includes a TX hash receipt for the Clawhub dashboard.
- [ ] Privacy: Only the signed TX hex leaves the Orin — the private key never touches RAM (the Sting handles signing internally).

### Transaction Monitor (`transaction_monitor.py`)

The final piece of the Genesis Loop. Polls the Queen's `/tx_status/{tx_id}` endpoint and drives physical feedback on the Sting's LCD.

| Sting Display | Meaning                                | LED Color |
| :------------ | :------------------------------------- | :-------- |
| `TX_PENDING`  | Transaction submitted, awaiting ledger | Amber     |
| `TX_SUCCESS`  | Confirmed on mainnet — Gold Hexagon    | Green     |
| `TX_FAILED`   | Relay or ledger rejection              | Red       |
| `TX_TIMEOUT`  | No confirmation within 5 minutes       | Red flash |

### The Sovereign Chain of Command

| Action        | Hardware     | Logic Layer                     |
| :------------ | :----------- | :------------------------------ |
| **Decide**    | Jetson Orin  | The Skill (Ollama / n8n)        |
| **Authorize** | T-dongle S3  | Physical Signature (Sting)      |
| **Broadcast** | RTX 6000 Ada | Sovereign RPC (Queen)           |
| **Confirm**   | Jetson Orin  | Transaction Monitor → Sting LCD |

## 🛰️ The Apiary & Clawhub Integration

The Apiary serves as the decentralized repository for "Skills" (Books) logic. The local dashboard (Clawhub) mirrors this functionality for the local hive.

- **Ingress:** Pulls global sentiment and "Skill" deltas via atomic updates from the Apiary.
- **Hardware Validation:** Skill downloads require a physical signature from the T-dongle S3 to verify tier access.
- **Egress:** Pushes State-Locked transaction batches to the Queen nodes.
- **Visualization:** Managed via the Clawhub (kytinOS Dashboard/Mobile App).

### 🖥️ kytinOS Dashboard UI Architecture

The Clawhub is the mission control center for the localized Orin swarm, divided into four primary quadrants:

1. **Global Intelligence Header (The "Skyline"):**
   - Shows connection heartbeat to the Global Intelligence Network.
   - **Sting Authentication Badge:** Red (Missing), Yellow (Authenticating), Green (State-Locked & Secured).
   - **Swarm Consensus:** A Trust Score representing agreement between the Mini-Queen and Foragers.
2. **Swarm Topology (The "Hive View"):**
   - Visual map of localized Jetson hardware.
   - Live VRAM Heatmap ensuring Ollama has headroom for "The Skill".
3. **Financial Intelligence Pane (Executing "The Skill"):**
   - **Skill Intent:** Displays the active "Book" logic (e.g., Genesis Lite: Market Arb).
   - **Reasoning Feed:** Live-scroll of Ollama output.
   - **Execution Signal:** High-contrast Execute/Hold indicator.
   - **Trade Ledger:** List of local financial actions awaiting final state-lock signature.
4. **Protocol & Security Monitor (The "State-Lock"):**
   - Read-only Resin DSL execution log.
   - SHA-256 Hash Verification of the active Skill.
   - Real-time T-Dongle S3 telemetry (temperature, auth-cycle count).

**The "Sting" Interaction Flow on kytinOS:**

- **Gated Access:** Execution buttons are greyed out ("Awaiting State-Lock").
- **Physical Authentication:** When the Python daemon verifies the Sting, the UI performs a "Pulse Animation" across the Hive View.
- **Active Execution:** "The Skill" section illuminates, reasoning feeds populate, and the administrator can authorize workloads or dynamically toggle "Skill Intents" (e.g., switching from financial trading to energy logistics).

### 🏦 The Apiary: State-Locked Transaction Vault

The specific module within the Apiary that tracks the movement of value and logic from the localized Orin swarm up to the high-tier Queen nodes.

1. **The Batching Ledger (Local Swarm View):**
   - Displays how the Mini-Queen aggregates telemtry and trade signals into a single "State-Locked Batch".
   - Shows Originating Nodes, Intent, Payload Size, and the interactive **Protocol Status** (Queued, Pending Signature, State-Locked).
2. **The Queen Handoff (Uplink Status):**
   - Visualizes the transmission of the signed batch from the local Orin swarm to the Queen node.
   - Shows Uplink Target, Compression Ratio, Verification Latency, and Mainnet Broadcast status.
3. **The Resin DSL `SwarmHandoff` Module:**
   - Controls how the Orin decides to "close" a batch (e.g. `BATCH_SIZE >= 10.0KB` or `TIME_ELAPSED >= 60S`).
   - Ensures that the `T_DONGLE_S3` is authenticated before applying a State-Lock, applying `ALGO_GENESIS_LITE` compression, and executing the transmission to the Queen.

### 🚨 The "Sting Call" Notification Architecture

Ensures you are never disconnected from critical decision-making moments. The Resin DSL categorizes batches to prevent "alert fatigue".

**Alert Tiers:**

| Priority | Level      | Action Requirement                                                |
| :------- | :--------- | :---------------------------------------------------------------- |
| **P3**   | Routine    | Log only in Apiary. Auto-signed by local Mini-Queen.              |
| **P2**   | Sensitive  | Desktop notification on Apiary. Active Sting connection required. |
| **P1**   | High-Value | Mobile Push + Desktop Alert. Manual Sting interaction required.   |

**kytinOS Dashboard (Apiary) Visual Feedback for P1 Events:**

- **Overlay:** A high-contrast modal appears: "AWAITING MANUAL STATE-LOCK."
- **Sting Status:** The T-dongle S3 icon pulses orange.
- **Handoff Counter:** A countdown timer shows how long the batch will remain "hot" before auto-cancelling to prevent stale market execution.

### 📱 kytinOS Mobile: The "Guardian" Interface

The mobile app acts as the portable lens for your localized swarm—a "Reasoning Viewer"—to provide the context needed before physically authorizing a P1 transaction. **The mobile app is strictly Read-Only.** You cannot sign a transaction remotely. Physical Proximity is mandatory to prevent remote exploits.

**UI Architecture:**

1. **The Alert Banner:** Displays the `Batch ID`, `Network Weight` (e.g., 1,200 THINK), and a `Countdown` to expiration.
2. **The Reasoning Feed:** Pulls the "thought process" from the Mini-Queen, highlighting Truth Pillars (e.g., _Sentiment_: 94%, _Liquidity_: 88%, _Risk_: 99%) followed by a concise 50-word LLM summary explaining why the State-Lock is requested.
3. **Swarm Health (Mini-Map):** A simplified view showing Orin status (Processing Reasoning), Thor status (Ingesting), and Sting Connection (Pulsing Orange for "Awaiting Insertion").

**User Interaction Flow:**

1. **Notification:** Phone vibrates with a `P1_SIGNATURE_REQ` alert securely routed via n8n.
2. **Review:** User opens the app, reads the Orin's reasoning and the Queen's global sentiment validation.
3. **Decision & Authorization:** If the logic is sound, the user physically walks to the Jetson AGX Orin and plugs in the T-Dongle S3.
4. **Execution:** The mobile app instantly updates to `STATE-LOCKED: SUCCESS` as the transaction is dispatched over the Kytin-Link.

## 🐳 Docker Deployment

The Princess node is orchestrated via `docker-compose.yml`, which launches four interconnected cells on the `kytin_internal` bridge network:

| Service         | Container       | Port    | Role                                         |
| :-------------- | :-------------- | :------ | :------------------------------------------- |
| `kytin-daemons` | `kytin_daemons` | —       | Sting handshake, P2P discovery, relay engine |
| `n8n`           | `kytin_n8n`     | `5678`  | Workflow engine for telemetry routing        |
| `ollama`        | `kytin_ollama`  | `11434` | Fenced LLM inference (The Skill)             |
| `clawhub`       | `kytin_clawhub` | `8080`  | kytinOS dashboard (Clawhub)                  |

### Key Configurations

- **Hardware Passthrough:** `kytin-daemons` runs in `privileged` mode with `/dev/ttyACM0` mapped so the Sting is visible inside the container.
- **GPU Acceleration:** Ollama uses the NVIDIA Container Runtime to access the Orin's CUDA cores.
- **Resource Fencing:** Ollama environment variables (`OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_FLASH_ATTENTION=1`) are baked into the compose file.

### First Launch

```bash
# From the kytin-princess-node root:
docker-compose up -d --build
```

### Post-Launch Verification

```bash
# 1. Check the Sting: T-dongle LCD should display PRINCESS SECURED
# 2. Check n8n: Navigate to http://localhost:5678
# 3. Check P2P Discovery: View daemon logs
docker logs -f kytin_daemons
```

### Compliance Checklist for the Builder Agent

Before deploying, verify these final states:

- [ ] Is the T-dongle S3 securely flashed with the Orin's hardware ID?
- [ ] Is the `.env` file populated from `daemon/identity.example`?
- [ ] Have the n8n webhooks been imported into the local Docker container?

> [!WARNING]
> **Security Warning**
> Note: This repository must never contain the `HIVE_SECRET` or any private cryptographic keys. All secrets must be handled by the Sting hardware or local environment variables. Remote signing is permanently disabled by the State-Locked Protocol.
