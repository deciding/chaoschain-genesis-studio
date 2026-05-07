# DKG + ChaosChain + TradeMemory Integration Plan

## Overview

Integrate TradeMemory's OWM (Outcome-Weighted Memory) framework with ChaosChain SDK to implement your DKG.md vision: "ERC-7857 trading agents trading their own memories" with causal knowledge graphs and cryptographically secure ownership transfer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ERC-7857 iNFT Layer                       │
│  (owns encrypted memory key, ownership transfer, sealed executor)  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              DKG Causal Graph Layer                         │
│  (Action → Reflection → Strategy Update DAG)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              OWM Memory Layers                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Episodic │ │Semantic │ │Procedural│ │Affective│  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│  + Outcome-Weighted Recall (OWM core)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              0G Storage + On-Chain Commitment         │
│  (encrypted memory blobs, CID → chain hash)           │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: OWM Integration (Week 1-2)

Tasks:

- [ ] **T1.1**: Create `chaoschain_sdk/memory/` module
  - Copy OWM schema from TradeMemory `src/tradememory/db.py`
  - Adapt for agent-agnostic (not just MT5)
  - Add to SDK pyproject

- [ ] **T1.2**: Implement 4 memory layers
  - Episodic: trade records with context vector
  - Semantic: pattern discovery from episodic
  - Procedural: strategy + position sizing
  - Affective: streak + drawdown + confidence

- [ ] **T1.3**: Outcome-Weighted Recall function
  - Port from TradeMemory `recall_with_owm_score()`
  - Context similarity + outcome weighting

- [ ] **T1.4**: Integration with existing agents
  - `GenesisServerAgentSDK.memory -> OWM`
  - Auto-capture trades → episodic memory
  - Auto-generate reflections

### Phase 2: DKG Causal Graph (Week 2-3)

Tasks:

- [ ] **T2.1**: DAG schema for causal memories
  - Nodes: Action, Reflection, StrategyUpdate
  - Edges: causal relationships
  - Store in SQLite + 0G Storage backup

- [ ] **T2.2**: Causal graph builder
  - On trade close: extract Action node
  - LLM reflection → Reflection node
  - Strategy update → StrategyUpdate node
  - Link causally (A→R→S)

- [ ] **T2.3**: Causal proof generation
  - Generate DAG hash
  - Commit to chain (ERC-7846 or custom)

- [ ] **T2.4**: Verification API
  - `verify_causal_chain(agent_id)`
  - Check on-chain hash matches

### Phase 3: 0G Storage Integration (Week 3)

Tasks:

- [ ] **T3.1**: Encrypted storage client
  - Use 0G Storage API
  - Encrypt with agent's key before upload

- [ ] **T3.2**: Memory serialization
  - Serialize OWM layers → JSON
  - Encrypt → upload to 0G → get CID

- [ ] **T3.3**: On-chain commitment
  - Store CID + hash in ERC-7857 metadata
  - Implement `commitMemory(cid)` function

- [ ] **T3.4**: Retrieval from storage
  - Fetch by CID → decrypt → load into memory

### Phase 4: ERC-7857 iNFT Implementation (Week 4)

Tasks:

- [ ] **T4.1**: ERC-7857 smart contract (Solidity)
  - `iNFT.sol`: mint with encrypted metadata
  - `ownership transfer`: trigger re-encryption
  - `tokenURI`: point to 0G CID

- [ ] **T4.2**: Key management
  - Generate agent key pair
  - Store encrypted key in metadata
  - Update on ownership transfer

- [ ] **T4.3**: TEE/ZKP integration (optional, Phase 4b)
  - Mock for now (placeholder for production)
  - `reEncrypt(oldKey, newKey)` function

### Phase 5: Sealed Executor (Rental Mode) (Week 5)

Tasks:

- [ ] **T5.1**: Rental smart contract
  - `authorizeUsage(renter, duration)`
  - `revokeUsage(renter)`

- [ ] **T5.2**: Execution environment
  - TEE placeholder (local for now)
  - Input: trading request
  - Output: signal only (no data leak)

- [ ] **T5.3**: Payment integration
  - Renters pay A0GI
  - Auto-extend or expire access

## File Structure

```
chaoschain_sdk/
├── memory/
│   ├── __init__.py
│   ├── episodic.py      # Episode memory
│   ├── semantic.py    # Pattern memory
│   ├── procedural.py  # Strategy memory
│   ├── affective.py # State memory
│   ├── recall.py     # OWM recall function
│   └── db.py        # SQLite schema
├── dkg/
│   ├── __init__.py
│   ├── dag.py        # Causal graph
│   ├── nodes.py      # Action/Reflection/Strategy nodes
│   └── commitment.py # On-chain commitment
├── storage/
│   ├── __init__.py
│   ├── encrypted.py  # Encrypted 0G storage
│   └── commitment.py # Chain hash commitment
└── inft/
    ├── __init__.py
    ├── contract.py   # ERC-7857 contract
    └── keymgmt.py   # Key management
```

## Dependencies

```python
# requirements.txt additions
cryptography>=42.0.0  # For encryption
web3>=6.0.0        # For 0G interactions
```

## Key API Changes

```python
# New: Agent with memory
agent = ChaosChainAgentSDK(
    agent_name="Trader1",
    enable_memory=True,      # NEW: OWM memory
    enable_dkg=True,       # NEW: causal graph
    enable_inft=True,      # NEW: ERC-7857 iNFT
    enable_rental=False,   # NEW: sealed executor
)

# Store trade → automatic episodic memory
agent.execute_trade(symbol="XAUUSD", direction="long")
# → Creates Action node + Reflection (via LLM) + StrategyUpdate (if any)

# Recall with OWM scoring
memories = agent.recall(context={"regime": "trending", "session": "london"})
# → Outcome-weighted recall from OWM

# Get causal proof
proof = agent.get_causal_proof()
# → DAG hash for on-chain commitment

# Mint as iNFT (ERC-7857)
token_id = agent.mint_iNFT()
# → Mints NFT with encrypted memory key

# Transfer ownership (secure)
agent.transfer_iNFT(to_address, reencryption_proof)
# → Transfers with TEE/ZKP re-encryption
```

## Testing Strategy

1. Unit tests for each memory layer
2. Integration test: trade → memory → recall
3. DKG test: verify causal chain
4. Storage test: encrypt → upload → retrieve
5. iNFT test: mint → transfer → decrypt

## Notes

- TradeMemory's MCP tools (`store`, `recall`, `performance`, `reflection`) become SDK methods
- SSRT (Statistical Regime detection) ported as `detect_regime()` method
- DQS integrated into `validate_data_quality()`
- Original TradeMemory = MT5-specific, this adaptation = agent-agnostic