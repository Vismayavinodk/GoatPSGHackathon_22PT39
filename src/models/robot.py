from typing import List, Tuple, Optional
from enum import Enum

class RobotStatus(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    TASK_COMPLETED = "TASK_COMPLETED"
    ERROR = "ERROR"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"

class Robot:
    def __init__(self, robot_id: int, start_vertex: int):
        self.id = robot_id
        self.current_vertex = start_vertex
        self.target_vertex: Optional[int] = None
        self.path: List[int] = []
        self.status = RobotStatus.IDLE
        self.speed = 0.8  # Reduced speed for smoother movement
        self.progress = 0.0  # progress along current path segment
        
    def set_target(self, target_vertex: int) -> None:
        """Set new target vertex for the robot"""
        self.target_vertex = target_vertex
        self.status = RobotStatus.MOVING
        
    def set_path(self, path: List[int]) -> None:
        """Set the path to follow"""
        self.path = path
        self.progress = 0.0
        
    def cancel_task(self) -> None:
        """Cancel the current task and stop the robot"""
        self.target_vertex = None
        self.path = []
        self.progress = 0.0
        self.status = RobotStatus.IDLE
        
    def update_position(self, delta_time: float, traffic_manager=None) -> None:
        """Update robot position based on time elapsed"""
        if self.status != RobotStatus.MOVING and self.status != RobotStatus.WAITING:
            return
            
        if not self.path:
            self.status = RobotStatus.IDLE
            return
            
        # Check if path is blocked by traffic
        if traffic_manager:
            next_vertex = self.path[0]
            if traffic_manager.is_robot_blocked(self.id):
                self.status = RobotStatus.BLOCKED
                return
            elif traffic_manager.is_robot_waiting(self.id):
                self.status = RobotStatus.WAITING
                return
            else:
                if self.status in [RobotStatus.WAITING, RobotStatus.BLOCKED]:
                    self.status = RobotStatus.MOVING
            
        # Update progress along current path segment
        self.progress += self.speed * delta_time
        
        # Check if reached next vertex
        if self.progress >= 1.0:
            self.progress = 0.0
            old_vertex = self.current_vertex
            self.current_vertex = self.path.pop(0)
            
            # Update traffic manager
            if traffic_manager:
                traffic_manager.update_robot_position(self, self.current_vertex)
            
            # Check if reached final destination
            if not self.path:
                self.status = RobotStatus.TASK_COMPLETED
                self.target_vertex = None
                
    def get_current_position(self, nav_graph) -> Tuple[float, float]:
        """Get current position of the robot"""
        if not self.path:
            return nav_graph.get_vertex_position(self.current_vertex)
            
        # Interpolate between current and next vertex
        current_pos = nav_graph.get_vertex_position(self.current_vertex)
        next_pos = nav_graph.get_vertex_position(self.path[0])
        
        x = current_pos[0] + (next_pos[0] - current_pos[0]) * self.progress
        y = current_pos[1] + (next_pos[1] - current_pos[1]) * self.progress
        
        return (x, y) 