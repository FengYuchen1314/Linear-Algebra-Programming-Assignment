import MathLine from './MathLine';
import { intervalToLatex, numberToLatex } from '../utils/latex';

export default function ApproxRootsPanel({ roots, precision }) {
  if (!roots?.length) {
    return <p className="roots-empty">未找到实根</p>;
  }

  return (
    <div className="approx-roots-panel">
      {precision != null && (
        <div className="approx-roots-meta">
          <span className="roots-meta-label">求根精度</span>
          <MathLine inline tex={`\\varepsilon = ${numberToLatex(precision)}`} />
        </div>
      )}
      <div className="roots-grid">
        {roots.map((root, i) => (
          <div key={i} className="root-card">
            <div className="root-card-index">#{i + 1}</div>
            <div className="root-card-section">
              <span className="root-card-label">隔离区间</span>
              <div className="root-card-value">
                <MathLine tex={intervalToLatex(root.interval[0], root.interval[1])} />
              </div>
            </div>
            <div className="root-card-divider" aria-hidden />
            <div className="root-card-section root-card-section--highlight">
              <span className="root-card-label">近似根</span>
              <div className="root-card-value root-card-value--primary">
                <MathLine tex={`x \\approx ${numberToLatex(root.approx_root)}`} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
