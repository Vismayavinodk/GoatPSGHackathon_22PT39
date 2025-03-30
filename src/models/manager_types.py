from typing import Protocol, Dict, Optional
from .robot import Robot

class IFleetManager(Protocol):
    """Interface for FleetManager to avoid circular imports"""
    @property
    def robots(self) -> Dict[int, Robot]:
        ...

class ITrafficManager(Protocol):
    """Interface for TrafficManager to avoid circular imports"""
    def is_robot_blocked(self, robot_id: int) -> bool:
        ...
    def update_robot_position(self, robot: Robot, next_vertex: int) -> None:
        ...
    def is_lane_occupied(self, edge: tuple[int, int]) -> bool:
        ...
    def is_intersection_occupied(self, vertex: int) -> bool:
        ... 