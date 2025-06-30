import React from 'react';
import styles from './styles.module.css';

const maturityLevels = [
  {
    stage: 0,
    title: "Legacy Monolith",
    description: "Single codebase, tightly coupled components",
    characteristics: ["Difficult to change independently", "Long release cycles", "Manual deployment"],
    color: "red"
  },
  {
    stage: 1,
    title: "Modular Monolith", 
    description: "Better separation of concerns with internal boundaries",
    characteristics: ["Layered/modular structure", "Still monolithic deployment", "Improving observability"],
    color: "orange"
  },
  {
    stage: 2,
    title: "Microservices Pilot",
    description: "Some components extracted as microservices",
    characteristics: ["Mixed deployment model", "Docker/K8s adoption", "Learning curve challenges"],
    color: "yellow"
  },
  {
    stage: 3,
    title: "Microservices Adoption",
    description: "Most services decomposed with bounded contexts",
    characteristics: ["Independent deployability", "Kubernetes usage", "Centralized observability"],
    color: "blue"
  },
  {
    stage: 4,
    title: "Cloud-Native Maturity",
    description: "Fully microservices-based with 12-factor principles",
    characteristics: ["Service mesh patterns", "Chaos engineering", "Full DevOps integration"],
    color: "green"
  }
];

function MaturityTile({ level }) {
  return (
    <div className={`${styles.tile} ${styles[level.color]}`}>
      <div className={styles.stageNumber}>Stage {level.stage}</div>
      <h3 className={styles.title}>{level.title}</h3>
      <p className={styles.description}>{level.description}</p>
      <ul className={styles.characteristics}>
        {level.characteristics.map((char, index) => (
          <li key={index}>{char}</li>
        ))}
      </ul>
    </div>
  );
}

export default function MaturityLevels() {
  return (
    <section className={styles.maturityLevels}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Microservices Maturity Levels</h2>
        <div className={styles.tilesGrid}>
          {/* First row - 2 tiles */}
          <div className={styles.row}>
            <MaturityTile level={maturityLevels[0]} />
            <MaturityTile level={maturityLevels[1]} />
          </div>
          {/* Second row - 2 tiles */}
          <div className={styles.row}>
            <MaturityTile level={maturityLevels[2]} />
            <MaturityTile level={maturityLevels[3]} />
          </div>
          {/* Third row - 1 centered tile */}
          <div className={`${styles.row} ${styles.singleTile}`}>
            <MaturityTile level={maturityLevels[4]} />
          </div>
        </div>
      </div>
    </section>
  );
} 