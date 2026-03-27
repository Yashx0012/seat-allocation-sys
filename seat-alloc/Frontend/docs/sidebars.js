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
      label: '🚀 Introduction'
    },
    {
      type: 'category',
      label: '📖 User Guide',
      collapsed: false,
      items: [
        'user-guide/manual',
        'user-guide/troubleshooting',
        {
          type: 'category',
          label: '🧭 Quick Navigation',
          collapsed: true,
          items: [
            {
              type: 'doc',
              id: 'user-guide/frontend-setup',
              label: '🖥️ Frontend Setup',
            },
            {
              type: 'doc',
              id: 'user-guide/backend-setup',
              label: '⚙️ Backend Setup',
            },
          ],
        },
      ],
    },
    {
      type: 'category',
      label: '🧠 Algorithm',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'developers/Algorithm/index',
          label: '🧠 Overview'
        },
        {
          type: 'category',
          label: '🧩 Core Modules',
          collapsed: false,
          items: [
            'developers/Algorithm/data-structures',
            'developers/Algorithm/distribution-logic',
            'developers/Algorithm/allocation-engine',
            'developers/Algorithm/paper-set-priority',
            'developers/Algorithm/validation-system',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: '🛠️ Developer Reference',
      collapsed: true,
      items: [
        'developers/setup',
        'developers/architecture',
        'developers/api',
        'developers/auth',
      ],
    },
  ]
};

export default sidebars;
