from typing import List, Tuple
import math

def calculate_distance(point1: Tuple[float, float], 
                      point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.sqrt((point1[0] - point2[0])**2 + 
                    (point1[1] - point2[1])**2)

def interpolate_position(start: Tuple[float, float],
                        end: Tuple[float, float],
                        progress: float) -> Tuple[float, float]:
    """Interpolate between two positions based on progress (0-1)"""
    x = start[0] + (end[0] - start[0]) * progress
    y = start[1] + (end[1] - start[1]) * progress
    return (x, y)

def is_point_in_circle(point: Tuple[float, float],
                      center: Tuple[float, float],
                      radius: float) -> bool:
    """Check if a point is inside a circle"""
    return calculate_distance(point, center) <= radius

def get_angle_between_points(point1: Tuple[float, float],
                           point2: Tuple[float, float]) -> float:
    """Calculate angle between two points in radians"""
    return math.atan2(point2[1] - point1[1],
                     point2[0] - point1[0]) 