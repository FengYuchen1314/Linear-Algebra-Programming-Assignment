export default function PageLayout({ title, description, children }) {
  return (
    <div className="page">
      <header className="page-hero">
        <h1 className="md-headline-medium page-title">{title}</h1>
        {description && <p className="page-description md-body-large">{description}</p>}
      </header>
      <div className="page-body">{children}</div>
    </div>
  );
}

export function WorkflowSection({ children }) {
  return <section className="workflow-section">{children}</section>;
}

export function ActionPanel({ title = '分析参数', children }) {
  return (
    <div className="md-card md-card--outlined action-panel">
      <h3 className="md-title-small action-panel-title">{title}</h3>
      <div className="action-panel-body">{children}</div>
    </div>
  );
}

export function ResultsSection({ children }) {
  return (
    <section className="results-section">
      <h2 className="md-title-large results-section-title">分析结果</h2>
      <div className="results">{children}</div>
    </section>
  );
}
