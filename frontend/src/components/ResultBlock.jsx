import MathJaxDisplay from './MathJax';
import { IconCheck } from './ui/Icons';

export default function ResultBlock({ title, children, latex }) {
  return (
    <article className="md-card md-card--elevated result-block">
      {title && (
        <header className="result-block-header">
          <h3 className="md-title-medium">{title}</h3>
        </header>
      )}
      <div className="result-content">{children}</div>
      {latex && (
        <div className="latex-block">
          <MathJaxDisplay tex={latex} />
        </div>
      )}
    </article>
  );
}

export function SelectedBanner({ children }) {
  return (
    <div className="md-banner md-banner--success selected-info">
      <strong className="md-label-large">
        <IconCheck aria-hidden />
        已选择
      </strong>
      {children}
    </div>
  );
}
