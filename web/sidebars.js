/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a set of docs in a scoped sidebar
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

/** @type {import('@docusaurus/types').SidebarsConfig} */
const sidebars = {
  // But you can create a sidebar manually
  tutorialSidebar: [
    'intro',
    {
      label: 'Getting Started',
      items: [
        'getting-started/setup',
        'getting-started/first-steps',
        'getting-started/how-to-use',
      ],
    },
    {
      label: 'ROS 2 Fundamentals',
      items: [
        'ros2/overview',
        'ros2/architecture',
        'ros2/pub-sub',
        'ros2/nodes',
        'ros2/launch-files',
        'ros2/services',
        'ros2/actions',
      ],
    },
    {
      label: 'Simulation & Gazebo',
      items: [
        'simulation/intro',
        'simulation/gazebo-setup',
        'simulation/creating-models',
        'simulation/physics',
        'simulation/sensors',
      ],
    },
    {
      label: 'Digital Twins',
      items: [
        'digital-twins/overview',
        'digital-twins/design',
        'digital-twins/implementation',
      ],
    },
    {
      label: 'Advanced Topics',
      items: [
        'advanced/vision',
        'advanced/llm-integration',
        'advanced/reinforcement-learning',
      ],
    },
    {
      label: 'Projects',
      items: [
        'projects/capstone',
        'projects/examples',
      ],
    },
  ],
};

module.exports = sidebars;
