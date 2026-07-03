"""
NetworkService
==============
Builds a criminal network graph connecting:
    Case ──► Accused ──► ArrestSurrender ──► Case

Uses NetworkX to compute graph metrics (degree centrality, betweenness)
and returns JSON structures compatible with React Flow / Cytoscape.js.

The LLM layer (Phase 9) will call this to identify key criminal nodes
for investigation insight summaries.
"""
from typing import Any, Dict, List, Optional

import networkx as nx
from sqlalchemy.orm import Session

from app.models.case import CaseMaster
from app.models.people import Accused
from app.models.arrest import ArrestSurrender
from app.database.repositories import case_repository, accused_repository


class NetworkService:
    """
    Generates criminal network graphs from relational FIR data.
    Returns Cytoscape.js / React Flow compatible JSON structures.
    """

    # ------------------------------------------------------------------ #
    #  Graph Builder                                                       #
    # ------------------------------------------------------------------ #

    def _build_graph(self, db: Session, case_ids: List[int] = None) -> nx.Graph:
        """
        Internal method: build a NetworkX graph from the database.

        Nodes:
          - type='case'    → CaseMaster records (FIR nodes)
          - type='accused' → Accused persons (criminal nodes)

        Edges:
          - case ↔ accused  (accused is linked to a case)
          - accused ↔ case  (accused was arrested in a different case, cross-linking)
        """
        G = nx.Graph()

        # Fetch cases — all or filtered
        if case_ids:
            cases = [case_repository.get_with_relations(db, cid) for cid in case_ids]
            cases = [c for c in cases if c is not None]
        else:
            cases = db.query(CaseMaster).limit(500).all()

        for case in cases:
            # Add case node
            G.add_node(
                f"case_{case.id}",
                node_type="case",
                label=case.fir_number,
                district=case.district,
                unit=case.unit_name,
                status=case.status,
            )

            # Add accused nodes and edges
            accused_list = db.query(Accused).filter(Accused.case_id == case.id).all()
            for accused in accused_list:
                node_id = f"accused_{accused.id}"
                if not G.has_node(node_id):
                    G.add_node(
                        node_id,
                        node_type="accused",
                        label=accused.name,
                        status=accused.status,
                        age=accused.age,
                        gender=accused.gender,
                    )
                # Edge: case ↔ accused
                G.add_edge(
                    f"case_{case.id}",
                    node_id,
                    relationship="accused_in_case",
                )

        # Cross-link accused who appear in multiple cases via ArrestSurrender
        arrest_records = db.query(ArrestSurrender).all()
        for arrest in arrest_records:
            case_node = f"case_{arrest.case_id}"
            accused_node = f"accused_{arrest.accused_id}"
            if G.has_node(case_node) and G.has_node(accused_node):
                if not G.has_edge(case_node, accused_node):
                    G.add_edge(
                        case_node,
                        accused_node,
                        relationship="arrested_in_case",
                        arrest_type=arrest.arrest_type,
                    )

        return G

    # ------------------------------------------------------------------ #
    #  Public Methods                                                      #
    # ------------------------------------------------------------------ #

    def get_full_network(self, db: Session) -> Dict[str, Any]:
        """
        Build and return the complete criminal network graph.
        Returns Cytoscape.js compatible JSON with nodes, edges, and metrics.
        """
        G = self._build_graph(db)
        return self._graph_to_cytoscape(G)

    def get_case_network(self, db: Session, case_id: int) -> Dict[str, Any]:
        """
        Build a localised sub-graph centred on a specific case and its
        direct neighbours (accused, related cases via shared accused).
        """
        # Start with the target case
        case = case_repository.get_with_relations(db, case_id)
        if not case:
            raise LookupError(f"Case ID {case_id} not found.")

        # Collect all case IDs that share an accused with this case
        related_case_ids = {case_id}
        for accused in case.accused_list:
            # Find other cases this accused is linked to
            other_cases = (
                db.query(Accused.case_id)
                .filter(Accused.name == accused.name, Accused.case_id != case_id)
                .all()
            )
            for (other_case_id,) in other_cases:
                related_case_ids.add(other_case_id)

        G = self._build_graph(db, case_ids=list(related_case_ids))
        return self._graph_to_cytoscape(G)

    def get_accused_network(self, db: Session, accused_id: int) -> Dict[str, Any]:
        """
        Return all cases and co-accused connected to a specific accused person.
        Useful for understanding a criminal's full activity history.
        """
        accused = accused_repository.get(db, accused_id)
        if not accused:
            raise LookupError(f"Accused ID {accused_id} not found.")

        # Find all cases this person is linked to (by name — cross-case identity)
        linked_cases = (
            db.query(Accused.case_id)
            .filter(Accused.name == accused.name)
            .all()
        )
        case_ids = [cid for (cid,) in linked_cases]
        G = self._build_graph(db, case_ids=case_ids)
        return self._graph_to_cytoscape(G)

    def get_network_metrics(self, db: Session) -> Dict[str, Any]:
        """
        Compute network centrality metrics to identify key criminal nodes.
        Returns:
          - degree_centrality: nodes with the most direct connections
          - betweenness_centrality: nodes acting as bridges
          - most_connected_accused: top 10 accused by degree
        """
        G = self._build_graph(db)

        if G.number_of_nodes() == 0:
            return {"nodes": 0, "edges": 0, "top_accused": [], "top_cases": []}

        degree = nx.degree_centrality(G)
        # betweenness is expensive — skip for very large graphs
        betweenness = (
            nx.betweenness_centrality(G)
            if G.number_of_nodes() < 500
            else {}
        )

        # Separate node types for top-N ranking
        accused_nodes = {
            n: degree[n]
            for n in G.nodes
            if G.nodes[n].get("node_type") == "accused"
        }
        case_nodes = {
            n: degree[n]
            for n in G.nodes
            if G.nodes[n].get("node_type") == "case"
        }

        top_accused = sorted(accused_nodes, key=accused_nodes.get, reverse=True)[:10]
        top_cases = sorted(case_nodes, key=case_nodes.get, reverse=True)[:10]

        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "top_accused": [
                {
                    "node_id": n,
                    "label": G.nodes[n].get("label"),
                    "degree_centrality": round(degree[n], 4),
                    "betweenness_centrality": round(betweenness.get(n, 0), 4),
                }
                for n in top_accused
            ],
            "top_cases": [
                {
                    "node_id": n,
                    "label": G.nodes[n].get("label"),
                    "degree_centrality": round(degree[n], 4),
                }
                for n in top_cases
            ],
        }

    # ------------------------------------------------------------------ #
    #  Serialiser                                                          #
    # ------------------------------------------------------------------ #

    def _graph_to_cytoscape(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Convert a NetworkX graph to Cytoscape.js compatible JSON format.

        Output format:
        {
          "nodes": [ { "data": { "id": ..., "label": ..., ... } }, ... ],
          "edges": [ { "data": { "id": ..., "source": ..., "target": ..., ... } }, ... ],
          "metadata": { "node_count": ..., "edge_count": ... }
        }
        """
        nodes = [
            {"data": {"id": node_id, **attrs}}
            for node_id, attrs in G.nodes(data=True)
        ]
        edges = [
            {
                "data": {
                    "id": f"edge_{u}_{v}",
                    "source": u,
                    "target": v,
                    **attrs,
                }
            }
            for u, v, attrs in G.edges(data=True)
        ]
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges(),
            },
        }


# Singleton service instance
network_service = NetworkService()
