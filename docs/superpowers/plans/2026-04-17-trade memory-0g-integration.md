# TradeMemory + ChaosChain Integration Plan (Simplified)

## Overview

Integrate TradeMemory's OWM (Outcome-Weighted Memory) framework with ChaosChain SDK, but replace SQLite with 0G Storage for persistence.

## Core Change

| Current (TradeMemory) | This Integration |
|---------------------|---------------|
| SQLite local storage | 0G Storage (encrypted) |
| MT5-specific | Agent-agnostic |
| MCP tools | SDK methods |

## OWM Layers (from TradeMemory)

```
┌─────────────────────────────────────────┐
│         Affective Memory               │
│   (streak, drawdown, confidence)       │
└─────────────────────────────────────────┘
              ▲
              │ reads
┌─────────────────────────────────────────┐
│         Procedural Memory              │
│   (strategy, position sizing)         │
└─────────────────────────────────────────┘
              ▲
              │ evolves from
┌─────────────────────────────────────────┐
│         Semantic Memory              │
│   (patterns discovered)             │
└─────────────────────────────────────────┘
              ▲
              │ aggregates
┌─────────────────────────────────────────┐
│         Episodic Memory             │
│   (trade records + context)           │
└─────────────────────────────────────────┘
              ▲
              │ writes
┌─────────────────────────────────────────┐
│        Trading Actions              │
└─────────────────────────────────────────┘
```

## Implementation

### Phase 1: OWM SDK Module (Week 1-2)

- [ ] Copy OWM schema from TradeMemory
- [ ] Adapt for agent-agnostic (not MT5-specific)
- [ ] Implement 4 memory layers

### Phase 2: 0G Storage Integration (Week 2)

- [ ] Replace SQLite with 0G Storage client
- [ ] Encrypt before upload
- [ ] Fetch and decrypt on retrieval
- [ ] Handle chain commitment (optional CID → hash)

### Phase 3: Agent Integration (Week 3)

- [ ] Add `enable_memory=True` to SDK
- [ ] Auto-capture trades → episodic
- [ ] Auto-LLM reflection → semantic
- [ ] OWM recall function

## File Structure

```
chaoschain_sdk/
└── memory/
    ├── __init__.py
    ├── episodic.py     # Trade records
    ├── semantic.py    # Patterns
    ├── procedural.py # Strategy
    ├── affective.py  # State
    ├── recall.py    # OWM recall
    ├── storage.py   # 0G encrypted storage
    └── client.py   # SDK wrapper
```

## Key API

```python
agent = ChaosChainAgentSDK(
    agent_name="Trader1",
    enable_memory=True,
)

# Trade → auto-captured to episodic memory
agent.execute_trade(symbol="XAUUSD", direction="long")

# Outcome-weighted recall
memories = agent.recall(context={"regime": "trending", "session": "london"})

# Get all layers
state = agent.get_memory_state()
# Returns: {episodic, semantic, procedural, affective}
```

## What We Skip (for now)

- ❌ DKG causal graph
- ❌ ERC-7857 iNFT
- ❌ Sealed executor (rental)
- ❌ On-chain commitment

These can be added later if needed.