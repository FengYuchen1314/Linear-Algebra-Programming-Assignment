import MathJaxDisplay from './MathJax';
import { IconCheck } from './ui/Icons';

export default function ResultBlock({ title, children, latex }) {
  return (
    <article className="card result-block">
      {title && (
        <header className="result-block-header">
          <h3 className="text-h4">{title}</h3>
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
    <div className="banner banner--success selected-info">
      <strong className="banner__label">
        <IconCheck aria-hidden />
        已选择
      </strong>
      {children}
    </div>
  );
}
