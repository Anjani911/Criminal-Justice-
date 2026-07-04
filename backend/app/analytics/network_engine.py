"""
Criminal network engine.

Builds explicit graph structures for the relationship chain:
Case -> Accused -> Arrest -> Case

The output is JSON-ready and compatible with Cytoscape.js and React Flow
consumers. This module performs the graph assembly only and contains no API
or authentication concerns.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx
from sqlalchemy.orm import Session

from app.models.arrest import ArrestSurrender
from app.models.case import CaseMaster
from app.models.people import Accused


class NetworkEngine:
    """
    Builds criminal graph structures from existing FIR database records.
    """

    def build_full_graph(self, db: Session, case_ids: Optional[Iterable[int]] = None) -> nx.DiGraph:
        graph = nx.DiGraph()
        cases = self._load_cases(db, case_ids=case_ids)
        self._add_case_accused_arrest_chain(graph, db, cases)
        return graph

    def build_case_graph(self, db: Session, case_id: int) -> nx.DiGraph:
        case = db.query(CaseMaster).filter(CaseMaster.id == case_id).first()
        if case is None:
            raise LookupError(f"Case ID {case_id} not found.")

        related_case_ids: Set[int] = {case_id}
        accused_names = [accused.name for accused in case.accused_list]
        if accused_names:
            rows = (
                db.query(Accused.case_id)
                .filter(Accused.name.in_(accused_names))
                .all()
            )
            related_case_ids.update(case_id for (case_id,) in rows)

        return self.build_full_graph(db, case_ids=related_case_ids)

    def build_accused_graph(self, db: Session, accused_id: int) -> nx.DiGraph:
        accused = db.query(Accused).filter(Accused.id == accused_id).first()
        if accused is None:
            raise LookupError(f"Accused ID {accused_id} not found.")

        linked_case_ids: Set[int] = {accused.case_id}
        rows = (
            db.query(Accused.case_id)
            .filter(Accused.name == accused.name)
            .all()
        )
        linked_case_ids.update(case_id for (case_id,) in rows)
        return self.build_full_graph(db, case_ids=linked_case_ids)

    def graph_metrics(self, db: Session) -> Dict[str, Any]:
        graph = self.build_full_graph(db)

        if graph.number_of_nodes() == 0:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "top_cases": [],
                "top_accused": [],
                "top_arrests": [],
            }

        degree = nx.degree_centrality(graph)
        betweenness = nx.betweenness_centrality(graph) if graph.number_of_nodes() <= 500 else {}

        top_cases = self._top_nodes(graph, degree, node_type="case")
        top_accused = self._top_nodes(graph, degree, node_type="accused")
        top_arrests = self._top_nodes(graph, degree, node_type="arrest")

        return {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "top_cases": self._format_ranked_nodes(graph, top_cases, degree, betweenness),
            "top_accused": self._format_ranked_nodes(graph, top_accused, degree, betweenness),
            "top_arrests": self._format_ranked_nodes(graph, top_arrests, degree, betweenness),
        }

    def to_cytoscape(self, graph: nx.DiGraph) -> Dict[str, Any]:
        nodes = []
        for node_id, attrs in graph.nodes(data=True):
            nodes.append({"data": {"id": node_id, **attrs}})

        edges = []
        for source, target, attrs in graph.edges(data=True):
            edge_id = attrs.get("edge_id") or f"edge_{source}_{target}"
            payload = {k: v for k, v in attrs.items() if k != "edge_id"}
            edges.append({"data": {"id": edge_id, "source": source, "target": target, **payload}})

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
                "node_types": self._node_type_counts(graph),
            },
        }

    def build_full_payload(self, db: Session, case_ids: Optional[Iterable[int]] = None) -> Dict[str, Any]:
        return self.to_cytoscape(self.build_full_graph(db, case_ids=case_ids))

    def build_case_payload(self, db: Session, case_id: int) -> Dict[str, Any]:
        return self.to_cytoscape(self.build_case_graph(db, case_id))

    def build_accused_payload(self, db: Session, accused_id: int) -> Dict[str, Any]:
        return self.to_cytoscape(self.build_accused_graph(db, accused_id))

    def _load_cases(self, db: Session, case_ids: Optional[Iterable[int]] = None) -> List[CaseMaster]:
        query = db.query(CaseMaster)
        if case_ids is not None:
            case_id_list = list(dict.fromkeys(case_ids))
            if not case_id_list:
                return []
            query = query.filter(CaseMaster.id.in_(case_id_list))
        return query.limit(1000).all()

    def _add_case_accused_arrest_chain(self, graph: nx.DiGraph, db: Session, cases: List[CaseMaster]) -> None:
        for case in cases:
            case_node_id = f"case_{case.id}"
            graph.add_node(
                case_node_id,
                node_type="case",
                label=case.fir_number,
                case_id=case.id,
                status=case.status,
                district=case.district,
                unit=case.unit_name,
            )

            accused_rows = (
                db.query(Accused)
                .filter(Accused.case_id == case.id)
                .all()
            )

            for accused in accused_rows:
                accused_node_id = f"accused_{accused.id}"
                graph.add_node(
                    accused_node_id,
                    node_type="accused",
                    label=accused.name,
                    accused_id=accused.id,
                    case_id=accused.case_id,
                    status=accused.status,
                    age=accused.age,
                    gender=accused.gender,
                )
                graph.add_edge(
                    case_node_id,
                    accused_node_id,
                    relationship="case_to_accused",
                    edge_id=f"edge_{case_node_id}_{accused_node_id}",
                )

                arrest_rows = (
                    db.query(ArrestSurrender)
                    .filter(ArrestSurrender.accused_id == accused.id)
                    .all()
                )

                for arrest in arrest_rows:
                    arrest_node_id = f"arrest_{arrest.id}"
                    graph.add_node(
                        arrest_node_id,
                        node_type="arrest",
                        label=arrest.arrest_type,
                        arrest_id=arrest.id,
                        arrest_date=arrest.arrest_date.isoformat() if arrest.arrest_date else None,
                        case_id=arrest.case_id,
                        accused_id=arrest.accused_id,
                        court_name=arrest.court_name,
                    )
                    graph.add_edge(
                        accused_node_id,
                        arrest_node_id,
                        relationship="accused_to_arrest",
                        edge_id=f"edge_{accused_node_id}_{arrest_node_id}",
                    )

                    arrest_case_node_id = f"case_{arrest.case_id}"
                    if not graph.has_node(arrest_case_node_id):
                        graph.add_node(
                            arrest_case_node_id,
                            node_type="case",
                            label=f"FIR {arrest.case_id}",
                            case_id=arrest.case_id,
                        )
                    graph.add_edge(
                        arrest_node_id,
                        arrest_case_node_id,
                        relationship="arrest_to_case",
                        arrest_type=arrest.arrest_type,
                        edge_id=f"edge_{arrest_node_id}_{arrest_case_node_id}",
                    )

    def _node_type_counts(self, graph: nx.DiGraph) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get("node_type", "unknown")
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts

    def _top_nodes(self, graph: nx.DiGraph, degree: Dict[str, float], node_type: str) -> List[str]:
        nodes = [node_id for node_id, attrs in graph.nodes(data=True) if attrs.get("node_type") == node_type]
        return sorted(nodes, key=lambda node_id: degree.get(node_id, 0), reverse=True)[:10]

    def _format_ranked_nodes(
        self,
        graph: nx.DiGraph,
        node_ids: List[str],
        degree: Dict[str, float],
        betweenness: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        formatted = []
        for node_id in node_ids:
            attrs = graph.nodes[node_id]
            formatted.append(
                {
                    "node_id": node_id,
                    "label": attrs.get("label"),
                    "node_type": attrs.get("node_type"),
                    "degree_centrality": round(degree.get(node_id, 0), 4),
                    "betweenness_centrality": round(betweenness.get(node_id, 0), 4),
                }
            )
        return formatted


network_engine = NetworkEngine()
