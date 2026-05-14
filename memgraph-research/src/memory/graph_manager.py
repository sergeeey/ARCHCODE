"""
Graph Manager - Handles Neo4j connection with NetworkX fallback.

Architecture:
- Try Neo4j first (if available)
- Fallback to NetworkX (in-memory) if Neo4j unavailable
- Unified interface for both backends
"""

from typing import Optional, List, Dict, Any
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class GraphManager:
    """Manages research memory graph with automatic backend selection."""

    def __init__(self, uri: Optional[str] = None, user: str = "neo4j", password: str = ""):
        self.backend = None
        self.driver = None
        self.graph = None  # NetworkX fallback

        # Try Neo4j first
        if uri:
            try:
                from neo4j import GraphDatabase

                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.driver.verify_connectivity()
                self.backend = "neo4j"
                logger.info(f"✓ Connected to Neo4j at {uri}")
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}")
                self._init_networkx_fallback()
        else:
            self._init_networkx_fallback()

    def _init_networkx_fallback(self):
        """Initialize NetworkX in-memory graph as fallback."""
        import networkx as nx

        self.graph = nx.MultiDiGraph()
        self.backend = "networkx"
        logger.info("✓ Using NetworkX in-memory graph (fallback)")

    def add_project(self, project_id: str, metadata: Dict[str, Any]) -> None:
        """Add project node to graph."""
        if self.backend == "neo4j":
            with self.driver.session() as session:
                session.run(
                    "MERGE (p:Project {id: $id}) SET p += $metadata",
                    id=project_id,
                    metadata=metadata,
                )
        else:
            self.graph.add_node(project_id, type="Project", **metadata)

    def add_hypothesis(
        self, hyp_id: str, project_id: str, text: str, score: float, metadata: Dict[str, Any]
    ) -> None:
        """Add hypothesis node linked to project."""
        if self.backend == "neo4j":
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (h:Hypothesis {id: $hyp_id})
                    SET h.text = $text, h.score = $score, h += $metadata
                    WITH h
                    MATCH (p:Project {id: $project_id})
                    MERGE (p)-[:HAS_HYPOTHESIS]->(h)
                    """,
                    hyp_id=hyp_id,
                    project_id=project_id,
                    text=text,
                    score=score,
                    metadata=metadata,
                )
        else:
            self.graph.add_node(hyp_id, type="Hypothesis", text=text, score=score, **metadata)
            self.graph.add_edge(project_id, hyp_id, relation="HAS_HYPOTHESIS")

    def add_similarity_edge(self, hyp_id_1: str, hyp_id_2: str, similarity: float) -> None:
        """Add similarity edge between hypotheses."""
        if self.backend == "neo4j":
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (h1:Hypothesis {id: $id1})
                    MATCH (h2:Hypothesis {id: $id2})
                    MERGE (h1)-[:SIMILAR_TO {score: $similarity}]->(h2)
                    """,
                    id1=hyp_id_1,
                    id2=hyp_id_2,
                    similarity=similarity,
                )
        else:
            self.graph.add_edge(hyp_id_1, hyp_id_2, relation="SIMILAR_TO", score=similarity)

    def get_similar_hypotheses(
        self, project_id: str, min_similarity: float = 0.7, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve similar hypotheses from other projects."""
        if self.backend == "neo4j":
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (source:Project {id: $project_id})-[:HAS_HYPOTHESIS]->(h1:Hypothesis)
                    MATCH (h1)-[sim:SIMILAR_TO]->(h2:Hypothesis)<-[:HAS_HYPOTHESIS]-(target:Project)
                    WHERE target.id <> $project_id AND sim.score >= $min_sim
                    RETURN h2.id as id, h2.text as text, h2.score as score,
                           sim.score as similarity, target.id as source_project
                    ORDER BY sim.score DESC
                    LIMIT $limit
                    """,
                    project_id=project_id,
                    min_sim=min_similarity,
                    limit=limit,
                )
                return [dict(record) for record in result]
        else:
            # NetworkX fallback
            similar = []
            for node, data in self.graph.nodes(data=True):
                if data.get("type") == "Hypothesis":
                    # Get incoming similarity edges
                    for pred in self.graph.predecessors(node):
                        for edge_key, edge_data in self.graph[pred][node].items():
                            if edge_data.get("relation") == "SIMILAR_TO":
                                sim_score = edge_data.get("score", 0)
                                if sim_score >= min_similarity:
                                    similar.append(
                                        {
                                            "id": node,
                                            "text": data.get("text"),
                                            "score": data.get("score"),
                                            "similarity": sim_score,
                                            "source_project": self._get_project_for_hypothesis(
                                                pred
                                            ),
                                        }
                                    )
            return sorted(similar, key=lambda x: x["similarity"], reverse=True)[:limit]

    def _get_project_for_hypothesis(self, hyp_id: str) -> Optional[str]:
        """Find project that owns this hypothesis (NetworkX only)."""
        for pred in self.graph.predecessors(hyp_id):
            if self.graph.nodes[pred].get("type") == "Project":
                return pred
        return None

    def save_to_file(self, path: Path) -> None:
        """Persist graph to JSON (NetworkX only, Neo4j is already persistent)."""
        if self.backend == "networkx":
            import networkx as nx

            data = nx.node_link_data(self.graph)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"✓ Graph saved to {path}")

    def load_from_file(self, path: Path) -> None:
        """Load graph from JSON (NetworkX only)."""
        if self.backend == "networkx":
            import networkx as nx

            with open(path) as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data, directed=True, multigraph=True)
            logger.info(f"✓ Graph loaded from {path}")

    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
