import MathJaxDisplay from './MathJax';
import { exprToLatex } from '../utils/latex';

export default function PolynomialPreview({ expr, label }) {
  if (!expr) return null;
  const tex = label ? `${label} = ${exprToLatex(expr)}` : exprToLatex(expr);
  return (
    <div className="polynomial-preview">
      <MathJaxDisplay tex={tex} />
    </div>
  );
}
