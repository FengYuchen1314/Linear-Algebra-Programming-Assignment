export function formatCell(val) {
  if (val === null || val === undefined) return '0';
  return numberToLatex(val);
}

export function numberToLatex(val) {
  if (val === null || val === undefined) return '0';
  if (typeof val === 'object') {
    if (val.latex) return val.latex;
    if ('re' in val || 'im' in val) {
      const re = val.re ?? 0;
      const im = val.im ?? 0;
      const reTex = numberToLatex(re);
      const imNum = parseNumber(im);
      if (Math.abs(imNum) < 1e-10) return reTex;
      const imTex = numberToLatex(Math.abs(imNum));
      if (Math.abs(parseNumber(re)) < 1e-10) {
        return imNum >= 0 ? `${imTex}i` : `-${imTex}i`;
      }
      return `${reTex}${imNum >= 0 ? '+' : '-'}${imTex}i`;
    }
  }
  if (typeof val === 'string' && val.includes('/')) {
    const [p, q] = val.split('/');
    return q ? `\\frac{${p}}{${q}}` : val;
  }
  return String(val);
}

export function parseNumber(val) {
  if (typeof val === 'number') return val;
  if (typeof val === 'string' && val.includes('/')) {
    const [p, q] = val.split('/').map(Number);
    return p / q;
  }
  return Number(val);
}

export function exprToLatex(expr) {
  if (expr == null || expr === '') return '';
  const s = String(expr);
  if (s.includes('\\')) return s;
  return s
    .replace(/\*\*/g, '^')
    .replace(/\blambda\b/g, '\\lambda')
    .replace(/\^(\w+)/g, (_, p) => `^{${p}}`)
    .replace(/\*/g, ' \\cdot ');
}

export function matrixToLatex(matrix) {
  if (!matrix?.length) return '';
  const rows = matrix
    .map((row) => row.map(formatCell).join(' & '))
    .join(' \\\\ ');
  return `\\begin{bmatrix}${rows}\\end{bmatrix}`;
}

export function labeledMatrix(label, matrix) {
  const body = matrixToLatex(matrix);
  return label ? `${label} = ${body}` : body;
}

export function intervalToLatex(a, b) {
  return `\\left[${numberToLatex(a)},\\ ${numberToLatex(b)}\\right]`;
}

export function eigenvalueLineLatex(ev) {
  const lam = ev.eigenvalue_latex || numberToLatex(ev.eigenvalue);
  return `\\lambda = ${lam},\\ n_a = ${ev.algebraic_multiplicity},\\ n_g = ${ev.geometric_multiplicity}`;
}

export function rootApproxLatex(root) {
  return `${intervalToLatex(root.interval[0], root.interval[1])} \\Rightarrow x \\approx ${numberToLatex(root.approx_root)}\\ (\\varepsilon=${root.precision})`;
}

export function valueToLatex(label, value, suffix = '') {
  const body = typeof value === 'string' && value.includes('\\') ? value : numberToLatex(value);
  return `${label} = ${body}${suffix}`;
}
