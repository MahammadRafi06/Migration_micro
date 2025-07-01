/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // Your existing sidebars...
  migrationGuideSidebar: [
    {
      type: 'category',
      label: 'Monolith to Microservices Migration Guide',
      items: [
        'migration-guide/introduction',
        'migration-guide/understanding-example',
        'migration-guide/service-breakdown',
        'migration-guide/kubernetes-deployment',
        'migration-guide/migration-considerations',
        'migration-guide/troubleshooting',
        'migration-guide/conclusion',
        './Microservices-Maturity-Levels',
        'micro-services/architecture-implementation',
        'micro-services/fundamentals',
        'micro-services/operations-best-practices',
        'Docker Compose to Kubernetese/Docker-Compose-Conversion-Part1',
        'Docker Compose to Kubernetese/Docker-Compose-Conversion-Part2',
        'Docker Compose to Kubernetese/Docker-Compose-Conversion-Part3',
        'Docker Compose to Kubernetese/Docker-Compose-Conversion-Part4'

      ],
    },
  ],
};

module.exports = sidebars;
