"""
TradeMemory + DKG (Distributed Knowledge Graph)

Adds causal relationships to the 4 OWM layers:
- Memories are linked by "because" relationships
- Creates a causal DAG (Directed Acyclic Graph)

Example causal chain:
  Trade A (episodic) → Pattern B (semantic) → Rule C (procedural)
       ↓ (led to)          ↓ (led to)           ↓ (caused)
   "lost $500"      "breakouts fail"    "reduce size 50%"
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DKGEdge:
    """A causal link between two memories."""

    from_id: str  # cause
    to_id: str  # effect
    relationship: str  # "caused", "led_to", "resulted_in"
    strength: float = 1.0  # confidence in the causal link


@dataclass
class CausalMemory:
    """A memory with DKG metadata."""

    memory_id: str
    memory_type: str  # "episodic", "semantic", "procedural", "affective"
    content: Dict
    causes: List[str] = field(default_factory=list)  # IDs this was caused by
    effects: List[str] = field(default_factory=list)  # IDs this caused
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TradeMemoryDKG:
    """
    TradeMemory with DKG causal graph.

    Each memory knows:
    - What caused it (causes)
    - What it caused (effects)
    """

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or ".tradememory/dkg"
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

        self.memories: Dict[str, CausalMemory] = {}
        self.edges: List[DKGEdge] = []

        self._load()

    def _load(self):
        """Load existing DKG."""
        memory_file = Path(self.storage_path) / "memories.json"
        if memory_file.exists():
            data = json.loads(memory_file.read_text())
            for m in data.get("memories", []):
                self.memories[m["memory_id"]] = CausalMemory(**m)
            self.edges = [DKGEdge(**e) for e in data.get("edges", [])]

    def _save(self):
        """Save DKG to disk."""
        data = {
            "memories": [
                {
                    "memory_id": m.memory_id,
                    "memory_type": m.memory_type,
                    "content": m.content,
                    "causes": m.causes,
                    "effects": m.effects,
                    "timestamp": m.timestamp,
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
        Path(self.storage_path).joinpath("memories.json").write_text(
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
        Add a memory with causal links.

        Args:
            memory_id: Unique ID
            memory_type: "episodic", "semantic", "procedural", "affective"
            content: The memory data
            caused_by: List of memory IDs that caused this

        Returns:
            The created memory
        """
        causes = caused_by or []

        # Create memory
        memory = CausalMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            causes=causes,
            effects=[],
        )

        # Add to index
        self.memories[memory_id] = memory

        # Create causal edges
        for cause_id in causes:
            if cause_id in self.memories:
                # Link cause → this memory
                edge = DKGEdge(from_id=cause_id, to_id=memory_id, relationship="caused")
                self.edges.append(edge)

                # Add to effect list
                self.memories[cause_id].effects.append(memory_id)

        self._save()
        return memory

    def query_causes(self, memory_id: str) -> List[CausalMemory]:
        """Get all memories that caused this memory."""
        if memory_id not in self.memories:
            return []
        return [self.memories[mid] for mid in self.memories[memory_id].causes]

    def query_effects(self, memory_id: str) -> List[CausalMemory]:
        """Get all memories caused by this memory."""
        if memory_id not in self.memories:
            return []
        return [self.memories[mid] for mid in self.memories[memory_id].effects]

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
        """Generate a causal explanation string."""
        if memory_id not in self.memories:
            return f"Memory {memory_id} not found"

        mem = self.memories[memory_id]
        parts = [f"[{mem.memory_type}] {memory_id}"]

        if mem.causes:
            causes = [
                f"{c}: {self.memories[c].memory_type}"
                for c in mem.causes
                if c in self.memories
            ]
            parts.append(f"  caused by: {', '.join(causes)}")

        if mem.effects:
            effects = [
                f"{e}: {self.memories[e].memory_type}"
                for e in mem.effects
                if e in self.memories
            ]
            parts.append(f"  led to: {', '.join(effects)}")

        return "\n".join(parts)


# ========== Example Usage ==========

if __name__ == "__main__":
    dkg = TradeMemoryDKG()

    # Layer 1: Episodic - Specific trade
    trade = dkg.add_memory(
        "trade_001", "episodic", {"symbol": "XAUUSD", "direction": "long", "pnl": -500}
    )

    # Layer 2: Semantic - Pattern discovered (caused by trade)
    pattern = dkg.add_memory(
        "pattern_001",
        "semantic",
        {"pattern": "breakout_afternoon", "success_rate": 0.4},
        caused_by=["trade_001"],
    )

    # Layer 3: Procedural - Rule created (caused by pattern)
    rule = dkg.add_memory(
        "rule_001",
        "procedural",
        {"action": "reduce_size_50%", "condition": "afternoon"},
        caused_by=["pattern_001"],
    )

    # Layer 4: Affective - Emotional state
    affect = dkg.add_memory(
        "state_001",
        "affective",
        {"streak": -3, "emotion": "frustrated"},
        caused_by=["trade_001"],
    )

    # Query causal chain
    print("=== Causal Chain for rule_001 ===")
    chain = dkg.query_causal_chain("rule_001")
    for m in chain:
        print(dkg.explain(m.memory_id))

    print("\n=== Full Explanation ===")
    print(dkg.explain("rule_001"))
