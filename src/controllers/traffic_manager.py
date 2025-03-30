from typing import List, Dict, Set, Tuple, Optional
from ..models.robot import Robot
from ..models.nav_graph import NavigationGraph
from ..models.manager_types import IFleetManager

class TrafficManager:
    def __init__(self, nav_graph: NavigationGraph):
        self.nav_graph = nav_graph
        self.edge_occupancy: Dict[Tuple[int, int], Set[int]] = {}
        self.intersection_occupancy: Dict[int, Set[int]] = {}
        self.fleet_manager: Optional[IFleetManager] = None
        
    def set_fleet_manager(self, fleet_manager: IFleetManager) -> None:
        """Set the fleet manager reference"""
        self.fleet_manager = fleet_manager
        
    def initialize_edge(self, edge: Tuple[int, int]) -> None:
        """Initialize an edge in the traffic management system"""
        if edge not in self.edge_occupancy:
            self.edge_occupancy[edge] = set()
            
    def get_edge(self, from_vertex: int, to_vertex: int) -> Tuple[int, int]:
        """Get canonical edge representation"""
        return tuple(sorted([from_vertex, to_vertex]))
        
    def is_lane_occupied(self, edge: Tuple[int, int]) -> bool:
        """Check if a lane is currently occupied by any robot"""
        edge = self.get_edge(edge[0], edge[1])
        occupants = self.edge_occupancy.get(edge, set())
        return len(occupants) > 0
        
    def is_intersection_occupied(self, vertex: int) -> bool:
        """Check if an intersection is currently occupied"""
        # Only consider it an intersection if it has more than 2 neighbors
        if len(self.nav_graph.get_neighbors(vertex)) <= 2:
            return False
        return len(self.intersection_occupancy.get(vertex, set())) > 0
        
    def is_robot_blocked(self, robot_id: int) -> bool:
        """Check if a robot is blocked by traffic"""
        if not self.fleet_manager:
            return False
            
        robot = self.fleet_manager.robots.get(robot_id)
        if not robot or not robot.path:
            return False
            
        next_vertex = robot.path[0]
        current_vertex = robot.current_vertex
        
        # Check if current intersection is blocked (if we're at an intersection)
        if len(self.nav_graph.get_neighbors(current_vertex)) > 2:
            current_intersection_occupants = self.intersection_occupancy.get(current_vertex, set())
            if len(current_intersection_occupants - {robot_id}) > 0:
                return True
        
        # Check if next intersection is blocked
        if len(self.nav_graph.get_neighbors(next_vertex)) > 2:
            next_intersection_occupants = self.intersection_occupancy.get(next_vertex, set())
            if len(next_intersection_occupants - {robot_id}) > 0:
                return True
        
        # Check if the next edge is occupied
        edge = self.get_edge(current_vertex, next_vertex)
        edge_occupants = self.edge_occupancy.get(edge, set())
        other_robots = edge_occupants - {robot_id}
        if other_robots:
            return True
            
        return False
        
    def is_robot_waiting(self, robot_id: int) -> bool:
        """Check if a robot is waiting for traffic to clear"""
        if not self.fleet_manager:
            return False
            
        robot = self.fleet_manager.robots.get(robot_id)
        if not robot or not robot.path:
            return False
            
        next_vertex = robot.path[0]
        current_vertex = robot.current_vertex
        
        # Only wait at intersections (vertices with more than 2 neighbors)
        if len(self.nav_graph.get_neighbors(next_vertex)) <= 2:
            return False
            
        # Check if next intersection is occupied by another robot
        next_intersection_occupants = self.intersection_occupancy.get(next_vertex, set())
        if len(next_intersection_occupants - {robot_id}) > 0:
            return True
            
        return False
        
    def update_robot_position(self, robot: Robot, next_vertex: int) -> None:
        """Update traffic management system with new robot position"""
        if not robot.path:
            return
            
        current_vertex = robot.current_vertex
        
        # Remove robot from previous edge
        if current_vertex != next_vertex:
            prev_edge = self.get_edge(current_vertex, robot.path[0])
            if prev_edge in self.edge_occupancy:
                self.edge_occupancy[prev_edge].discard(robot.id)
                
            # Remove from previous intersection if it was one
            if len(self.nav_graph.get_neighbors(current_vertex)) > 2:
                if current_vertex in self.intersection_occupancy:
                    self.intersection_occupancy[current_vertex].discard(robot.id)
                
        # Add robot to new edge
        new_edge = self.get_edge(current_vertex, next_vertex)
        if new_edge not in self.edge_occupancy:
            self.initialize_edge(new_edge)
        self.edge_occupancy[new_edge].add(robot.id)
        
        # Update intersection occupancy
        if len(self.nav_graph.get_neighbors(next_vertex)) > 2:  
            if next_vertex not in self.intersection_occupancy:
                self.intersection_occupancy[next_vertex] = set()
            # Only add to intersection occupancy if robot has reached the intersection
            if current_vertex == next_vertex:
                self.intersection_occupancy[next_vertex].add(robot.id)
                
    def clear_robot_occupancy(self, robot_id: int) -> None:
        """Clear all occupancy records for a robot"""
        # Clear from all edges
        for edge in self.edge_occupancy:
            self.edge_occupancy[edge].discard(robot_id)
            
        # Clear from all intersections
        for vertex in self.intersection_occupancy:
            self.intersection_occupancy[vertex].discard(robot_id)
            
    def get_edge_occupancy(self, edge: Tuple[int, int]) -> Set[int]:
        """Get set of robot IDs currently on an edge"""
        return self.edge_occupancy.get(edge, set())
        
    def clear_edge(self, edge: Tuple[int, int]) -> None:
        """Clear all robots from an edge"""
        if edge in self.edge_occupancy:
            self.edge_occupancy[edge].clear() 