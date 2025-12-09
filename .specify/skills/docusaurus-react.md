# Skill: Docusaurus & React Component Development

**Description**: Building Docusaurus static sites with custom React components, MDX, and interactive elements.

**Scope**:
- Docusaurus v3 configuration
- Markdown authoring and MDX
- React component development
- Sidebar and routing setup
- Plugin integration
- Theme customization

**Key Technologies**:
- Docusaurus v3
- React 18+
- MDX (interactive markdown)
- Markdown-it (parsing)
- GitHub Pages / Vercel (deployment)

**File Structure**:
```
docs/
  01-intro/
    intro.md
    what-is-physical-ai.md
    index.md
  02-ros2/
    ros2-basics.md
    rclpy-tutorial.md
    urdf-guide.md
  _category_.json  # Module metadata
```

**Docusaurus Config** (`docusaurus.config.js`):
```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  url: 'https://example.com',
  baseUrl: '/',
  presets: [
    ['@docusaurus/preset-classic', {
      docs: {
        sidebarPath: require.resolve('./sidebars.js'),
      },
    }],
  ],
  themeConfig: {
    navbar: { title: 'Textbook', items: [] },
  },
};
```

**Module Sidebar** (`sidebars.js`):
```javascript
module.exports = {
  textbook: [
    {
      label: 'ROS 2 Fundamentals',
      items: [
        'ros2/ros2-basics',
        'ros2/rclpy-tutorial',
        'ros2/urdf-guide',
      ],
    },
  ],
};
```

**React Component in MDX**:
```jsx
import CodeBlock from '@docusaurus/theme-common/CodeBlock';

export function InteractiveExample() {
  const [output, setOutput] = useState('');

  return (
    <div>
      <button onClick={() => setOutput('Hello!')}>Run</button>
      <CodeBlock language="python">
        {`print("Hello from ROS 2!")`}
      </CodeBlock>
      <div>{output}</div>
    </div>
  );
}
```

**Embedding Chatbot**:
```jsx
// docusaurus.config.js swizzled component
import ChatbotWidget from '@/components/ChatbotWidget';

<ChatbotWidget apiEndpoint="https://api.example.com/chat" />
```

**Code Examples with Highlighting**:
```markdown
:::info Python
```python title="example.py" showLineNumbers
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
```
:::
```

**Code Standards**:
- MDX files in `docs/` directory
- One topic per file
- Consistent heading hierarchy (h1 → h3 max)
- Alt text for all images
- Syntax highlighting for code blocks

**Performance**:
- Static generation: < 60 seconds
- Build size: < 10MB
- Deploy time: < 5 minutes

**Accessibility**:
- WCAG 2.1 AA compliance
- Semantic HTML
- Keyboard navigation
- Screen reader support

**Owner**: Docusaurus Content Agent

**Related**: docusaurus-content-agent.md
