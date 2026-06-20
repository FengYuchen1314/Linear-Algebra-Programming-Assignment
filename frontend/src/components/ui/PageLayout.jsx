export default function PageLayout({ title, description, children }) {
  return (
    <div className="page">
      <header className="page-hero">
        <h1 className="text-h1 page-title">{title}</h1>
        {description && <p className="page-description text-body-lg">{description}</p>}
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
    <div className="card action-panel">
      <h3 className="text-h4 action-panel-title">{title}</h3>
      <div className="action-panel-body">{children}</div>
    </div>
  );
}

export function ResultsSection({ children }) {
  return (
    <section className="results-section">
      <h2 className="text-h2 results-section-title">分析结果</h2>
      <div className="results">{children}</div>
    </section>
  );
}
