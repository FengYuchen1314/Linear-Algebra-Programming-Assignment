import MathJaxDisplay from './MathJax';
import { matrixToLatex, labeledMatrix } from '../utils/latex';

export default function MatrixPreview({ matrix, compact, label }) {
  if (!matrix) return null;
  const tex = label ? labeledMatrix(label, matrix) : matrixToLatex(matrix);
  return (
    <div className={`matrix-preview ${compact ? 'compact' : ''}`}>
      <MathJaxDisplay tex={tex} />
    </div>
  );
}
