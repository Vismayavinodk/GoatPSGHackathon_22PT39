import os
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from queue import Queue
from threading import Lock

class FleetLogger:
    """
    A thread-safe singleton logger for the Fleet Management System.
    
    This class implements the singleton pattern to ensure only one logger
    instance exists throughout the application. It provides methods for
    logging various system events with appropriate formatting and context.
    
    The logger writes to both a file (fleet_logs.txt) and console output,
    with different formatting for each. It also maintains a queue of recent
    messages for display in the GUI.
    
    Attributes:
        _instance: The single instance of the logger (singleton pattern)
        _lock: Thread-safe lock for singleton creation
    """
    
    _instance: Optional['FleetLogger'] = None
    _lock = Lock()
    
    def __new__(cls):
        """Creates or returns the singleton instance of FleetLogger."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FleetLogger, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """
        Sets up the logging system with file and console handlers.
        
        Creates the logs directory if it doesn't exist and configures
        both file and console logging with appropriate formatting.
        The file handler uses a more detailed format including timestamps
        and thread information, while the console handler uses a simpler
        format for readability.
        """
        # Set up the main logger
        self.logger = logging.getLogger('FleetManagement')
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory in the project root
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.logs_dir = os.path.join(current_dir, 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Configure file handler for detailed logging
        log_file = os.path.join(self.logs_dir, 'fleet_logs.txt')
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Configure console handler for user feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Set up formatters with appropriate detail levels
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        
        # Apply formatters to handlers
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Clear any existing handlers to prevent duplicates
        self.logger.handlers.clear()
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Initialize queue for GUI message display
        self.log_queue = Queue(maxsize=100)
        
        # Log system startup
        self.logger.info("Fleet Management System started")
        self.logger.info("Logging system initialized")
        
    def log_robot_action(self, robot_id: int, action: str, details: str = ""):
        """
        Logs a robot's action with optional context.
        
        Used for recording robot movements, state changes, and other
        significant actions in the system.
        
        Args:
            robot_id: The ID of the robot performing the action
            action: Description of what the robot is doing
            details: Additional context about the action (optional)
        """
        message = f"Robot R{robot_id}: {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
        self._add_to_queue(message)
        
    def log_path_update(self, robot_id: int, path: list, reason: str = ""):
        """
        Logs when a robot's path is updated.
        
        Records changes to a robot's planned path, including the reason
        for the update (e.g., new task, path blocked, etc.).
        
        Args:
            robot_id: The ID of the robot
            path: List of vertex IDs representing the new path
            reason: Explanation for the path update (optional)
        """
        path_str = ' -> '.join(f'L{v}' for v in path)
        message = f"Robot R{robot_id}: New path [{path_str}]"
        if reason:
            message += f" ({reason})"
        self.logger.info(message)
        self._add_to_queue(message)
        
    def log_traffic_event(self, robot_id: int, event_type: str, location: str):
        """
        Logs traffic-related events in the system.
        
        Records events like robots waiting at intersections or being
        blocked by other robots.
        
        Args:
            robot_id: The ID of the robot involved
            event_type: Type of traffic event (waiting, blocked, etc.)
            location: Where the event occurred
        """
        message = f"Robot R{robot_id}: Traffic event - {event_type} at {location}"
        self.logger.info(message)
        self._add_to_queue(message)
        
    def log_task_completion(self, robot_id: int, start_vertex: int, end_vertex: int):
        """
        Logs when a robot completes its assigned task.
        
        Records successful task completion with the path taken from
        start to end vertex.
        
        Args:
            robot_id: The ID of the robot completing the task
            start_vertex: Starting vertex ID
            end_vertex: Ending vertex ID
        """
        message = f"Robot R{robot_id}: Task completed - Path: L{start_vertex} -> L{end_vertex}"
        self.logger.info(message)
        self._add_to_queue(message)
        
    def log_error(self, error_msg: str):
        """
        Logs system errors with full stack trace.
        
        Used for recording system errors and exceptions with detailed
        debugging information.
        
        Args:
            error_msg: The error message to log
        """
        self.logger.error(error_msg, exc_info=True)
        self._add_to_queue(f"ERROR: {error_msg}")
        
    def log_warning(self, warning_msg: str):
        """
        Logs system warnings.
        
        Used for recording non-critical issues that might need attention.
        
        Args:
            warning_msg: The warning message to log
        """
        self.logger.warning(warning_msg)
        self._add_to_queue(f"WARNING: {warning_msg}")
        
    def _add_to_queue(self, message: str):
        """
        Adds a message to the GUI display queue.
        
        Maintains a queue of recent messages for display in the GUI,
        with timestamps for each message. If the queue is full, the
        oldest message is removed.
        
        Args:
            message: The message to add to the queue
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        if self.log_queue.full():
            try:
                self.log_queue.get_nowait()
            except:
                pass
        try:
            self.log_queue.put_nowait((timestamp, message))
        except:
            pass
        
    def get_recent_logs(self, count: int = 10) -> List[Tuple[str, str]]:
        """
        Retrieves recent log messages for GUI display.
        
        Returns the most recent log messages with their timestamps,
        limited to the specified count.
        
        Args:
            count: Number of recent messages to retrieve (default: 10)
            
        Returns:
            List of (timestamp, message) tuples
        """
        return list(self.log_queue.queue)[-count:] 