"""
TradeMemory + DKG + 0G Storage Combined

Combines:
- DKG causal relationships (from dkg.py)
- Encrypted 0G Storage (from storage_0g.py)

Flow:
1. Add memory → encrypt → upload to 0G → store CID
2. Query memory → fetch from 0G → decrypt → return
3. Causal links tracked locally + in 0G backup
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

try:
    from .storage_0g import TradeMemory0GStorage
except ImportError:
    from storage_0g import TradeMemory0GStorage


@dataclass
class DKGEdge:
    """A causal link between two memories."""

    from_id: str
    to_id: str
    relationship: str
    strength: float = 1.0


@dataclass
class CausalMemory:
    """A memory with DKG metadata."""

    memory_id: str
    memory_type: str
    content: Dict
    causes: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    og_cid: str = ""  # 0G Storage CID


class TradeMemoryDKG:
    """
    TradeMemory with DKG causal graph + 0G Storage.

    Storage: 0G (encrypted)
    Causal links: Tracked + backed up to 0G
    """

    def __init__(self, storage: TradeMemory0GStorage = None, local_path: str = None):
        """
        Initialize with 0G Storage.

        Args:
            storage: TradeMemory0GStorage instance (creates if None)
            local_path: Fallback local storage for causal edges (if 0G fails)
        """
        self.storage = storage or TradeMemory0GStorage()
        self.local_path = local_path or ".tradememory/dkg_0g"
        Path(self.local_path).mkdir(parents=True, exist_ok=True)

        self.memories: Dict[str, CausalMemory] = {}
        self.edges: List[DKGEdge] = []

        # Try to load from local cache
        self._load_cached_edges()

    def _load_cached_edges(self):
        """Load causal edges from local cache."""
        cache_file = Path(self.local_path) / "edges.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            for m in data.get("memories", []):
                self.memories[m["memory_id"]] = CausalMemory(**m)
            self.edges = [DKGEdge(**e) for e in data.get("edges", [])]

    def _save_edges(self):
        """Save causal edges locally."""
        data = {
            "memories": [
                {
                    "memory_id": m.memory_id,
                    "memory_type": m.memory_type,
                    "content": m.content,
                    "causes": m.causes,
                    "effects": m.effects,
                    "timestamp": m.timestamp,
                    "og_cid": m.og_cid,
                }
                for m in self.memories.values()
            ],
            "edges": [
                {
                    "from_id": e.from_id,
                    "to_id": e.to_id,
                    "relationship": e.relationship,
                    "strength": e.strength,
                }
                for e in self.edges
            ],
        }
        Path(self.local_path).joinpath("edges.json").write_text(
            json.dumps(data, indent=2)
        )

    def add_memory(
        self,
        memory_id: str,
        memory_type: str,
        content: Dict,
        caused_by: List[str] = None,
    ) -> CausalMemory:
        """
        Add a memory with causal links + 0G storage.

        1. Upload content to 0G Storage (encrypted)
        2. Track causal links locally
        """
        causes = caused_by or []

        # Create memory
        memory = CausalMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            causes=causes,
            effects=[],
            og_cid="",
        )

        # Upload to 0G Storage
        try:
            cid = self.storage.push_table(memory_id, [content])
            memory.og_cid = cid
            print(f"Uploaded to 0G: {cid}")
        except Exception as e:
            print(f"0G upload failed (using local): {e}")

        # Add to index
        self.memories[memory_id] = memory

        # Create causal edges
        for cause_id in causes:
            if cause_id in self.memories:
                edge = DKGEdge(from_id=cause_id, to_id=memory_id, relationship="caused")
                self.edges.append(edge)
                self.memories[cause_id].effects.append(memory_id)

        # Save causal links locally
        self._save_edges()

        return memory

    def get_memory(self, memory_id: str) -> CausalMemory:
        """Get a memory by ID."""
        return self.memories.get(memory_id)

    def query_causes(self, memory_id: str) -> List[CausalMemory]:
        """Get all memories that caused this memory."""
        if memory_id not in self.memories:
            return []
        return [self.memories[mid] for mid in self.memories[memory_id].causes]

    def query_causal_chain(self, memory_id: str, depth: int = 3) -> List[CausalMemory]:
        """Trace back the causal chain."""
        chain = []
        visited = set()

        def trace_down(mid, d):
            if d <= 0 or mid in visited:
                return
            visited.add(mid)

            if mid in self.memories:
                chain.append(self.memories[mid])
                for cause_id in self.memories[mid].causes:
                    trace_down(cause_id, d - 1)

        trace_down(memory_id, depth)
        return chain

    def explain(self, memory_id: str) -> str:
        """Generate a causal explanation."""
        if memory_id not in self.memories:
            return f"Memory {memory_id} not found"

        mem = self.memories[memory_id]
        parts = [
            f"[{mem.memory_type}] {memory_id}",
            f"  0G CID: {mem.og_cid}" if mem.og_cid else "  0G: pending",
        ]

        if mem.causes:
            causes = []
            for c in mem.causes:
                if c in self.memories:
                    causes.append(f"{c}: {self.memories[c].memory_type}")
            parts.append(f"  caused by: {', '.join(causes)}")

        if mem.effects:
            effects = []
            for e in mem.effects:
                if e in self.memories:
                    effects.append(f"{e}: {self.memories[e].memory_type}")
            parts.append(f"  led to: {', '.join(effects)}")

        return "\n".join(parts)


# ========== Example Usage ==========

if __name__ == "__main__":
    from storage_0g import TradeMemory0GStorage

    # Create storage (will try 0G, fallback to mock)
    storage = TradeMemory0GStorage()
    dkg = TradeMemoryDKG(storage)

    print("=== TradeMemory DKG + 0G Storage ===\n")

    # Layer 1: Episodic
    print("Adding trade memory...")
    trade = dkg.add_memory(
        "trade_xauusd_001",
        "episodic",
        {"symbol": "XAUUSD", "direction": "long", "entry": 2045, "pnl": -500},
    )

    # Layer 2: Semantic (caused by trade)
    print("Adding pattern...")
    pattern = dkg.add_memory(
        "pattern_breakout",
        "semantic",
        {"pattern": "afternoon breakout", "success_rate": 0.4},
        caused_by=["trade_xauusd_001"],
    )

    # Layer 3: Procedural (caused by pattern)
    print("Adding rule...")
    rule = dkg.add_memory(
        "rule_reduce_size",
        "procedural",
        {"action": "size = 50%", "when": "afternoon"},
        caused_by=["pattern_breakout"],
    )

    # Query
    print("\n=== Causal Chain ===")
    chain = dkg.query_causal_chain("rule_reduce_size")
    for mem in chain:
        print(dkg.explain(mem.memory_id))
        print()

    print("=== Done ===")
    print(f"Total memories: {len(dkg.memories)}")
    print(f"Total edges: {len(dkg.edges)}")
