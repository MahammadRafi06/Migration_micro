import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
      </div>
    </header>
  );
}

function ComponentsSection() {
  return (
    <section className={styles.componentsSection}>
      <div className="container">
        <div className="row">
          <div className="col col--4">
            <div className={styles.componentCard}>
              <Heading as="h3">Atlas</Heading>
              <p>Atlas is our operational insights product for all your connected assets. Seamlessly monitor and manage your IoT devices from a single pane of glass.</p>
            </div>
          </div>
          <div className="col col--4">
            <div className={styles.componentCard}>
              <Heading as="h3">Galleon</Heading>
              <p>Galleons are our ruggedized modular data centers, powered by AEP. Multiple form factors designed to tackle your hardest problems.</p>
            </div>
          </div>
          <div className="col col--4">
            <div className={styles.componentCard}>
              <Heading as="h3">Marketplace</Heading>
              <p>Marketplace is your hub for all the hardware and software you need to operate at the remote edge.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`AEP Documentation | Armada`}
      description="Armada AEP Documentation">
      <HomepageHeader />
      <main>
        <ComponentsSection />
      </main>
    </Layout>
  );
}
