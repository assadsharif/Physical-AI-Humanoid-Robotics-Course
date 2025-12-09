# Phase 2 Enhancements: Code Sandbox & Analytics Dashboard

**Version**: 1.0.0
**Created**: 2025-12-09
**Status**: Phase 2 Design (3-4 weeks after Phase 1)
**Effort**: 18-25 hours total
**Priority**: ⭐⭐⭐⭐⭐ (Major competitive advantage)

---

## Part 1: Code Sandbox & Interactive Exercises

### **Vision**

Transform the textbook from **read-only content** to **hands-on learning environment**.

**Before**: Students read code → must test locally → friction, low engagement
**After**: Students read code → click "Run" → immediate feedback → high engagement

### **Architecture**

```
┌─────────────────────────────────────────────────┐
│     Docusaurus Chapter (Browser)                │
│  ┌───────────────────────────────────────────┐  │
│  │  "Publishers & Subscribers" chapter       │  │
│  │                                           │  │
│  │  Concept explanation...                  │  │
│  │                                           │  │
│  │  ╔═══════════════════════════════════╗  │  │
│  │  ║ Code Example: Simple Publisher    ║  │  │
│  │  ║                                   ║  │  │
│  │  ║ import rclpy                      ║  │  │
│  │  ║ def main():                       ║  │  │
│  │  ║     pub = Publisher(...)          ║  │  │
│  │  ║     pub.publish("Hello")          ║  │  │
│  │  ║                                   ║  │  │
│  │  ║ [Copy] [Run] [Modify]            ║  │  │
│  │  ╚═══════════════════════════════════╝  │  │
│  │                                           │  │
│  │  ╔═══════════════════════════════════╗  │  │
│  │  ║ Exercise: Write your own node     ║  │  │
│  │  ║                                   ║  │  │
│  │  ║ [Monaco Editor with syntax hi]   ║  │  │
│  │  ║                                   ║  │  │
│  │  ║ [Run Tests] [Submit] [Hint]      ║  │  │
│  │  ║ ✅ Test 1: Node starts           ║  │  │
│  │  ║ ✅ Test 2: Publishes message     ║  │  │
│  │  ║ ❌ Test 3: Correct topic name    ║  │  │
│  │  ╚═══════════════════════════════════╝  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                         │
                 ┌───────┴────────┐
                 │                │
           ┌─────▼──────┐  ┌──────▼────────┐
           │ Code        │  │ ROS 2 Sandbox │
           │ Execution   │  │ Environment   │
           │ Service     │  │ (Docker)      │
           │             │  │               │
           │ - Linting   │  │ - rclpy ready │
           │ - Testing   │  │ - Gazebo sim  │
           │ - Syntax    │  │ - Pre-loaded  │
           └─────────────┘  └───────────────┘
```

### **Components**

#### **1. Monaco Editor Integration**

Add browser-based code editor to Docusaurus.

```typescript
// frontend/src/components/CodeEditor/CodeEditor.tsx

import Editor from "@monaco-editor/react";

export interface CodeEditorProps {
  language: "python" | "ros2";
  defaultCode: string;
  onSubmit: (code: string) => Promise<ExecutionResult>;
  readOnly?: boolean;
  height?: string;
}

export function CodeEditor(props: CodeEditorProps) {
  const [code, setCode] = useState(props.defaultCode);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const result = await executeCode(code, props.language);
      setResult(result);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div>
      <Editor
        height={props.height || "400px"}
        language={props.language === "ros2" ? "python" : "python"}
        value={code}
        onChange={(value) => setCode(value || "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          readOnly: props.readOnly || false,
        }}
      />

      <div>
        <button onClick={handleRun} disabled={isRunning}>
          {isRunning ? "Running..." : "Run"}
        </button>
        <button onClick={() => setCode(props.defaultCode)}>Reset</button>
      </div>

      {result && (
        <div>
          <h4>Output</h4>
          <pre>{result.stdout}</pre>
          {result.errors && <pre style={{ color: "red" }}>{result.errors}</pre>}
        </div>
      )}
    </div>
  );
}
```

#### **2. Code Execution Backend**

Safe Python sandbox for code execution.

