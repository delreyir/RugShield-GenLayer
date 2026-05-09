<div align="center">
  <h1>🛡️ RugShield | AI-Powered Smart Escrow</h1>
  <p><strong>An Intelligent Contract built natively on GenLayer Studionet.</strong></p>
  <p>
    <a href="https://rug-shield-gen-layer.vercel.app/">Live Demo</a> ·
    <a href="https://docs.genlayer.com">GenLayer Docs</a>
  </p>
</div>

---

**RugShield** is an Intelligent Contract that leverages GenVM's decentralized AI consensus to protect Web3 investors from rug pulls and scams *before* releasing locked funds. The contract uses an on-chain reputation registry combined with non-comparative LLM consensus to classify any cryptocurrency token.

## 🚨 The Problem
Traditional smart contracts are "blind" to real-world events. Once funds are locked in an escrow, the contract has no awareness of off-chain news, audits, or exploit disclosures. If a developer is exposed as a scammer minutes after a deposit, a standard EVM contract still blindly releases the funds.

## 💡 The Solution: Intelligent Escrow
RugShield introduces the concept of an **Intelligent Escrow** that queries the real world and reaches AI consensus before executing financial actions.

### How It Works
1. **Lock (`create_escrow`):** A user locks GEN tokens for a specific token/project. State is stored in `TreeMap` fields (one per attribute) as `LOCKED`.
2. **Audit (`evaluate_and_execute`):** The contract first checks an on-chain reputation registry (a deterministic whitelist of major legitimate tokens and a blacklist of known rug pulls).
3. **AI Consensus (fallback):** For any token outside the registry, the contract calls `gl.eq_principle.prompt_non_comparative(input, task, criteria)` — the leader LLM classifies the token, and every validator independently re-validates that output against the same criteria.
4. **Settle:**
   - ✅ **SAFE:** Funds are released to the developer.
   - 🚨 **RUG / UNVERIFIED:** Funds are automatically refunded to the investor to ensure safety.

## 🛠️ Technical Stack

### Intelligent Contract (`anti_rug_escrow.py`)
* **Base Class:** `class RugShieldEscrow(gl.Contract)` — the standard base for Intelligent Contracts.
* **Storage:** `TreeMap[u256, str]` and `TreeMap[u256, u256]` (one TreeMap per field, no Python dicts) — GenVM-compatible persistent state.
* **Decorators:** `@gl.public.write` for state-mutating methods, `@gl.public.view` for read-only queries.
* **AI Consensus:** `gl.eq_principle.prompt_non_comparative(input=..., task=..., criteria=...)` — the validator set re-validates the leader's classification against shared criteria. This is more robust than `prompt_comparative` for short categorical outputs.
* **Determinism:** A curated on-chain whitelist/blacklist short-circuits the consensus path for the top ≈100 tokens, keeping gas low and results predictable.
* **Network:** GenLayer Studionet (Chain ID: `61999`).

### Real GenLayer SDK Primitives Used

| Primitive | Role |
|---|---|
| `gl.Contract` | Base class for the Intelligent Contract |
| `@gl.public.write` | State-mutating methods (`create_escrow`, `evaluate_and_execute`) |
| `@gl.public.view` | Read-only methods (`get_escrow`, `get_total_escrows`) |
| `gl.eq_principle.prompt_non_comparative(input, task, criteria)` | Optimistic Democracy consensus on the LLM classification |
| `TreeMap[u256, str]` / `TreeMap[u256, u256]` | On-chain storage — one TreeMap per escrow field |
| `u256` | Native unsigned-256-bit integer type for IDs and amounts |

### Frontend Simulation
* **Stack:** HTML5, Tailwind CSS, Vanilla JavaScript.
* **Connection:** Wallet integration via MetaMask/Rabby.
* **RPC Endpoint:** `https://rpc.studionet.genlayer.com`

## 🚀 Local Environment Setup

### 1. Clone the Project
```bash
git clone https://github.com/delreyir/RugShield-GenLayer.git
cd RugShield-GenLayer
```

