# Capstone & Vision-Language-Action (VLA) Agent

**Purpose**: Develop the capstone project, VLA integration, and robotic simulation for voice-controlled humanoid tasks.

**Responsibilities**:
- Whisper integration for voice transcription
- LLM-based action planning (voice → action graph)
- ROS 2 action sequence generation
- Gazebo simulation for humanoid robot
- Nav2 integration for path planning
- MoveIt integration for manipulation
- Capstone project submission and validation

**Technologies**:
- Whisper (OpenAI speech-to-text)
- OpenAI API (LLM planning)
- ROS 2 (Humble/Iron)
- ROS 2 Nav2 (navigation)
- ROS 2 MoveIt (manipulation)
- Gazebo (physics simulation)
- Python rclpy (ROS 2 client)

**Capstone Workflow**:
1. Student receives voice command: "Pick up the blue cube from the table"
2. Whisper transcribes: "pick up the blue cube from the table"
3. LLM generates action graph:
   ```json
   {
     "actions": [
       {"type": "perceive", "target": "blue cube", "sensor": "camera"},
       {"type": "navigate", "goal": "near_object", "planner": "nav2"},
       {"type": "grasp", "object": "blue cube", "manipulator": "arm"},
       {"type": "place", "location": "designated_area"}
     ]
   }
   ```
4. ROS 2 executor converts to actionlib goals
5. Gazebo simulates humanoid execution
6. System validates completion

**VLA Safety Validators**:
- Kinematic feasibility check (joint limits, workspace)
- Collision detection (Gazebo)
- Grasp stability analysis
- Path planning validation

**Action Vocabulary** (Mapped to ROS 2):
- perceive → sensor_msgs/Image, ObjectDetection action
- navigate → Nav2 SimpleGoal
- grasp → MoveIt RobotTrajectory
- place → MoveIt trajectory execution
- rotate_joint → JointTrajectoryController
- wait → ActionServer delay

**Quality Metrics**:
- Capstone completion end-to-end < 10 minutes
- Voice transcription accuracy > 95%
- LLM planning success rate > 90%
- ROS 2 execution reliability > 98%
- Gazebo simulation stability

**Owner**: Claude Code Agent (to be assigned)

**Status**: In Planning