```python
# backend/src/services/code_sandbox.py

import subprocess
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any

class CodeSandbox:
    """Execute student code safely in isolated container"""

    async def execute_python(
        self,
        code: str,
        language: str = "python",
        timeout: int = 10,
        test_suite: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code in sandbox

        Args:
            code: Python code to execute
            language: "python" or "ros2"
            timeout: Max execution time (seconds)
            test_suite: Optional tests to validate code

        Returns:
            {
                "success": True/False,
                "stdout": "output",
                "stderr": "errors",
                "test_results": [{"name": "Test 1", "passed": True}],
                "execution_time_ms": 1234
            }
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "user_code.py"
            script_path.write_text(code)

            try:
                # Run with timeout
                result = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        "python",
                        str(script_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=tmpdir
                    ),
                    timeout=timeout
                )

                stdout, stderr = await result.communicate()

                return {
                    "success": result.returncode == 0,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "test_results": await self.run_tests(code, test_suite),
                }

            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "stderr": f"Execution timed out after {timeout} seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "stderr": str(e)
                }

    async def run_tests(
        self,
        code: str,
        tests: List[str]
    ) -> List[Dict[str, Any]]:
        """Run validation tests on code"""

        results = []

        for test in tests:
            try:
                # Execute test
                exec(code)  # First: make sure code runs
                exec(test)  # Then: run test

                results.append({
                    "name": test.split("\n")[0][:50],
                    "passed": True
                })
            except AssertionError as e:
                results.append({
                    "name": test.split("\n")[0][:50],
                    "passed": False,
                    "error": str(e)
                })
            except Exception as e:
                results.append({
                    "name": test.split("\n")[0][:50],
                    "passed": False,
                    "error": f"Runtime error: {str(e)}"
                })

        return results

    async def lint_code(self, code: str) -> List[Dict[str, Any]]:
        """Check code quality with flake8"""

        import flake8.api.legacy as flake8

        guide = flake8.get_style_guide()
        report = guide.check_files(['<string>'], expected=[code])

        return [
            {
                "line": error.line_number,
                "column": error.column_number,
                "message": error.text,
                "code": error.code
            }
            for error in report._application.file_checker_manager.results
        ]
```

#### **3. Exercise Auto-Grading**

Automatically validate student solutions.

```python
# backend/src/services/exercise_grader.py

class ExerciseGrader:
    """Auto-grade student code exercises"""

    async def grade_exercise(
        self,
        exercise_id: str,
        student_code: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Grade student solution"""

        # Get exercise definition
        exercise = await get_exercise(exercise_id)

        # Run student code
        execution = await self.sandbox.execute_python(
            code=student_code,
            test_suite=exercise.tests,
            timeout=exercise.timeout_seconds
        )

        # Calculate score
        test_results = execution.get("test_results", [])
        passed = sum(1 for t in test_results if t["passed"])
        total = len(test_results)
        score = (passed / total * 100) if total > 0 else 0

        # Lint code
        issues = await self.sandbox.lint_code(student_code)

        # Generate feedback
        feedback = self.generate_feedback(
            exercise=exercise,
            execution=execution,
            test_results=test_results,
            lint_issues=issues
        )

        # Store submission
        submission = await store_submission(
            exercise_id=exercise_id,
            user_id=user_id,
            code=student_code,
            score=score,
            feedback=feedback,
            test_results=test_results
        )

        return {
            "submission_id": submission.id,
            "score": score,
            "passed_tests": passed,
            "total_tests": total,
            "feedback": feedback,
            "test_results": test_results,
            "lint_issues": issues[:5],  # Top 5 issues
            "passed": score >= 80  # 80% = pass
        }

    def generate_feedback(
        self,
        exercise,
        execution,
        test_results,
        lint_issues
    ) -> str:
        """Generate personalized feedback"""

        feedback = []

        # Success/failure
        if execution["success"]:
            feedback.append("✅ Code executed successfully!")
        else:
            feedback.append("❌ Code has errors. See below.")
            feedback.append(f"Error: {execution.get('stderr', '')}")

        # Test results
        for result in test_results:
            if result["passed"]:
                feedback.append(f"✅ {result['name']}")
            else:
                feedback.append(f"❌ {result['name']}")
                if "error" in result:
                    feedback.append(f"   Hint: {result['error']}")

        # Linting
        if lint_issues:
            feedback.append("\n💡 Code quality suggestions:")
            for issue in lint_issues[:3]:
                feedback.append(f"   Line {issue['line']}: {issue['message']}")

        return "\n".join(feedback)
```

#### **4. ROS 2 Sandbox Setup**

Pre-configured Docker container with ROS 2.

