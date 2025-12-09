# Skill: OpenAI LLM Integration & Prompt Engineering

**Description**: Integrating OpenAI API for chatbot completions, action planning, and knowledge retrieval.

**Scope**:
- Chat completion API usage
- Prompt engineering for domain-specific tasks
- Temperature and token management
- Streaming responses
- Error handling and fallbacks
- Cost monitoring

**Key Technologies**:
- OpenAI API (gpt-4o, gpt-4-turbo)
- Python openai SDK
- Prompt templates
- Token counting (tiktoken)

**1. Chatbot Completion**:
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_completion(query: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert roboticist teaching Physical AI. Answer only based on provided context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content
```

**2. VLA Action Planning**:
```python
def plan_robot_action(voice_command: str) -> dict:
    """Generate action graph from voice command"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a robot action planner.
                Convert voice commands to JSON action graphs.
                Valid actions: perceive, navigate, grasp, place, rotate_joint.
                Output ONLY valid JSON."""
            },
            {
                "role": "user",
                "content": f"Command: {voice_command}"
            }
        ],
        temperature=0.0,  # Deterministic for reproducibility
        max_tokens=1000
    )

    import json
    action_graph = json.loads(response.choices[0].message.content)
    return action_graph
```

**3. Streaming Response**:
```python
def stream_answer(query: str):
    """Stream chatbot response for real-time display"""

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

**Prompt Templates**:

**RAG Chatbot System Prompt**:
```
You are an expert roboticist and educator specializing in Physical AI,
Embodied Intelligence, and Humanoid Robotics.

Your role:
- Answer questions about ROS 2, Digital Twins, NVIDIA Isaac, and VLA systems
- Cite specific chapters and sections when answering
- Provide code examples in Python using ROS 2 rclpy
- Explain concepts clearly for students

Answer ONLY based on provided content context.
If the context doesn't contain relevant information, say "I don't have information about that in the course materials."
```

**VLA Planning System Prompt**:
```
You are a deterministic robot action planner (seed=0 for reproducibility).

Convert voice commands to structured action graphs.

Valid actions:
- perceive(target: str, sensor: str) → ObjectDetection action
- navigate(goal: str, planner: str) → Nav2 SimpleGoal
- grasp(object: str, manipulator: str) → MoveIt trajectory
- place(location: str) → place object
- rotate_joint(joint_name: str, angle: float) → JointTrajectoryController

Output format:
{
  "actions": [
    {"type": "perceive", "target": "blue cube", "sensor": "camera"},
    {"type": "navigate", "goal": "table_center", "planner": "nav2"},
    ...
  ],
  "safety_checks": ["kinematic_feasible", "no_collision"]
}

Be conservative: if command is ambiguous or unsafe, output error.
```

**Token Counting**:
```python
import tiktoken

def estimate_cost(messages: list) -> float:
    encoding = tiktoken.encoding_for_model("gpt-4o")

    total_tokens = 0
    for msg in messages:
        total_tokens += len(encoding.encode(msg["content"]))

    # gpt-4o pricing: $0.03/1K input, $0.06/1K output
    input_cost = (total_tokens / 1000) * 0.03
    estimated_output_cost = (500 / 1000) * 0.06
    return input_cost + estimated_output_cost
```

**Error Handling**:
```python
from openai import RateLimitError, APIError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    logger.warning("Rate limited, retrying...")
    time.sleep(5)
    # Retry logic
except APIError as e:
    logger.error(f"API error: {e}")
    return {"error": "Service unavailable"}
```

**Performance Targets**:
- Response latency: < 3 seconds (p95)
- Uptime: 99.9%
- Cost per query: < $0.05

**Monitoring**:
- Token usage per request
- Error rates and failures
- Average response time
- Cost tracking

**Owner**: RAG Chatbot Agent, Capstone VLA Agent

**Related**: rag-chatbot-agent.md, capstone-vla-agent.md, fastapi-backend.md
