"""
PyQt-based GUI for the Fleet Management System.
Provides a modern, professional interface with better styling and components.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame, QScrollArea, QGraphicsView,
                            QGraphicsScene, QGraphicsItem, QStatusBar, QGraphicsEllipseItem)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QLinearGradient
from typing import Dict, List, Tuple, Optional
from ..models.robot import RobotStatus
import math

class NetworkView(QGraphicsView):
    """Custom view for displaying the navigation network"""
    
    def __init__(self, fleet_gui):
        super().__init__(fleet_gui)
        self.fleet_gui = fleet_gui
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Colors
        self.BACKGROUND_COLOR = QColor("#2B2B2B")
        self.VERTEX_COLOR = QColor("#FFFFFF")
        self.EDGE_COLOR = QColor("#4A4A4A")
        self.ROBOT_COLORS = {
            "R0": QColor("#FF6B6B"),
            "R1": QColor("#4ECDC4"),
            "R2": QColor("#45B7D1"),
            "R3": QColor("#96CEB4"),
            "R4": QColor("#FFEEAD"),
            "R5": QColor("#D4A5A5")
        }
        self.STATUS_COLORS = {
            "IDLE": QColor("#90EE90"),
            "MOVING": QColor("#87CEEB"),
            "WAITING": QColor("#FFD700"),
            "BLOCKED": QColor("#FF69B4"),
            "CHARGING": QColor("#32CD32"),
            "COMPLETE": QColor("#808080")
        }
        
        # Add glow effect colors
        self.GLOW_COLOR = QColor("#FFFFFF")
        self.TRAIL_COLOR = QColor(255, 255, 255, 50)  # Semi-transparent white
        
        # Set background
        self.setBackgroundBrush(QBrush(self.BACKGROUND_COLOR))
        
        # State
        self.selected_robot = None
        self.hovered_vertex = None
        self.vertex_items = {}  # Store vertex items for interaction
        self.robot_items = {}   # Store robot items for interaction
        
    def draw_network(self, nav_graph, robots, traffic_manager):
        """Draw the navigation network with robots"""
        self.scene.clear()
        self.vertex_items.clear()
        self.robot_items.clear()
        
        # Calculate scale factors
        min_x = min(pos[0] for pos in nav_graph.vertex_positions.values())
        max_x = max(pos[0] for pos in nav_graph.vertex_positions.values())
        min_y = min(pos[1] for pos in nav_graph.vertex_positions.values())
        max_y = max(pos[1] for pos in nav_graph.vertex_positions.values())
        
        width = max_x - min_x
        height = max_y - min_y
        
        scale_x = (self.width() - 150) / width if width > 0 else 1  # Increased margin
        scale_y = (self.height() - 150) / height if height > 0 else 1  # Increased margin
        scale = min(scale_x, scale_y)
        
        # Draw edges
        for edge in nav_graph.graph.edges():
            start_pos = nav_graph.get_vertex_position(edge[0])
            end_pos = nav_graph.get_vertex_position(edge[1])
            
            # Scale positions
            start_x = (start_pos[0] - min_x) * scale + 75  # Increased offset
            start_y = (start_pos[1] - min_y) * scale + 75  # Increased offset
            end_x = (end_pos[0] - min_x) * scale + 75  # Increased offset
            end_y = (end_pos[1] - min_y) * scale + 75  # Increased offset
            
            # Check if edge is occupied
            edge_occupants = traffic_manager.get_edge_occupancy(tuple(sorted(edge)))
            if edge_occupants:
                pen = QPen(QColor("#00BFFF"), 3)  # Deep sky blue for occupied edges
            else:
                pen = QPen(self.EDGE_COLOR, 2)
            
            line = self.scene.addLine(start_x, start_y, end_x, end_y, pen)
            line.setZValue(1)
            
            # Draw edge label with background
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Add white background for edge label with larger size
            label_bg = self.scene.addRect(mid_x - 25, mid_y - 12, 50, 24,
                                        QPen(Qt.PenStyle.NoPen),
                                        QBrush(QColor(43, 43, 43, 200)))
            label_bg.setZValue(1.1)
            
            label = self.scene.addText(f"L{edge[0]}-L{edge[1]}")
            label.setDefaultTextColor(QColor("#FFFFFF"))  # Brighter color
            label.setFont(QFont("Arial", 9))  # Slightly larger font
            label.setPos(mid_x - 25, mid_y - 12)
            label.setZValue(1.2)
        
        # Draw vertices
        for vertex in nav_graph.graph.nodes():
            pos = nav_graph.get_vertex_position(vertex)
            x = (pos[0] - min_x) * scale + 75  # Increased offset
            y = (pos[1] - min_y) * scale + 75  # Increased offset
            
            # Draw vertex circle
            vertex_item = self.scene.addEllipse(x - 15, y - 15,
                                              30, 30, QPen(self.VERTEX_COLOR),
                                              QBrush(self.VERTEX_COLOR))
            vertex_item.setZValue(2)
            self.vertex_items[vertex] = vertex_item
            
            # Draw vertex label with background
            label_bg = self.scene.addRect(x - 40, y + 20, 35, 24,  # Adjusted position
                                        QPen(Qt.PenStyle.NoPen),
                                        QBrush(QColor(43, 43, 43, 200)))
            label_bg.setZValue(2.1)
            
            label = self.scene.addText(f"L{vertex}")
            label.setDefaultTextColor(QColor("#FFFFFF"))  # Brighter color
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setPos(x - 40, y + 20)  # Adjusted position
            label.setZValue(2.2)
            
            # Draw intersection indicator if needed
            if len(nav_graph.get_neighbors(vertex)) > 2:
                if traffic_manager.is_intersection_occupied(vertex):
                    # Draw intersection ring
                    ring = self.scene.addEllipse(x - 20, y - 20,
                                               40, 40, QPen(QColor("#FFD700"), 2))
                    ring.setZValue(1.5)
                    
                    # Draw highlight
                    highlight = self.scene.addEllipse(x - 22, y - 22,
                                                    44, 44, QPen(QColor("#FFA500"), 1))
                    highlight.setZValue(1.4)
            
            # Draw hover effect
            if vertex == self.hovered_vertex:
                hover = self.scene.addEllipse(x - 17, y - 17,
                                            34, 34, QPen(QColor("#FFFFFF"), 2))
                hover.setZValue(1.9)
        
        # Draw robots
        for robot_id, robot in robots.items():
            pos = nav_graph.get_vertex_position(robot.current_vertex)
            x = (pos[0] - min_x) * scale + 75  # Increased offset
            y = (pos[1] - min_y) * scale + 75  # Increased offset
            
            # Draw robot circle
            robot_color = self.ROBOT_COLORS.get(f"R{robot_id}", QColor("#FF0000"))
            robot_item = self.scene.addEllipse(x - 12, y - 12,
                                             24, 24, QPen(robot_color),
                                              QBrush(robot_color))
            robot_item.setZValue(4)
            self.robot_items[robot_id] = robot_item
            
            # Draw status indicator
            status_str = str(robot.status).split('.')[-1]  # Convert enum to string
            status_color = self.STATUS_COLORS.get(status_str, QColor("#FFFFFF"))
            status_item = self.scene.addEllipse(x - 6, y - 6,
                                              12, 12, QPen(QColor("#FFFFFF")),
                                              QBrush(status_color))
            status_item.setZValue(5)
            
            # Draw robot label with background
            label_bg = self.scene.addRect(x + 20, y - 20, 35, 24,  # Adjusted position and size
                                        QPen(Qt.PenStyle.NoPen),
                                        QBrush(QColor(43, 43, 43, 200)))
            label_bg.setZValue(5.1)
            
            label = self.scene.addText(f"R{robot_id}")
            label.setDefaultTextColor(QColor("#FFFFFF"))  # Brighter color
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setPos(x + 20, y - 20)  # Adjusted position
            label.setZValue(5.2)
            
            # Draw selection indicator if selected
            if robot_id == self.selected_robot:
                select_ring = self.scene.addEllipse(x - 14, y - 14,
                                                  28, 28, QPen(QColor("#FFFFFF"), 2))
                select_ring.setZValue(3.5)
            
            # Draw status text with background
            status_bg = self.scene.addRect(x - 40, y + 20, 80, 24,  # Wider background
                                         QPen(Qt.PenStyle.NoPen),
                                         QBrush(QColor(43, 43, 43, 200)))
            status_bg.setZValue(5.3)
            
            status_text = status_str
            if robot.path:
                status_text += f" → L{robot.path[0]}"
            
            status_label = self.scene.addText(status_text)
            status_label.setDefaultTextColor(QColor("#FFFFFF"))  # Brighter color
            status_label.setFont(QFont("Arial", 9))
            status_label.setPos(x - 40, y + 20)
            status_label.setZValue(5.4)
            
            # Draw path if exists
            if robot.path:
                path_color = robot_color.lighter(150)  # Lighter version of robot color
                for i in range(len(robot.path) - 1):
                    start_pos = nav_graph.get_vertex_position(robot.path[i])
                    end_pos = nav_graph.get_vertex_position(robot.path[i + 1])
                    start_x = (start_pos[0] - min_x) * scale + 75
                    start_y = (start_pos[1] - min_y) * scale + 75
                    end_x = (end_pos[0] - min_x) * scale + 75
                    end_y = (end_pos[1] - min_y) * scale + 75
                    path_line = self.scene.addLine(start_x, start_y, end_x, end_y,
                                                 QPen(path_color, 2, Qt.PenStyle.DashLine))
                    path_line.setZValue(1.2)
        
        # Fit view to scene with margin
        scene_rect = self.scene.itemsBoundingRect()
        scene_rect.adjust(-50, -50, 50, 50)  # Add margin
        self.scene.setSceneRect(scene_rect)
        self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        scene_pos = self.mapToScene(event.pos())
        
        # Check if clicked on a robot
        for robot_id, robot_item in self.robot_items.items():
            if robot_item.contains(scene_pos):
                self.selected_robot = robot_id
                self.fleet_gui.status_bar.showMessage(f"Selected Robot R{robot_id}")
                self.draw_network(self.fleet_gui.nav_graph,
                               self.fleet_gui.fleet_manager.robots,
                               self.fleet_gui.traffic_manager)
                return
        
        # Check if clicked on a vertex
        for vertex, vertex_item in self.vertex_items.items():
            if vertex_item.contains(scene_pos):
                if self.selected_robot is not None:
                    # Assign task to selected robot
                    success = self.fleet_gui.fleet_manager.assign_task(
                        self.selected_robot, vertex
                    )
                    if success:
                        self.fleet_gui.status_bar.showMessage(
                            f"Assigned task to R{self.selected_robot}: Move to L{vertex}"
                        )
                    else:
                        self.fleet_gui.status_bar.showMessage(
                            "Failed to assign task: Path blocked or invalid"
                        )
                else:
                    # Add new robot
                    success = self.fleet_gui.fleet_manager.add_robot(vertex)
                    if success:
                        self.fleet_gui.status_bar.showMessage(
                            f"Added new robot at L{vertex}"
                        )
                    else:
                        self.fleet_gui.status_bar.showMessage(
                            "Failed to add robot: Location occupied"
                        )
                self.draw_network(self.fleet_gui.nav_graph,
                                self.fleet_gui.fleet_manager.robots,
                                self.fleet_gui.traffic_manager)
                return
        
        # Clear selection if clicked empty space
        self.selected_robot = None
        self.fleet_gui.status_bar.showMessage("")
        self.draw_network(self.fleet_gui.nav_graph,
                         self.fleet_gui.fleet_manager.robots,
                         self.fleet_gui.traffic_manager)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        scene_pos = self.mapToScene(event.pos())
        old_hover = self.hovered_vertex
        self.hovered_vertex = None
        
        # Check if hovering over a vertex
        for vertex, vertex_item in self.vertex_items.items():
            if vertex_item.contains(scene_pos):
                self.hovered_vertex = vertex
                if self.fleet_gui.traffic_manager.is_intersection_occupied(vertex):
                    self.fleet_gui.status_bar.showMessage(f"L{vertex} is occupied")
                else:
                    self.fleet_gui.status_bar.showMessage(f"L{vertex} is available")
                break
        
        # Redraw if hover state changed
        if old_hover != self.hovered_vertex:
            self.draw_network(self.fleet_gui.nav_graph,
                            self.fleet_gui.fleet_manager.robots,
                            self.fleet_gui.traffic_manager)

class LogPanel(QFrame):
    """Panel for displaying system logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #4A4A4A;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Logs")
        title.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        layout.addWidget(title)
        
        # Log display
        self.log_display = QLabel()
        self.log_display.setStyleSheet("color: #A0A0A0;")
        self.log_display.setWordWrap(True)
        layout.addWidget(self.log_display)
        
    def update_logs(self, logs):
        """Update the log display"""
        text = ""
        for timestamp, message in logs:
            text += f"[{timestamp}] {message}\n"
        self.log_display.setText(text)

