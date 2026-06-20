import MathJaxDisplay from './MathJax';

export default function MathLine({ tex, inline = false, className = '' }) {
  if (!tex) return null;
  const cls = inline ? className : `math-line ${className}`.trim();
  return <MathJaxDisplay tex={tex} inline={inline} className={cls} />;
}
