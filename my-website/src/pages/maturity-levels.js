import React from 'react';
import Layout from '@theme/Layout';
import MaturityLevels from '@site/src/components/MaturityLevels';

export default function MaturityLevelsPage() {
  return (
    <Layout
      title="Microservices Maturity Levels"
      description="Assessment framework for microservices adoption stages">
      <main>
        <MaturityLevels />
      </main>
    </Layout>
  );
} 