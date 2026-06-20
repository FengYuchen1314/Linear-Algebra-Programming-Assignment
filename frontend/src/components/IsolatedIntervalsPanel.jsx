import MathLine from './MathLine';
import { intervalToLatex } from '../utils/latex';

export default function IsolatedIntervalsPanel({ intervals }) {
  if (!intervals?.length) {
    return <p className="roots-empty">未找到实根区间</p>;
  }

  return (
    <div className="intervals-grid">
      {intervals.map((interval, i) => (
        <div key={i} className="interval-chip">
          <span className="interval-chip-index">#{i + 1}</span>
          <MathLine tex={intervalToLatex(interval[0], interval[1])} />
        </div>
      ))}
    </div>
  );
}
