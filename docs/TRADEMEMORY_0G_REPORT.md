# TradeMemory + DKG + 0G Storage
## AI Trading Agent Memory Infrastructure Proposal

**Presented to:** 0G Labs  
**Date:** May 2026  
**Status:** Technical Proof of Concept

---

## Executive Summary

We propose integrating **TradeMemory** (AI trading agent memory system) with **DKG** (Distributed Knowledge Graph) and **0G Storage** to create a decentralized, tradable memory infrastructure for AI trading agents.

**Key Value Proposition:**
- AI trading agents can now own, trade, and monetize their trading memories
- Memories become verifiable, transferable assets
- Enables "AI trading agent marketplaces" where successful agent memories can be sold/rented

---

## Why TradeMemory?

### The Problem: AI Agents Have No Memory

Current AI trading agents:
- Start fresh on every deployment
- No accumulated experience
- Can't learn from past trades
- Can't transfer knowledge to other agents

### The Solution: Outcome-Weighted Memory (OWM)

TradeMemory implements a 4-layer cognitive memory architecture inspired by human memory:

| Layer | Function | Example |
|-------|----------|---------|
| **Episodic** | Specific experiences | "Lost $500 on XAUUSD breakout on March 15" |
| **Semantic** | Generalized patterns | "Breakout strategies work 73% in trending markets" |
| **Procedural** | Action rules | "Use 2% risk per trade, max 5% total" |
| **Affective** | Emotional state | "3 losses → nervous → reduce size" |

### Why 4 Layers?

Based on cognitive science (Tulving, LeDoux):
- **Episodic**: Captures specific trades (what happened)
- **Semantic**: Generalizes patterns (what works)
- **Procedural**: Encodes habits (how to act)
- **Affective**: Tracks emotional drift (how we feel)

Each layer interacts: emotional state → which patterns you recall → which rules you follow → what trades you make → new memories → updated emotions

---

## Why DKG? (Distributed Knowledge Graph)

### The Trust Problem

If I sell you my "trading memory", how do you know it's real?
- Did these trades actually happen?
- Is the pattern legitimate?
- Was the strategy actually profitable?

### The Solution: Causal Links

DKG adds **"because" relationships** between memories:

```
Trade A (episodic) ──caused──→ Pattern B (semantic) ──caused──→ Rule C (procedural)
     │                              │                              │
     └──→ Emotional State D        └──→ New Trade E            └──→ ...
```

**Example causal chain:**
```
1. Trade: XAUUSD long @ 2045 → -$500 (episodic)
   ↓ caused
2. Pattern: "Afternoon breakouts fail 60% of time" (semantic)
   ↓ caused  
3. Rule: "Reduce position size 50% in afternoon" (procedural)
   ↓ caused
4. State: "Frustrated, on 3-loss streak" (affective)
```

**Benefits:**
- Verifiable: Each link can be cryptographically proven
- Traceable: Query "what caused my biggest loss?"
- Valuable: Buyers know the causal story behind a strategy

---

## Why 0G Storage?

### Storage Requirements

- **Large data**: Trading history, patterns, proofs (can be GBs)
- **Permanent**: Must survive agent lifetime
- **Secure**: Trading strategies are valuable IP
- **Decentralized**: No single point of failure
- **Affordable**: High-volume memory storage

### Why 0G?

| Feature | Benefit |
|---------|----------|
| **Decentralized** | No single point of failure |
| **High throughput** | Fast uploads/downloads |
| **Low cost** | Cheaper than Arweave/Filecoin |
| **EVM compatible** | Easy integration with Ethereum tools |
| **Encryption** | Client-side encryption before upload |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ERC-7857 iNFT Layer                         │
│  (Intelligent NFT - Owns memory decryption key)            │
│  • Ownership transfer with TEE/ZKP verification            │
│  • "Sealed Executor" rental mode (AIaaS)                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DKG Causal Graph Layer                    │
│  • Action → Reflection → Strategy Update DAG             │
│  • Causal proofs for every pattern                       │
│  • Query: "What caused this trade?"                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OWM Memory Layers                        │
│  ┌─────────┐  ┌─────────┐  ┌────────────┐  ┌──────────┐  │
│  │Episodic │→ │Semantic │→ │Procedural  │→ │ Affective│  │
│  └─────────┘  └─────────┘  └────────────┘  └──────────┘  │
│  + Outcome-Weighted Recall (relevance scoring)           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    0G Storage Layer                         │
│  • Encrypted memory blobs (AES-256)                      │
│  • CID stored on-chain (commitment)                   │
│  • Client-side encryption (0G never sees plaintext)    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Status

