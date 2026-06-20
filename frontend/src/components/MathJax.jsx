import { useEffect, useRef } from 'react';

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

export default function MathJaxDisplay({ tex, inline = false, className = '' }) {
  const ref = useRef(null);

  useEffect(() => {
    const node = ref.current;
    if (!node || tex == null || tex === '') return undefined;

    node.textContent = inline ? `\\(${tex}\\)` : `\\[${tex}\\]`;

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
  }, [tex, inline]);

  if (tex == null || tex === '') return null;

  return <div ref={ref} className={`mathjax-display ${className}`.trim()} />;
}
