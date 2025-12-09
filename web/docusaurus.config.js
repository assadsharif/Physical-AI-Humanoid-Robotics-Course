// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Learn robotics with AI-powered tutoring',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://robotics-textbook.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'robotics-ai',
  projectName: 'textbook',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/robotics-ai/textbook/tree/main/web/docs',
        },
        blog: {
          showReadingTime: true,
          editUrl:
            'https://github.com/robotics-ai/textbook/tree/main/web/blog',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      metadata: [
        {
          name: 'description',
          content: 'Learn Physical AI and Humanoid Robotics with AI-powered tutoring',
        },
        {
          name: 'keywords',
          content: 'robotics, ROS 2, AI, learning, education',
        },
      ],
      image: 'img/social-card.jpg',
      navbar: {
        title: 'Robotics Textbook',
        logo: {
          alt: 'Robotics AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Courses',
          },
          { to: '/blog', label: 'Blog', position: 'left' },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            type: 'custom-auth',
            position: 'right',
          },
          {
            href: 'https://github.com/robotics-ai/textbook',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Courses',
            items: [
              {
                label: 'ROS 2 Fundamentals',
                to: '/docs/ros2/intro',
              },
              {
                label: 'Simulation & Digital Twins',
                to: '/docs/simulation/intro',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/example',
              },
              {
                label: 'GitHub Issues',
                href: 'https://github.com/robotics-ai/textbook/issues',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/robotics-ai/textbook',
              },
            ],
          },
        ],
        copyright: `Copyright © 2025 Physical AI. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml'],
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;
