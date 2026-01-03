// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Seat Allocation System',
  tagline: 'Intelligent classroom seating arrangement system',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://seat-allocation-sys.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'TANISHX1', // Usually your GitHub org/user name.
  projectName: 'seat-allocation-sys', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // REQUIRED FOR MERMAID: Enable mermaid markdown parsing
  markdown: {
    mermaid: true,
  },

  // REQUIRED FOR MERMAID: Add the theme to the themes array
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Edit this page link
          editUrl:
            'https://github.com/TANISHX1/seat-allocation-sys/tree/main/Frontend/docs/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Edit this page link
          editUrl:
            'https://github.com/TANISHX1/seat-allocation-sys/tree/main/Frontend/docs/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
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
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      // OPTIONAL: Mermaid specific configuration
      mermaid: {
        theme: { light: 'neutral', dark: 'forest' },
      },
      navbar: {
        hideOnScroll: false,
        style: 'dark',
        title: 'Seat Allocation',
        logo: {
          alt: 'Seat Allocation System Logo',
          src: 'img/logo.svg',
          srcDark: 'img/logo.svg',
          height: 32,
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'mainSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'dropdown',
            label: 'Resources',
            position: 'left',
            items: [
              {
                label: 'API Reference',
                to: '/docs/algorithm-documentation',
              },
              {
                label: 'Architecture',
                to: '/docs/system-architecture',
              },
              {
                label: 'Quick Reference',
                to: '/docs/quick-reference',
              },
            ],
          },
          { to: '/blog', label: 'Blog', position: 'left' },
          {
            href: 'https://github.com/TANISHX1/seat-allocation-sys',
            position: 'right',
            className: 'header-github-link',
            'aria-label': 'GitHub repository',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'Algorithm Guide',
                to: '/docs/algorithm-documentation',
              },
              {
                label: 'Quick Reference',
                to: '/docs/quick-reference',
              },
              {
                label: 'Authentication',
                to: '/docs/authentication-setup',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'System Architecture',
                to: '/docs/system-architecture',
              },
              {
                label: 'API Endpoints',
                to: '/docs/algorithm-documentation#api-endpoints',
              },
              {
                label: 'Configuration',
                to: '/docs/getting-started#configuration',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Issues',
                href: 'https://github.com/TANISHX1/seat-allocation-sys/issues',
              },
              {
                label: 'GitHub Discussions',
                href: 'https://github.com/TANISHX1/seat-allocation-sys/discussions',
              },
              {
                label: 'GitHub Repository',
                href: 'https://github.com/TANISHX1/seat-allocation-sys',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Seat Allocation System. Built with ❤️ and Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json', 'javascript', 'typescript', 'jsx'],
      },
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: false,
        },
      },
    }),
};

export default config;
