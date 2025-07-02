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
  // This is the main sidebar for the documentation
  tutorialSidebar: [
    {
      type: 'category',
      label: 'I. Getting Started with the Edge Platform',
      link: {
        type: 'doc',
        id: 'getting-started/platform-overview', // Link to an overview page
      },
      items: [
        'getting-started/platform-overview',
        'getting-started/key-concepts',
        // Add more foundational topics here if needed
      ],
    },
    {
      type: 'category',
      label: 'II. Application Modernization & Microservices',
      link: {
        type: 'doc',
        id: 'application-modernization/microservice-fundamentals', // Link to an intro page
      },
      items: [
        'application-modernization/microservice-fundamentals',
        'application-modernization/design-and-implementation-patterns',
        'application-modernization/operational-best-practices',
        'application-modernization/application-maturity-assessment',
      ],
    },
    {
      type: 'category',
      label: 'III. Migration Playbooks',
      link: {
        type: 'doc',
        id: 'migration-playbooks/overview', // A general overview of migration paths
      },
      items: [
        {
          type: 'category',
          label: 'A. Monolith to Microservices Migration',
          items: [
            'migration-playbooks/monolith-to-microservices/overview',
            'migration-playbooks/monolith-to-microservices/case-study-example',
            'migration-playbooks/monolith-to-microservices/service-decomposition-strategies',
            'migration-playbooks/monolith-to-microservices/kubernetes-deployment-strategies',
            'migration-playbooks/monolith-to-microservices/key-migration-considerations',
            'migration-playbooks/monolith-to-microservices/common-challenges-and-troubleshooting',
            'migration-playbooks/monolith-to-microservices/summary',
          ],
        },
        {
          type: 'category',
          label: 'B. Docker Compose to Kubernetes Migration',
          items: [
            {
              type: 'category',
              label: '1. Developer Guide',
              items: [
                'migration-playbooks/docker-compose-to-kubernetes/developer-guide/introduction-and-core-concepts',
                'migration-playbooks/docker-compose-to-kubernetes/developer-guide/manual-conversion-process',
                'migration-playbooks/docker-compose-to-kubernetes/developer-guide/leveraging-automated-tools',
                'migration-playbooks/docker-compose-to-kubernetes/developer-guide/practical-examples-and-best-practices',
              ],
            },
            {
              type: 'category',
              label: '2. Operational Runbook',
              items: [
                'migration-playbooks/docker-compose-to-kubernetes/operational-runbook/prerequisites-and-setup',
                'migration-playbooks/docker-compose-to-kubernetes/operational-runbook/converting-with-kompose',
                'migration-playbooks/docker-compose-to-kubernetes/operational-runbook/manual-kubernetes-resource-creation',
                'migration-playbooks/docker-compose-to-kubernetes/operational-runbook/advanced-topics-and-cleanup',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'C. Docker Compose to Helm Charts',
          items: [
            'migration-playbooks/docker-compose-to-helm-charts/introduction-and-prerequisites',
            'migration-playbooks/docker-compose-to-helm-charts/conversion-tools-kompose-katenary',
            'migration-playbooks/docker-compose-to-helm-charts/helm-repositories-and-advanced-charting',
            'migration-playbooks/docker-compose-to-helm-charts/score-and-simplified-deployment',
          ],
        },
        {
          type: 'category',
          label: 'D. Docker Compose to Virtual Machines (Kubevirt)',
          items: [
            'migration-playbooks/docker-compose-to-virtual-machines/introduction-and-migration-strategy',
            'migration-playbooks/docker-compose-to-virtual-machines/preparing-golden-images',
            'migration-playbooks/docker-compose-to-virtual-machines/defining-virtual-machine-resources',
            'migration-playbooks/docker-compose-to-virtual-machines/kubevirt-deployment-and-best-practices',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'IV. Platform Deep Dive & Advanced Concepts',
      link: {
        type: 'doc',
        id: 'platform-deep-dive/overview', // Placeholder for an overview page
      },
      items: [
        {
          type: 'category',
          label: 'A. Networking & Connectivity',
          items: [
            'platform-deep-dive/networking/ingress-egress-management',
            'platform-deep-dive/networking/service-mesh-integration',
            'platform-deep-dive/networking/network-policies',
            'platform-deep-dive/networking/edge-network-considerations',
          ],
        },
        {
          type: 'category',
          label: 'B. Security & Compliance',
          items: [
            'platform-deep-dive/security/identity-access-management',
            'platform-deep-dive/security/secrets-management',
            'platform-deep-dive/security/image-security',
            'platform-deep-dive/security/network-security',
            'platform-deep-dive/security/compliance-certifications',
          ],
        },
        {
          type: 'category',
          label: 'C. Storage & Data Management',
          items: [
            'platform-deep-dive/storage/persistent-storage-options',
            'platform-deep-dive/storage/database-services',
            'platform-deep-dive/storage/data-synchronization-consistency',
            'platform-deep-dive/storage/backup-restore',
          ],
        },
        {
          type: 'category',
          label: 'D. Observability & Monitoring',
          items: [
            'platform-deep-dive/observability/logging',
            'platform-deep-dive/observability/metrics',
            'platform-deep-dive/observability/tracing',
            'platform-deep-dive/observability/alerting-dashboards',
            'platform-deep-dive/observability/platform-level-monitoring',
          ],
        },
        {
          type: 'category',
          label: 'E. Armada Platform Components', // New section for Armada specifics
          items: [
            'platform-deep-dive/armada-components/galleon-overview',
            'platform-deep-dive/armada-components/atlas-operational-insights',
            'platform-deep-dive/armada-components/marketplace-integration',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'V. Application Lifecycle Management (ALM)',
      link: {
        type: 'doc',
        id: 'application-lifecycle/overview', // Placeholder for an overview page
      },
      items: [
        {
          type: 'category',
          label: 'A. CI/CD Integration',
          items: [
            'application-lifecycle/ci-cd/integrating-popular-tools',
            'application-lifecycle/ci-cd/automated-deployments',
            'application-lifecycle/ci-cd/gitops-workflows',
          ],
        },
        {
          type: 'category',
          label: 'B. Deployment Strategies & Rollbacks',
          items: [
            'application-lifecycle/deployment-strategies/blue-green-deployments',
            'application-lifecycle/deployment-strategies/canary-deployments',
            'application-lifecycle/deployment-strategies/rolling-updates',
            'application-lifecycle/deployment-strategies/rollback-procedures',
          ],
        },
        {
          type: 'category',
          label: 'C. Scaling & Performance Optimization',
          items: [
            'application-lifecycle/scaling-performance/horizontal-pod-autoscaling',
            'application-lifecycle/scaling-performance/vertical-pod-autoscaling',
            'application-lifecycle/scaling-performance/edge-specific-scaling-challenges',
            'application-lifecycle/scaling-performance/performance-tuning',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'VI. Developer Resources & Support',
      link: {
        type: 'doc',
        id: 'developer-resources/overview', // Placeholder for an overview page
      },
      items: [
        {
          type: 'category',
          label: 'A. Local Development Environment Setup',
          items: [
            'developer-resources/local-dev/mini-kubernetes-solutions',
            'developer-resources/local-dev/edge-simulator-emulator',
            'developer-resources/local-dev/debugging-tools',
          ],
        },
        {
          type: 'category',
          label: 'B. Command-Line Tools & APIs',
          items: [
            'developer-resources/cli-apis/recommended-kubectl-plugins',
            'developer-resources/cli-apis/platform-specific-clis',
            'developer-resources/cli-apis/api-reference',
          ],
        },
        {
          type: 'category',
          label: 'C. Troubleshooting & FAQs',
          items: [
            'developer-resources/troubleshooting/common-issues-solutions',
            'developer-resources/troubleshooting/error-code-reference',
            'developer-resources/troubleshooting/debugging-guides',
          ],
        },
        {
          type: 'category',
          label: 'D. Support & Community',
          items: [
            'developer-resources/support/support-channels',
            'developer-resources/support/community-resources',
            'developer-resources/support/release-notes-roadmap',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'VII. Cost Management (If Applicable)',
      link: {
        type: 'doc',
        id: 'cost-management/overview', // Placeholder for an overview page
      },
      items: [
        'cost-management/pricing-model',
        'cost-management/cost-optimization-strategies',
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
