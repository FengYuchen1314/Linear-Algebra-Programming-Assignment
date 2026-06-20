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
        return imNum >= 0 ? `${imTex}\\mathrm{i}` : `-${imTex}\\mathrm{i}`;
      }
      return `${reTex}${imNum >= 0 ? '+' : '-'}${imTex}\\mathrm{i}`;
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

/** Convert SymPy-style strings to LaTeX. Pass through strings that already contain TeX. */
export function exprToLatex(expr) {
  if (expr == null || expr === '') return '';
  const s = String(expr).trim();
  if (s.includes('\\')) return s;

  let out = s
    .replace(/\*\*/g, '^')
    .replace(/\blambda\b/g, '\\lambda');

  out = out.replace(/\^\(([^)]+)\)/g, '^{$1}');
  out = out.replace(/\^([a-zA-Z_][a-zA-Z0-9_]*|\d+)/g, '^{$1}');
  out = out.replace(/\bsqrt\(([^)]+)\)/g, '\\sqrt{$1}');
  out = out.replace(/\*/g, ' \\cdot ');

  return out;
}

/** Normalize subscripts in identifiers like D_1 -> D_{1}. */
export function subscriptLatex(name) {
  return String(name).replace(/([A-Za-z])_(\d+)/g, '$1_{$2}');
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

export function pickLatex(latex, fallback) {
  if (latex != null && latex !== '') return latex;
  return exprToLatex(fallback);
}
