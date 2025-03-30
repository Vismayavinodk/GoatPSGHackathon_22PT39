import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from .models.nav_graph import NavigationGraph
from .controllers.fleet_manager import FleetManager
from .controllers.traffic_manager import TrafficManager
from .gui.fleet_gui import FleetGUI

def load_navigation_graph(file_path: str) -> NavigationGraph:
    """Load navigation graph from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return NavigationGraph(data)
    except FileNotFoundError:
        print(f"Error: Navigation graph file not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in navigation graph file {file_path}")
        sys.exit(1)

def main():
    """Main entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Get the absolute path to the nav_graph.json file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    nav_graph_path = os.path.join(data_dir, 'nav_graph_1.json')
    
    # Load navigation graph
    nav_graph = load_navigation_graph(nav_graph_path)
    
    # Initialize managers
    fleet_manager = FleetManager(nav_graph)
    traffic_manager = TrafficManager(nav_graph)
    traffic_manager.set_fleet_manager(fleet_manager)
    fleet_manager.set_traffic_manager(traffic_manager)
    
    # Create and show GUI
    gui = FleetGUI(nav_graph, fleet_manager, traffic_manager)
    gui.show()
    
    # Create simulation timer (60 FPS)
    sim_timer = QTimer()
    sim_timer.timeout.connect(lambda: fleet_manager.update_fleet(1/60))  # 16.67ms update interval
    sim_timer.start(16)  # 60 FPS
    
    # Create GUI update timer (60 FPS)
    gui_timer = QTimer()
    gui_timer.timeout.connect(lambda: gui.update_display())
    gui_timer.start(16)  # 60 FPS
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 