class StatusPanel(QFrame):
    """Panel for displaying system status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #4A4A4A;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Status")
        title.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        layout.addWidget(title)
        
        # Status indicators
        self.status_labels = {}
        for status in [RobotStatus.IDLE, RobotStatus.MOVING, RobotStatus.WAITING, RobotStatus.BLOCKED]:
            status_layout = QHBoxLayout()
            
            # Color indicator
            indicator = QLabel()
            indicator.setFixedSize(16, 16)
            indicator.setStyleSheet(f"""
                background-color: {self.get_status_color(status).name()};
                border-radius: 8px;
            """)
            status_layout.addWidget(indicator)
            
            # Status text
            label = QLabel(f"{status.value}: 0")
            label.setStyleSheet("color: #A0A0A0;")
            status_layout.addWidget(label)
            
            layout.addLayout(status_layout)
            self.status_labels[status] = label
            
    def get_status_color(self, status):
        """Get color for status indicator"""
        colors = {
            RobotStatus.IDLE: QColor("#90EE90"),
            RobotStatus.MOVING: QColor("#87CEEB"),
            RobotStatus.WAITING: QColor("#FFD700"),
            RobotStatus.BLOCKED: QColor("#FF69B4"),
            RobotStatus.TASK_COMPLETED: QColor("#808080"),
            RobotStatus.ERROR: QColor("#FF0000")
        }
        return colors.get(status, QColor("#FFFFFF"))
        
    def update_status(self, status_counts):
        """Update status counts"""
        for status, count in status_counts.items():
            if status in self.status_labels:
                self.status_labels[status].setText(f"{status.value}: {count}")

class FleetGUI(QMainWindow):
    """Main GUI window for the Fleet Management System"""
    
    def __init__(self, nav_graph, fleet_manager, traffic_manager):
        super().__init__()
        self.nav_graph = nav_graph
        self.fleet_manager = fleet_manager
        self.traffic_manager = traffic_manager
        
        self.setWindowTitle("Fleet Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create left panel for controls
        left_panel = QVBoxLayout()
        
        # Add control buttons
        add_robot_btn = QPushButton("Add Robot")
        add_robot_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_robot_btn.clicked.connect(self.add_robot)
        left_panel.addWidget(add_robot_btn)
        
        remove_robot_btn = QPushButton("Remove Robot")
        remove_robot_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        remove_robot_btn.clicked.connect(self.remove_robot)
        left_panel.addWidget(remove_robot_btn)
        
        cancel_task_btn = QPushButton("Cancel Task")
        cancel_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        cancel_task_btn.clicked.connect(self.cancel_task)
        left_panel.addWidget(cancel_task_btn)
        
        # Add spacer
        left_panel.addStretch()
        
        # Add instructions
        instructions = QLabel(
            "Instructions:\n\n"
            "1. Click on a vertex to add a robot\n"
            "2. Click on a robot to select it\n"
            "3. Click on a vertex to assign task\n"
            "4. Use buttons to manage robots"
        )
        instructions.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                padding: 10px;
                background-color: #363636;
                border-radius: 4px;
            }
        """)
        instructions.setWordWrap(True)
        left_panel.addWidget(instructions)
        
        # Create network view
        self.network_view = NetworkView(self)
        
        # Create right panel
        right_panel = QVBoxLayout()
        
        # Status panel
        self.status_panel = StatusPanel()
        right_panel.addWidget(self.status_panel)
        
        # Log panel
        self.log_panel = LogPanel()
        right_panel.addWidget(self.log_panel)
        
        # Add panels to main layout
        layout.addLayout(left_panel, stretch=1)
        layout.addWidget(self.network_view, stretch=4)
        layout.addLayout(right_panel, stretch=2)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(50)  # 20 FPS
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
            }
            QStatusBar {
                background-color: #2B2B2B;
                color: #A0A0A0;
            }
            QWidget {
                background-color: #2B2B2B;
            }
        """)
        
    def add_robot(self):
        """Add a new robot at the selected vertex"""
        self.status_bar.showMessage("Click on a vertex to add a robot")
        self.network_view.selected_robot = None
        
    def remove_robot(self):
        """Remove the selected robot"""
        if self.network_view.selected_robot is not None:
            success = self.fleet_manager.remove_robot(self.network_view.selected_robot)
            if success:
                self.status_bar.showMessage(f"Removed Robot R{self.network_view.selected_robot}")
                self.network_view.selected_robot = None
            else:
                self.status_bar.showMessage("Failed to remove robot")
        else:
            self.status_bar.showMessage("Select a robot to remove")
            
    def cancel_task(self):
        """Cancel the task of the selected robot"""
        if self.network_view.selected_robot is not None:
            success = self.fleet_manager.cancel_task(self.network_view.selected_robot)
            if success:
                self.status_bar.showMessage(f"Cancelled task for Robot R{self.network_view.selected_robot}")
            else:
                self.status_bar.showMessage("Failed to cancel task")
        else:
            self.status_bar.showMessage("Select a robot to cancel its task")
        
    def update_display(self):
        """Update the display"""
        # Update network view
        self.network_view.draw_network(self.nav_graph,
                                     self.fleet_manager.robots,
                                     self.traffic_manager)
        
        # Update status panel
        status_counts = {
            RobotStatus.IDLE: 0,
            RobotStatus.MOVING: 0,
            RobotStatus.WAITING: 0,
            RobotStatus.BLOCKED: 0
        }
        for robot in self.fleet_manager.robots.values():
            if robot.status in status_counts:
                status_counts[robot.status] += 1
        self.status_panel.update_status(status_counts)
        
        # Update log panel
        self.log_panel.update_logs(self.fleet_manager.logger.get_recent_logs())
        
        # Update status bar if no message
        if not self.status_bar.currentMessage():
            self.status_bar.showMessage(f"Active Robots: {len(self.fleet_manager.robots)}")
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Handle left click
            pass
        elif event.button() == Qt.MouseButton.RightButton:
            # Handle right click
            pass
        super().mousePressEvent(event)
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event) 