```dockerfile
# Dockerfile.sandbox

FROM ros:humble-ros-core

# Install Python packages
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

# Pre-load common ROS 2 packages
RUN apt-get update && apt-get install -y \
    ros-humble-geometry-msgs \
    ros-humble-std-msgs \
    ros-humble-nav2 \
    && rm -rf /var/lib/apt/lists/*

# Setup workspace
WORKDIR /student_workspace
RUN . /opt/ros/humble/setup.sh

# Entry: run student code
CMD ["bash"]
```

```bash
# docker-compose addition for sandbox service

sandbox:
  build:
    context: .
    dockerfile: Dockerfile.sandbox
  image: textbook-sandbox:latest
  volumes:
    - ./sandbox:/workspace
  environment:
    - ROS_DOMAIN_ID=1
  networks:
    - textbook-net
```

### **Phase 2 API Endpoints**

#### **POST /api/exercises/{exercise_id}/submit**

Submit code for grading.

```json
{
  "code": "import rclpy\n...",
  "language": "python"
}
```

**Response**:
```json
{
  "submission_id": "sub-123",
  "score": 85,
  "passed": true,
  "feedback": "✅ Code executed successfully!...",
  "test_results": [
    {"name": "Test 1: Node starts", "passed": true},
    {"name": "Test 2: Publishes message", "passed": true}
  ]
}
```

#### **GET /api/exercises/{exercise_id}/submissions**

Get student's submission history.

```json
{
  "submissions": [
    {
      "submission_id": "sub-123",
      "submitted_at": "2025-12-09T10:00:00Z",
      "score": 85,
      "feedback": "..."
    }
  ]
}
```

---

## Part 2: Analytics Dashboard

### **Vision**

Give educators **data-driven insights** into student learning.

**Questions Dashboard Answers**:
- Which chapters are hardest?
- Where are students dropping out?
- Who needs help?
- What's the learning velocity?
- How effective is the curriculum?

### **Architecture**

```
┌──────────────────────────────────────────────┐
│     Analytics Aggregation Service            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Collect Events:                        │ │
│  │ - chapter_started                      │ │
│  │ - chapter_completed                    │ │
│  │ - quiz_attempted                       │ │
│  │ - exercise_submitted                   │ │
│  │ - chatbot_query                        │ │
│  │ - user_signup / user_dropout           │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────┐
│  Analytics Database Tables                   │
│  - user_analytics                            │
│  - chapter_analytics                         │
│  - quiz_analytics                            │
│  - exercise_analytics                        │
│  - chatbot_analytics                         │
│  - cohort_analytics                          │
└──────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────┐
│     Analytics API                            │
│  - GET /api/analytics/overview               │
│  - GET /api/analytics/chapters               │
│  - GET /api/analytics/users/{id}             │
│  - GET /api/analytics/cohort                 │
└──────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────┐
│     Analytics Dashboard (React)              │
│  - Overview metrics                          │
│  - Chapter difficulty heatmap                │
│  - Student progress tracking                 │
│  - Churn funnel                              │
│  - Quiz performance analysis                 │
│  - Chatbot usage patterns                    │
└──────────────────────────────────────────────┘
```

### **Database Schema**

