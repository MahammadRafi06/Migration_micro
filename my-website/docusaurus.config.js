// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Armada Edge Platform',
  tagline: 'Armada Edge Platform (AEP) brings powerful, modular infrastructure to solve your hardest problems at the remote edge. With Atlas, Galleon, and Marketplace, AEP delivers seamless, scalable performance where it matters most.',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-docusaurus-site.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'armada-platform', // Usually your GitHub org/user name.
  projectName: 'aep-docs', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  plugins: [
    // Analytics plugin
    [
      '@docusaurus/plugin-google-gtag',
      {
        trackingID: 'G-XXXXXXXXXX', // Replace with your actual Google Analytics 4 tracking ID
        anonymizeIP: true,
      },
    ],
    // PWA plugin for offline support
    [
      '@docusaurus/plugin-pwa',
      {
        debug: true,
        offlineModeActivationStrategies: [
          'appInstalled',
          'standalone',
          'queryString',
        ],
        pwaHead: [
          {
            tagName: 'link',
            rel: 'icon',
            href: '/img/docusaurus.png',
          },
          {
            tagName: 'link',
            rel: 'manifest',
            href: '/manifest.json',
          },
          {
            tagName: 'meta',
            name: 'theme-color',
            content: 'rgb(37, 194, 160)',
          },
        ],
      },
    ],
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/armada-platform/aep-docs/tree/main/',
          
          // Show last update info
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          
          // Add admonitions
          admonitions: {
            keywords: ['note', 'tip', 'info', 'caution', 'danger', 'warning', 'important'],
          },
          
          // Version management
          versions: {
            current: {
              label: 'Latest',
              path: '/',
            },
          },
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/armada-platform/aep-docs/tree/main/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        // Enable sitemap
        sitemap: {
          lastmod: 'date',
          changefreq: 'weekly',
          priority: 0.5,
          ignorePatterns: ['/tags/**'],
          filename: 'sitemap.xml',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      
      // Enhanced search configuration
      algolia: {
        // The application ID provided by Algolia
        appId: 'YOUR_APP_ID', // Replace with your Algolia app ID
        // Public API key: it is safe to commit it
        apiKey: 'YOUR_API_KEY', // Replace with your Algolia API key
        indexName: 'armada-docs',
        // Optional: see doc section below
        contextualSearch: true,
        // Optional: Specify domains where the navigation should occur through window.location instead of history.push
        externalUrlRegex: 'external\\.com|domain\\.com',
        // Optional: Replace parts of the item URLs from Algolia
        replaceSearchResultPathname: {
          from: '/docs/', // or as RegExp: /\/docs\//
          to: '/',
        },
        // Optional: Algolia search parameters
        searchParameters: {},
        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: 'search',
        //... other Algolia params
      },
      
      // Announcement bar for important updates
      announcementBar: {
        id: 'support_us',
        content:
          '⭐️ If you like our documentation, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/armada-platform/aep-docs">GitHub</a>! ⭐️',
        backgroundColor: '#fafbfc',
        textColor: '#091E42',
        isCloseable: false,
      },
      
      navbar: {
        title: 'AEP Documentation',
        logo: {
          alt: 'Armada Edge Platform Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Docs',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            to: '/docs/glossary',
            label: 'Glossary',
            position: 'left',
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            href: 'https://github.com/armada-platform/aep-docs',
            label: 'GitHub',
            position: 'right',
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
                to: '/docs/getting-started/platform-overview',
              },
              {
                label: 'Migration Playbooks',
                to: '/docs/migration-playbooks/overview',
              },
              {
                label: 'Platform Deep Dive',
                to: '/docs/platform-deep-dive/overview',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Support',
                to: '/docs/developer-resources/support/support-channels',
              },
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/armada-edge-platform',
              },
              {
                label: 'Discord',
                href: 'https://discord.gg/armada',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/armada-platform/aep-docs',
              },
              {
                label: 'Release Notes',
                to: '/docs/developer-resources/support/release-notes-roadmap',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Armada Edge Platform. Built with Docusaurus.`,
      },
      
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        // Add additional languages for syntax highlighting
        additionalLanguages: ['bash', 'yaml', 'json', 'dockerfile', 'powershell'],
      },
      
      // Enhanced color mode
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      
      // Table of contents configuration
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 5,
      },
      
      // Docs configuration
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
      
      // Live code blocks configuration
      liveCodeBlock: {
        playgroundPosition: 'bottom',
      },
    }),
  
  // Enhanced markdown configuration
  markdown: {
    mermaid: true,
  },
  
  themes: ['@docusaurus/theme-mermaid'],
};

export default config;
