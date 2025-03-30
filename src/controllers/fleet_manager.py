from typing import List, Dict, Optional
from ..models.robot import Robot, RobotStatus
from ..models.nav_graph import NavigationGraph
from ..models.manager_types import ITrafficManager
from ..utils.logger import FleetLogger

class FleetManager:
    def __init__(self, nav_graph: NavigationGraph):
        self.nav_graph = nav_graph
        self.robots: Dict[int, Robot] = {}
        self.next_robot_id = 0
        self.traffic_manager: Optional[ITrafficManager] = None
        self.logger = FleetLogger()
        
    def set_traffic_manager(self, traffic_manager: ITrafficManager) -> None:
        """Set the traffic manager reference"""
        self.traffic_manager = traffic_manager
        
    def add_robot(self, start_vertex: int) -> Robot:
        """Add a new robot to the fleet"""
        robot = Robot(self.next_robot_id, start_vertex)
        self.robots[self.next_robot_id] = robot
        self.logger.log_robot_action(
            robot.id,
            "Created",
            f"at vertex L{start_vertex}"
        )
        self.next_robot_id += 1
        return robot
        
    def remove_robot(self, robot_id: int) -> None:
        """Remove a robot from the fleet"""
        if robot_id in self.robots:
            robot = self.robots[robot_id]
            current_vertex = robot.current_vertex
            # Cancel any ongoing task
            robot.cancel_task()
            # Remove from traffic management
            if self.traffic_manager:
                if robot.path and len(robot.path) > 0:
                    next_vertex = robot.path[0]
                    edge = self.traffic_manager.get_edge(current_vertex, next_vertex)
                    self.traffic_manager.clear_edge(edge)
            # Log removal
            self.logger.log_robot_action(
                robot_id,
                "Removed",
                f"from vertex L{current_vertex}"
            )
            # Remove from fleet
            del self.robots[robot_id]
            
    def assign_task(self, robot_id: int, target_vertex: int) -> bool:
        """Assign a new task to a robot"""
        if robot_id not in self.robots:
            self.logger.log_error(f"Failed to assign task: Robot R{robot_id} not found")
            return False
            
        robot = self.robots[robot_id]
        # Allow reassignment if robot is IDLE, MOVING, or TASK_COMPLETED
        if robot.status == RobotStatus.ERROR:
            self.logger.log_error(f"Failed to assign task: Robot R{robot_id} is in ERROR state")
            return False
            
        # Calculate path to target
        path = self.nav_graph.get_shortest_path(robot.current_vertex, target_vertex)
        if not path:
            self.logger.log_error(
                f"Failed to assign task: No valid path from L{robot.current_vertex} to L{target_vertex}"
            )
            return False
            
        # If robot is currently moving, update traffic management
        if robot.status in [RobotStatus.MOVING, RobotStatus.WAITING, RobotStatus.BLOCKED]:
            if self.traffic_manager and robot.path and len(robot.path) > 0:
                next_vertex = robot.path[0]
                edge = self.traffic_manager.get_edge(robot.current_vertex, next_vertex)
                self.traffic_manager.clear_edge(edge)
                self.logger.log_path_update(
                    robot_id, path,
                    "Task reassigned"
                )
        else:
            self.logger.log_path_update(
                robot_id, path,
                "New task assigned"
            )
            
        robot.set_target(target_vertex)
        robot.set_path(path)
        return True
        
    def cancel_task(self, robot_id: int) -> bool:
        """Cancel the current task of a robot"""
        if robot_id not in self.robots:
            self.logger.log_error(f"Failed to cancel task: Robot R{robot_id} not found")
            return False
            
        robot = self.robots[robot_id]
        if robot.status == RobotStatus.IDLE:
            self.logger.log_warning(f"Robot R{robot_id} has no active task to cancel")
            return False
            
        # Clear traffic management
        if self.traffic_manager and robot.path and len(robot.path) > 0:
            next_vertex = robot.path[0]
            edge = self.traffic_manager.get_edge(robot.current_vertex, next_vertex)
            self.traffic_manager.clear_edge(edge)
            
        self.logger.log_robot_action(
            robot_id,
            "Task cancelled",
            f"at vertex L{robot.current_vertex}"
        )
        robot.cancel_task()
        return True
        
    def update_fleet(self, delta_time: float) -> None:
        """Update all robots in the fleet"""
        for robot in self.robots.values():
            prev_status = robot.status
            prev_vertex = robot.current_vertex
            
            robot.update_position(delta_time, self.traffic_manager)
            
            # Log status changes
            if robot.status != prev_status:
                if robot.status == RobotStatus.WAITING:
                    self.logger.log_traffic_event(
                        robot.id,
                        "Waiting",
                        f"intersection L{robot.path[0]}"
                    )
                elif robot.status == RobotStatus.BLOCKED:
                    self.logger.log_traffic_event(
                        robot.id,
                        "Blocked",
                        f"path L{robot.current_vertex}-L{robot.path[0]}"
                    )
                elif robot.status == RobotStatus.TASK_COMPLETED:
                    self.logger.log_task_completion(
                        robot.id,
                        prev_vertex,
                        robot.current_vertex
                    )
                elif prev_status in [RobotStatus.WAITING, RobotStatus.BLOCKED]:
                    self.logger.log_robot_action(
                        robot.id,
                        "Resumed movement",
                        f"from L{robot.current_vertex}"
                    )
            
    def get_robot_status(self, robot_id: int) -> Optional[RobotStatus]:
        """Get current status of a robot"""
        if robot_id not in self.robots:
            return None
        return self.robots[robot_id].status
        
    def get_robot_position(self, robot_id: int) -> Optional[tuple]:
        """Get current position of a robot"""
        if robot_id not in self.robots:
            return None
        return self.robots[robot_id].get_current_position(self.nav_graph)
        
    def get_robot_path(self, robot_id: int) -> Optional[List[int]]:
        """Get the current path of a robot"""
        if robot_id not in self.robots:
            return None
        return [self.robots[robot_id].current_vertex] + self.robots[robot_id].path if self.robots[robot_id].path else None 