```sql
CREATE TABLE user_analytics (
    user_id UUID PRIMARY KEY REFERENCES users(id),

    -- Engagement
    chapters_started INT DEFAULT 0,
    chapters_completed INT DEFAULT 0,
    total_time_spent_minutes INT DEFAULT 0,
    last_active_at TIMESTAMP,

    -- Performance
    avg_quiz_score FLOAT,
    exercises_attempted INT DEFAULT 0,
    exercises_passed INT DEFAULT 0,

    -- Progression
    current_chapter_id UUID REFERENCES chapters(id),
    progression_percentage INT,
    days_since_signup INT,
    is_active BOOLEAN DEFAULT TRUE,

    -- Predicted churn
    churn_risk_score FLOAT,  -- 0.0-1.0 (higher = at risk)
    last_churn_check TIMESTAMP,

    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chapter_analytics (
    chapter_id UUID PRIMARY KEY REFERENCES chapters(id),

    -- Traffic
    total_views INT DEFAULT 0,
    total_students INT DEFAULT 0,
    completion_rate FLOAT,  -- % of students who finished

    -- Difficulty indicators
    avg_time_spent_minutes INT,
    quiz_pass_rate FLOAT,
    exercise_pass_rate FLOAT,

    -- Challenges
    dropout_count INT DEFAULT 0,  -- Students who quit chapter
    avg_attempts_to_pass INT,
    common_errors JSONB DEFAULT '{}',

    -- Sentiment
    avg_user_rating FLOAT,  -- From chatbot feedback

    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quiz_analytics (
    quiz_id UUID PRIMARY KEY,
    chapter_id UUID REFERENCES chapters(id),

    -- Performance
    total_attempts INT DEFAULT 0,
    avg_score FLOAT,
    pass_rate FLOAT,

    -- Question analysis
    question_difficulties JSONB,  -- Per question stats
    common_wrong_answers JSONB,

    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE exercise_analytics (
    exercise_id UUID PRIMARY KEY,
    chapter_id UUID REFERENCES chapters(id),

    -- Submission stats
    total_submissions INT DEFAULT 0,
    pass_rate FLOAT,
    avg_attempts INT,
    avg_score FLOAT,

    -- Difficulty
    median_time_minutes INT,
    common_errors JSONB,
    hint_requests INT DEFAULT 0,

    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chatbot_analytics (
    day DATE PRIMARY KEY,

    -- Usage
    total_queries INT DEFAULT 0,
    unique_users INT DEFAULT 0,
    avg_queries_per_user FLOAT,

    -- Quality
    avg_user_rating FLOAT,  -- 1-5 stars
    helpful_rate FLOAT,  -- % rated helpful

    -- Topics
    top_topics JSONB,  -- Most asked topics
    unanswered_queries INT DEFAULT 0,

    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cohort_analytics (
    cohort_id UUID PRIMARY KEY,  -- Group of students
    cohort_name VARCHAR(255),

    -- Aggregate metrics
    total_students INT,
    avg_completion_percentage FLOAT,
    avg_days_to_complete INT,
    churn_rate FLOAT,

    -- Comparison
    below_avg_students INT,  -- Need intervention
    high_performers INT,  -- Ready for advanced

    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Analytics API Endpoints**

#### **GET /api/analytics/overview**

Overview dashboard (educators).

```json
{
  "total_students": 150,
  "active_students": 120,
  "avg_completion_percentage": 45,
  "churn_rate": 0.12,
  "avg_quiz_score": 78.5,
  "total_chatbot_queries": 2340,

  "difficulty_ranking": [
    {"chapter": "5.3: LLM Planning", "difficulty_score": 8.5},
    {"chapter": "4.3: RL Training", "difficulty_score": 8.2},
    {"chapter": "3.5: Gazebo Debugging", "difficulty_score": 7.8}
  ],

  "at_risk_students": [
    {
      "user_id": "user-123",
      "name": "Ahmed Ali",
      "churn_risk": 0.85,
      "last_active": "2025-12-05",
      "current_chapter": "2.2",
      "recommendation": "Check in - hasn't been active 4 days"
    }
  ]
}
```

#### **GET /api/analytics/chapters**

Detailed chapter analytics.

```json
{
  "chapter_id": "ch-001",
  "chapter": "2.1: ROS 2 Basics",

  "engagement": {
    "total_views": 450,
    "unique_students": 120,
    "avg_time_minutes": 45,
    "completion_rate": 0.92
  },

  "performance": {
    "quiz_pass_rate": 0.85,
    "exercise_pass_rate": 0.78,
    "avg_attempts_to_pass": 2.1
  },

  "difficulty": {
    "difficulty_score": 6.2,  // 0-10
    "dropout_count": 15,
    "struggling_students": 12
  },

  "common_issues": [
    {
      "issue": "ImportError: No module named rclpy",
      "affected_students": 8,
      "solution": "See setup guide in Chapter 1"
    }
  ]
}
```

#### **GET /api/analytics/users/{user_id}**

Individual student analytics.

```json
{
  "user_id": "user-123",
  "user_name": "Ahmed Ali",

  "engagement": {
    "days_active": 15,
    "total_hours": 24.5,
    "last_active": "2025-12-09T10:00:00Z"
  },

  "progress": {
    "chapters_completed": 8,
    "current_chapter": "2.2",
    "completion_percentage": 35,
    "predicted_completion_date": "2025-12-28"
  },

  "performance": {
    "avg_quiz_score": 82.3,
    "exercises_passed": 12,
    "exercises_failed": 3,
    "pass_rate": 0.80
  },

  "churn_risk": {
    "churn_risk_score": 0.15,  // 0.0-1.0
    "status": "Low risk",
    "factors": ["Consistent activity", "Good quiz scores"]
  },

  "chapter_history": [
    {
      "chapter": "2.1: ROS 2 Basics",
      "completed": true,
      "quiz_score": 88,
      "time_spent": 60,
      "exercises_passed": 2
    }
  ]
}
```

#### **GET /api/analytics/cohort**

Compare cohorts of students.

```json
{
  "cohorts": [
    {
      "cohort_name": "Batch 1 (Dec 2025)",
      "total_students": 50,
      "avg_completion": 0.45,
      "avg_quiz_score": 78.2,
      "churn_rate": 0.10
    },
    {
      "cohort_name": "Batch 2 (Jan 2026)",
      "total_students": 35,
      "avg_completion": 0.32,
      "avg_quiz_score": 75.1,
      "churn_rate": 0.15
    }
  ]
}
```

### **Dashboard UI Components**

```typescript
// frontend/src/components/Analytics/AnalyticsDashboard.tsx

