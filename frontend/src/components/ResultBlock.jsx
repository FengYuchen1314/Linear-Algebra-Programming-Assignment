import MathJaxDisplay from './MathJax';

export default function ResultBlock({ title, children, latex }) {
  return (
    <div className="result-block">
      {title && <h3>{title}</h3>}
      <div className="result-content">{children}</div>
      {latex && (
        <div className="latex-block">
          <MathJaxDisplay tex={latex} />
        </div>
      )}
    </div>
  );
}