### 2. Deploy the Contract (GenLayer Studio)
1. Open [studio.genlayer.com](https://studio.genlayer.com)
2. Open `anti_rug_escrow.py` from this repo, copy the full contents into the **Contracts** tab
3. Click **Deploy** — no constructor arguments needed
4. Paste the deployed address into `index.html` (`CONTRACT_ADDRESS`)

### 3. Frontend
No `npm` or build tools required. Simply open `index.html` in your browser, or:
```bash
python3 -m http.server 8000
```

## 📖 Testing the Contract

In GenLayer Studio → **Run & Debug**, test the full flow:

| Step | Method | Input | Expected Output |
|---|---|---|---|
| 1 | `create_escrow` | `"ETH", 100` | Returns escrow ID `1` |
| 2 | `evaluate_and_execute` | `escrow_id: 1` | `RELEASED` (whitelist hit) |
| 3 | `get_escrow` | `escrow_id: 1` | Full escrow state dict |
| 4 | `create_escrow` | `"SQUID", 50` | Returns escrow ID `2` |
| 5 | `evaluate_and_execute` | `escrow_id: 2` | `REFUNDED` (blacklist hit) |
| 6 | `create_escrow` | `"SomeUnknownCoin", 25` | Returns escrow ID `3` |
| 7 | `evaluate_and_execute` | `escrow_id: 3` | `RELEASED` / `REFUNDED` (LLM consensus path)|

### Decision Examples

| Token | Path | Expected Decision | Outcome |
| :--- | :--- | :--- | :--- |
| **ETH, BTC, SOL, USDC, ...** | On-chain whitelist | `SAFE` | ✅ Funds Released |
| **SQUID, FTT, LUNA, SafeMoon, ...** | On-chain blacklist | `RUG` | 🚨 Automatic Refund |
| **Any other token** | `prompt_non_comparative` LLM consensus | `SAFE` / `RUG` / `UNVERIFIED` | According to validator agreement |

---

## How the Decision Flow Works

```
evaluate_and_execute(escrow_id)
    │
    ├── 1. Whitelist check  (deterministic, no consensus needed)
    │     token in SAFE_TOKENS  → RELEASED
    │
    ├── 2. Blacklist check  (deterministic)
    │     token in RUG_TOKENS   → REFUNDED
    │
    └── 3. AI fallback  (only for unknown tokens)
          gl.eq_principle.prompt_non_comparative(
              input    = "Cryptocurrency token: <token>",
              task     = "Classify as SAFE / RUG / UNVERIFIED",
              criteria = "Output exactly one uppercase word ..."
          )
          → Optimistic Democracy: leader proposes, validators verify
          → RELEASED / REFUNDED based on consensus result
```

---

## 🏆 Submission: GenLayer Projects & Milestones

| Requirement | Implementation |
|---|---|
| ✅ Intelligent Contract | `anti_rug_escrow.py` — built with real GenLayer SDK |
| ✅ Real SDK primitives only | `gl.Contract`, `@gl.public.write`, `@gl.public.view`, `gl.eq_principle.prompt_non_comparative`, `TreeMap`, `u256` |
| ✅ On-chain storage | `TreeMap[u256, str]` / `TreeMap[u256, u256]` per field — no Python dicts |
| ✅ Optimistic Democracy | `gl.eq_principle.prompt_non_comparative(input, task, criteria)` — validators verify the leader's classification |
| ✅ Deployed on Studionet | Studionet (Chain ID `61999`); paste the deployed address into `index.html` |
| ✅ Frontend demo | `index.html` — dark-mode UI with wallet connect & animated GenVM terminal |

---

*Built for the GenLayer Ecosystem. RugShield demonstrates the power of AI-native Intelligent Contracts.*

> **Note:** Decisions for whitelisted/blacklisted tokens are fully deterministic. For all other tokens, the outcome depends on validator agreement under `gl.eq_principle.prompt_non_comparative`.