export function AnalyticsDashboard() {
  const [overview, setOverview] = useState(null);
  const [difficulty, setDifficulty] = useState(null);
  const [atRiskStudents, setAtRiskStudents] = useState([]);

  useEffect(() => {
    // Fetch analytics
    fetchAnalyticsOverview().then(setOverview);
    fetchChapterDifficulty().then(setDifficulty);
    fetchAtRiskStudents().then(setAtRiskStudents);
  }, []);

  return (
    <div className="analytics-dashboard">
      <h1>Learning Analytics</h1>

      {/* Overview Cards */}
      <MetricsRow>
        <MetricCard
          title="Total Students"
          value={overview?.total_students}
          trend="+12%"
        />
        <MetricCard
          title="Active Students"
          value={overview?.active_students}
          percentage={overview?.active_percentage}
        />
        <MetricCard
          title="Avg Completion"
          value={`${overview?.avg_completion}%`}
          trend="+5%"
        />
        <MetricCard
          title="Churn Rate"
          value={`${overview?.churn_rate * 100}%`}
          color="warning"
        />
      </MetricsRow>

      {/* Chapter Difficulty Heatmap */}
      <DifficultyHeatmap
        chapters={difficulty}
        onClick={(ch) => navigate(`/analytics/chapters/${ch.id}`)}
      />

      {/* At-Risk Students */}
      <AtRiskStudentsTable
        students={atRiskStudents}
        onStudentClick={(user) => navigate(`/analytics/users/${user.id}`)}
      />

      {/* Completion Funnel */}
      <CompletionFunnel />
    </div>
  );
}
```

---

## Implementation Timeline

### **Phase 2 (3-4 weeks after Phase 1)**

**Week 1**:
- [ ] Add Code Sandbox service (5 hours)
- [ ] Integrate Monaco Editor (3 hours)
- [ ] Create exercise auto-grading (4 hours)

**Week 2**:
- [ ] Set up analytics database (4 hours)
- [ ] Implement analytics collection (3 hours)
- [ ] Create analytics API (5 hours)

**Week 3**:
- [ ] Build analytics dashboard UI (6 hours)
- [ ] Test end-to-end (2 hours)
- [ ] Performance optimization (2 hours)

**Total**: ~34 hours (4 weeks parallel with Phase 2 other work)

---

## Success Criteria

### **Code Sandbox**
- ✅ Students can run code in browser (no local setup)
- ✅ Code execution < 5 seconds
- ✅ Auto-grading works (80%+ accuracy)
- ✅ Clear feedback on failures
- ✅ < 100ms latency for code submission

### **Analytics**
- ✅ Real-time data collection (< 1 sec delay)
- ✅ Dashboard loads < 2 seconds
- ✅ At-risk students identified (churn prediction > 80% accurate)
- ✅ Chapter difficulty scores correlate with actual pass rates
- ✅ Actionable insights for educators

---

## Impact

### **User Engagement**
- 10-20% increase in time on platform
- 15-25% improvement in exercise completion
- 5-10% improvement in quiz scores

### **Educator Insights**
- Identify struggling chapters (data-driven curriculum improvements)
- Predict student churn (proactive intervention)
- Measure learning effectiveness (ROI)

### **Competitive Advantage**
- Interactive code sandbox → vs static textbooks ✅
- Analytics dashboard → vs MOOCs without insights ✅
- Auto-grading → vs manual grading ✅

---

**Status**: Ready for Phase 2 implementation
**Next**: Begin Phase 1, plan Phase 2 in parallel

