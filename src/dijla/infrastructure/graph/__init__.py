"""Memgraph knowledge graph adapter (real + in-memory fallback)."""

from dijla.infrastructure.graph.client import InMemoryKnowledgeGraph, MemgraphClient

__all__ = ["InMemoryKnowledgeGraph", "MemgraphClient"]
