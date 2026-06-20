export const DEFAULT_DISPLAY_PRECISION = 0.01;

let globalDisplayPrecision = DEFAULT_DISPLAY_PRECISION;

export function getDisplayPrecision() {
  return globalDisplayPrecision;
}

export function setGlobalDisplayPrecision(value) {
  if (Number.isFinite(value) && value > 0) {
    globalDisplayPrecision = value;
  }
}

/** Decimal places implied by display precision (0.01 → 2). */
export function decimalsFromDisplayPrecision(precision) {
  if (!Number.isFinite(precision) || precision <= 0) {
    return decimalsFromDisplayPrecision(DEFAULT_DISPLAY_PRECISION);
  }
  if (precision >= 1) return 0;
  for (let d = 1; d <= 12; d += 1) {
    const scaled = precision * 10 ** d;
    if (Math.abs(scaled - Math.round(scaled)) < 1e-9) return d;
  }
  return 6;
}

export function roundForDisplay(n, precision = globalDisplayPrecision) {
  const decimals = decimalsFromDisplayPrecision(precision);
  const factor = 10 ** decimals;
  return Math.round(n * factor) / factor;
}

export function isExactDisplayValue(val) {
  if (val === null || val === undefined) return false;
  if (typeof val === 'object') {
    if (val.latex) return true;
    return false;
  }
  if (typeof val === 'number') return Number.isInteger(val);
  if (typeof val === 'string') {
    const s = val.trim();
    if (s.includes('/')) return true;
    if (s.includes('\\')) return true;
    if (/^-?\d+$/.test(s)) return true;
  }
  return false;
}

export function formatNumberForDisplay(val, precision = globalDisplayPrecision) {
  if (isExactDisplayValue(val)) return val;

  if (typeof val === 'object' && ('re' in val || 'im' in val)) {
    return {
      ...val,
      re: formatNumberForDisplay(val.re, precision),
      im: formatNumberForDisplay(val.im, precision),
    };
  }

  const n = typeof val === 'number' ? val : Number(val);
  if (!Number.isFinite(n)) return String(val);

  const rounded = roundForDisplay(n, precision);
  if (Number.isInteger(rounded)) return String(rounded);

  const decimals = decimalsFromDisplayPrecision(precision);
  return rounded.toFixed(decimals).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');
}

/** True when LaTeX represents an exact symbolic value (sqrt, frac, etc.). */
export function isExactLatex(latex) {
  if (latex == null || latex === '') return false;
  const s = String(latex);
  if (s.includes('\\sqrt') || s.includes('\\frac') || s.includes('\\operatorname')) return true;
  if (/\\[a-zA-Z]+/.test(s)) return true;
  return false;
}

/** Round decimal literals embedded in a LaTeX string (e.g. matrix entries in steps). */
export function applyDisplayPrecisionToLatex(tex, precision = globalDisplayPrecision) {
  if (!tex || typeof tex !== 'string') return tex;
  return tex.replace(/(?<![\d.])-?\d+\.\d+(?:[eE][+-]?\d+)?/g, (match) =>
    formatNumberForDisplay(Number(match), precision),
  );
}

/** Pick eigenvalue LaTeX: exact forms unchanged, floats respect display precision. */
export function displayEigenvalueLatex(ev) {
  const value = ev?.eigenvalue;
  if (typeof value === 'object' && value?.latex) return value.latex;

  const latex = ev?.eigenvalue_latex;
  if (latex && isExactLatex(latex)) return latex;

  if (value != null && value !== '') return formatNumberForDisplay(value, globalDisplayPrecision);
  if (latex != null && latex !== '') {
    return isExactLatex(latex) ? latex : formatNumberForDisplay(latex, globalDisplayPrecision);
  }
  return '';
}
