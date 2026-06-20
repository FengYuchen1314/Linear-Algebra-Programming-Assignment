import MathJaxDisplay from './MathJax';
import { exprToLatex, pickLatex } from '../utils/latex';

export default function PolynomialPreview({ expr, latex, label }) {
  const body = pickLatex(latex, expr);
  if (!body) return null;
  const tex = label ? `${label} = ${body}` : body;
  return (
    <div className="polynomial-preview">
      <MathJaxDisplay tex={tex} />
    </div>
  );
}