### Completed ✅

| Component | File | Status |
|-----------|------|--------|
| OWM Memory | `tradememory/` | Local JSON ✅ |
| DKG Causal | `tradememory/dkg.py` | Local ✅ |
| DKG + 0G | `tradememory/dkg_0g.py` | Combined ✅ |
| 0G Storage Adapter | `tradememory/storage_0g.py` | SDK ready ⚠️ |

**Note:** 0G testnet storage currently experiencing timeouts. Mainnet infrastructure expected to stabilize soon.

### Code Structure

```
tradememory/
├── storage_0g.py    # Encrypted 0G Storage
├── dkg.py           # DKG causal layer  
├── dkg_0g.py       # Combined (DKG + 0G Storage)
└── __init__.py
```

---

## Future Plan: Multi-Agent MT5 Trading

### Phase 1: Single Agent Trading (Month 1)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MetaTrader5  │ ←──│ TradeMemory  │ ←──│   0G Storage │
│   (Trading)     │     │   (Memory)    │     │   (Persist)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   ChaosChain  │
                    │   Agent SDK   │
                    └─────────────┘
```

**Flow:**
1. Agent trades on MT5
2. Trade → Episodic memory
3. LLM reflection → Semantic pattern
4. Pattern → Procedural rule
5. All → 0G Storage (encrypted)

### Phase 2: Multiple Agents (Month 2-3)

```
MT5 Broker
    │
    ├── Agent Alice (trend follower)
    │   └── Memory: "Breakouts work in London"
    │
    ├── Agent Bob (range trader)  
    │   └── Memory: "Support/resistance in Asia"
    │
    └── Agent Charlie (signal provider)
        └── Pays Alice/Bob for signals
```

**Agent Types:**
- **Worker**: Executes trades, generates signals
- **Validator**: Verifies worker accuracy
- **Client**: Pays for signals/trades

### Phase 3: Memory Marketplace (Month 4-6)

```
┌─────────────────────────────────────────────┐
│         Memory Marketplace (0G AIverse)      │
│                                             │
│  Seller: "My agent made +200% in 6 months"  │
│    └── Memory CID: 0g://abc123...         │
│    └── Price: 1.0 ETH                      │
│                                             │
│  Buyer: "I want that strategy!"             │
│    └── Pay → Transfer ownership            │
│    └── Receive decryption key             │
│    └── Agent learns new memory            │
└─────────────────────────────────────────────┘
```

**Features:**
- List agent memories for sale
- Verification of performance claims
- Secure ownership transfer (TEE/ZKP)
- Rental mode (pay-per-use without transfer)

### Phase 4: Autonomous Agent Economy (Month 6+)

```
┌──────────────────────────────────────────────────┐
│           Agent Economy                         │
│                                                  │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│   │  Agent  │←───│  Memory │←───│   0G   │   │
│   │  (AI)   │    │ (Value) │    │ Storage │   │
│   └────┬────┘    └─────────┘    └─────────┘   │
│        │                                       │
│        ▼                                       │
│   ┌─────────┐    ┌─────────┐                   │
│   │  Trade  │───→│ Profit  │                   │
│   │  (MT5)  │    │   $    │                   │
│   └─────────┘    └─────────┘                   │
│        │                                       │
│        ▼                                       │
│   Reinvest / Pay rent / Sell memory           │
└──────────────────────────────────────────────────┘
```

---

## Technical Requirements

### For 0G

| Requirement | Purpose |
|------------|---------|
| Storage Indexer | Working indexer for uploads |
| A0GI token | Pay for storage transactions |
| Documentation | SDK integration guide |

### For TradeMemory

| Component | Status |
|----------|--------|
| MT5 connector | In TradeMemory external |
| LLM reflection | Uses OpenAI/Anthropic |
| Pattern detection | Statistical + LLM |
| Storage | 0G (pending) |

---

## Call to Action

1. **Immediate**: Fix 0G testnet storage timeouts
2. **Short-term**: Deploy working storage integration
3. **Medium-term**: Build multi-agent trading demo
4. **Long-term**: Enable memory marketplace

---

## Appendix: Key Files

| File | Purpose |
|------|---------|
| `tradememory/dkg_0g.py` | Combined DKG + 0G Storage |
| `tradememory/storage_0g.py` | 0G Storage adapter |
| `external/tradememory-protocol/` | TradeMemory source |
| `genesis_studio.py` | Demo with 3 agents |

---

**Questions?**

---

*Built with ChaosChain SDK + TradeMemory + 0G Storage*
