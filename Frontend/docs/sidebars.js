// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  mainSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Overview'
    },
    {
      type: 'doc',
      id: 'getting-started',
      label: 'Getting Started'
    },
    {
      type: 'doc',
      id: 'algorithm-documentation',
      label: 'Algorithm Documentation'
    },
    {
      type: 'doc',
      id: 'system-architecture',
      label: 'System Architecture'
    },
    {
      type: 'doc',
      id: 'quick-reference',
      label: 'Quick Reference'
    },
    {
      type: 'doc',
      id: 'authentication-setup',
      label: 'Authentication Setup'
    }
  ]
};

export default sidebars;
