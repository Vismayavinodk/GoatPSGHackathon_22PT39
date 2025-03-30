"""
Navigation graph model for the Fleet Management System.
Handles the network of vertices and edges.
"""

import networkx as nx
from typing import Dict, List, Tuple, Union
import json
import os

class NavigationGraph:
    def __init__(self, graph_data: Union[str, Dict]):
        """
        Initialize the navigation graph.
        
        Args:
            graph_data: Either a path to a JSON file or a dictionary containing graph data
        """
        self.graph = nx.Graph()
        self.vertex_positions: Dict[int, Tuple[float, float]] = {}
        
        if isinstance(graph_data, str):
            self.load_graph(graph_data)
        else:
            self.load_data(graph_data)
            
    def load_graph(self, graph_file: str) -> None:
        """Load graph data from a JSON file"""
        with open(graph_file, 'r') as f:
            data = json.load(f)
        self.load_data(data)
            
    def load_data(self, data: Dict) -> None:
        """Load graph data from a dictionary"""
        # Get the first level's data
        level_data = data['levels']['l1']
        
        # Load vertices and their positions
        for i, vertex_data in enumerate(level_data['vertices']):
            x, y = vertex_data[0], vertex_data[1]
            self.graph.add_node(i)
            self.vertex_positions[i] = (x, y)
            
        # Load edges
        for edge in level_data['lanes']:
            v1, v2 = edge[0], edge[1]
            self.graph.add_edge(v1, v2)
            
    def get_vertex_position(self, vertex: int) -> Tuple[float, float]:
        """Get the position of a vertex"""
        return self.vertex_positions.get(vertex, (0, 0))
        
    def get_neighbors(self, vertex: int) -> List[int]:
        """Get all neighbors of a vertex"""
        return list(self.graph.neighbors(vertex))
        
    def get_shortest_path(self, start: int, end: int) -> List[int]:
        """Get the shortest path between two vertices"""
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            return []
            
    def is_valid_vertex(self, vertex: int) -> bool:
        """Check if a vertex exists in the graph"""
        return vertex in self.graph.nodes()

    def get_path_length(self, path: List[int]) -> float:
        """Calculate total length of a path"""
        return nx.path_weight(self.graph, path, 'weight') 