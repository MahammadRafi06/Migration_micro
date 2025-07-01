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
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Migration Guide',
      items: [
        'Migration Guide/introduction',
        'Migration Guide/understanding-example',
        'Migration Guide/service-breakdown',
        'Migration Guide/kubernetes-deployment',
        'Migration Guide/migration-considerations',
        'Migration Guide/troubleshooting',
        'Migration Guide/conclusion',
      ],
    },
    {
      type: 'category',
      label: 'Microservices',
      items: [
        'Microservices-Maturity-Levels',
        'Microservices/fundamentals',
        'Microservices/architecture-implementation',
        'Microservices/operations-best-practices',
      ],
    },
    {
      type: 'category',
      label: 'Developer Guide: Docker Compose to Kubernetes',
      items: [
        'Developer Guide: Docker Compose to Kubernetese/introduction-and-concepts',
        'Developer Guide: Docker Compose to Kubernetese/manual-conversion',
        'Developer Guide: Docker Compose to Kubernetese/automated-tools',
        'Developer Guide: Docker Compose to Kubernetese/example-best-practices',
      ],
    },
    {
      type: 'category',
      label: 'Developer Guide: Docker Compose to Helm Charts',
      items: [
        'Developer Guide: Docker Compose to Helm Charts/helm-introduction-prerequisites',
        'Developer Guide: Docker Compose to Helm Charts/helm-kompose-katenary',
        'Developer Guide: Docker Compose to Helm Charts/helm-repositories-advanced',
        'Developer Guide: Docker Compose to Helm Charts/helm-score-deployment',
      ],
    },
    {
      type: 'category',
      label: 'Developer Runbook: Docker Compose to Kubernetes',
      items: [
        'Devloper Runbook: Docker Compose to Kubernetese/setup-prerequisites',
        'Devloper Runbook: Docker Compose to Kubernetese/converting-with-kompose',
        'Devloper Runbook: Docker Compose to Kubernetese/deployment-manual-creation',
        'Devloper Runbook: Docker Compose to Kubernetese/advanced-considerations-cleanup',
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
