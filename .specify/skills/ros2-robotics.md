# Skill: ROS 2 Robotics Development

**Description**: Developing ROS 2 nodes, action servers, and integration for humanoid robot control.

**Scope**:
- ROS 2 node lifecycle management
- Topics, services, and actions
- URDF model parsing and usage
- Launch file creation
- Nav2 integration for navigation
- MoveIt integration for manipulation
- Gazebo simulation

**Key Technologies**:
- ROS 2 Humble or Iron
- rclpy (Python ROS 2 client)
- Nav2 (navigation stack)
- MoveIt (motion planning)
- Gazebo (physics simulation)
- URDF (robot description format)

**Core Patterns**:

**1. Node Lifecycle**:
```python
from rclpy.lifecycle import Node

class RobotController(Node):
    def on_configure(self):
        # Setup: initialize publishers, subscribers
        self.create_subscription(...)
        self.create_publisher(...)

    def on_activate(self):
        # Start executing
        pass

    def on_deactivate(self):
        # Stop executing
        pass
```

**2. Action Server** (for capstone execution):
```python
from rclpy_action import ActionServer

self.action_server = ActionServer(
    self,
    ExecuteAction,
    'execute_task',
    self.execute_callback
)

async def execute_callback(self, goal_handle):
    # Execute goal, publish feedback
    result = ExecuteAction.Result()
    return result
```

**3. URDF Parsing**:
```python
import urdf_parser_py.urdf as urdf_parser

robot = urdf_parser.URDF.from_xml_file("humanoid.urdf")
for joint in robot.joints:
    print(f"Joint: {joint.name}, Type: {joint.type}")
```

**4. Launch File**:
```python
# launch/humanoid_simulation.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='gazebo_ros', executable='gazebo',
             arguments=['--ros-args', '-p', 'use_sim_time:=true']),
        Node(package='robot_controller', executable='controller_node'),
        Node(package='nav2_bringup', executable='bringup_launch.py')
    ])
```

**Code Standards**:
- PEER naming conventions (Publishers, subscriptions, Events, RPC)
- Proper lifecycle transitions
- Diagnostics publishing (hardware_interface/DiagnosticsUpdater)
- Error handling and recovery

**Testing**:
- Unit tests with launch_testing
- Gazebo simulation for integration tests
- ROS 2 bag recording for debugging

**Performance Targets**:
- Node spin frequency: 10-50 Hz
- Action execution time: < 10 seconds (for capstone tasks)
- Message latency: < 100ms

**Owner**: Capstone VLA Agent

**Related**: capstone-vla-agent.md, gazebo-simulation.md
