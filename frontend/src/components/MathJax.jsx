import { useEffect, useRef } from 'react';
import { useDisplayPrecision } from '../context/DisplayPrecisionContext';
import { applyDisplayPrecisionToLatex } from '../utils/displayPrecision';

function waitForMathJax() {
  if (window.MathJax?.typesetPromise) {
    return window.MathJax.startup?.promise ?? Promise.resolve();
  }
  return new Promise((resolve) => {
    const timer = setInterval(() => {
      if (window.MathJax?.typesetPromise) {
        clearInterval(timer);
        (window.MathJax.startup?.promise ?? Promise.resolve()).then(resolve);
      }
    }, 50);
  });
}

export default function MathJaxDisplay({ tex, inline = false, className = '', formatNumeric = true }) {
  const ref = useRef(null);
  const { precision } = useDisplayPrecision();
  const displayTex = formatNumeric ? applyDisplayPrecisionToLatex(tex, precision) : tex;

  useEffect(() => {
    const node = ref.current;
    if (!node || displayTex == null || displayTex === '') return undefined;

    node.textContent = inline ? `\\(${displayTex}\\)` : `\\[${displayTex}\\]`;

    let cancelled = false;
    waitForMathJax().then(() => {
      if (cancelled || !ref.current) return null;
      if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([node]);
      }
      return window.MathJax.typesetPromise([node]);
    }).catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [displayTex, inline, precision]);

  if (displayTex == null || displayTex === '') return null;

  const Tag = inline ? 'span' : 'div';
  const modeClass = inline ? 'mathjax-inline' : 'mathjax-display';
  return <Tag ref={ref} className={`${modeClass} ${className}`.trim()} />;
}
