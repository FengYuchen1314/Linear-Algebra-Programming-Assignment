import MathJaxDisplay from './MathJax';

export default function MathLine({ tex, inline = false, className = '' }) {
  if (!tex) return null;
  return <MathJaxDisplay tex={tex} inline={inline} className={className} />;
}
