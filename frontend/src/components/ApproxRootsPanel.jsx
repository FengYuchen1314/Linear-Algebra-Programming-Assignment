import { motion } from 'framer-motion';
import MathLine from './MathLine';
import { intervalToLatex, numberToLatex } from '../utils/latex';
import { revealItem } from '../motion/presets';

const rootGridVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.05, delayChildren: 0.06 },
  },
};

export default function ApproxRootsPanel({ roots, precision }) {
  if (!roots?.length) {
    return <p className="roots-empty">未找到实根</p>;
  }

  return (
    <div className="approx-roots-panel">
      {precision != null && (
        <motion.div
          className="approx-roots-meta"
          variants={revealItem}
          initial="hidden"
          animate="visible"
        >
          <span className="roots-meta-label">求根精度</span>
          <MathLine inline tex={`\\varepsilon = ${numberToLatex(precision)}`} />
        </motion.div>
      )}
      <motion.div
        className="roots-grid"
        variants={rootGridVariants}
        initial="hidden"
        animate="visible"
      >
        {roots.map((root, i) => (
          <motion.div
            key={i}
            className="root-card"
            variants={revealItem}
          >
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
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
