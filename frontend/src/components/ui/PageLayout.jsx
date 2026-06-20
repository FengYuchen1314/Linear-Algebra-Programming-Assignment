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

export function ResultsSection({ children, placeholder = '选择输入并点击分析后，结果将显示在此处。' }) {
  const hasContent = children != null && children !== false;

  return (
    <section className="results-section">
      <h2 className="text-h2 results-section-title">分析结果</h2>
      <div className="results">
        {hasContent ? children : (
          <p className="results-empty text-muted">{placeholder}</p>
        )}
      </div>
    </section>
  );
}
