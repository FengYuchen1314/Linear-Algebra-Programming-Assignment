export default function PageLayout({ title, description, children, actions }) {
  return (
    <div className="page">
      <header className="page-header">
        <div className="page-header-text">
          <h2>{title}</h2>
          {description && <p className="page-description">{description}</p>}
        </div>
        {actions && <div className="page-header-actions">{actions}</div>}
      </header>
      <div className="page-body">{children}</div>
    </div>
  );
}

export function ActionPanel({ children }) {
  return <div className="action-panel">{children}</div>;
}

export function ResultsSection({ children }) {
  return <section className="results">{children}</section>;
}
