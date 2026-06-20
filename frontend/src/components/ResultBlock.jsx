import MathJaxDisplay from './MathJax';
import { IconCheck } from './ui/Icons';

export default function ResultBlock({ title, children, latex }) {
  return (
    <div className="result-block">
      {title && (
        <div className="result-block-header">
          <span className="result-block-marker" aria-hidden />
          <h3>{title}</h3>
        </div>
      )}
      <div className="result-content">{children}</div>
      {latex && (
        <div className="latex-block">
          <MathJaxDisplay tex={latex} />
        </div>
      )}
    </div>
  );
}

export function SelectedBanner({ children }) {
  return (
    <div className="selected-info">
      <strong><IconCheck /> 已选择</strong>
      {children}
    </div>
  );
}
