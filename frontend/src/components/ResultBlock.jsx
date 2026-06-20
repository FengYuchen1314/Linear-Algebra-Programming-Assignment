import { motion } from 'framer-motion';
import MathJaxDisplay from './MathJax';
import { IconCheck } from './ui/Icons';
import { revealItem } from '../motion/presets';

export default function ResultBlock({ title, children, latex }) {
  return (
    <motion.article
      className="card result-block"
      variants={revealItem}
      initial="hidden"
      animate="visible"
    >
      {title && (
        <header className="result-block-header">
          <h3 className="text-h4">{title}</h3>
        </header>
      )}
      <div className="result-content">{children}</div>
      {latex && (
        <div className="latex-block">
          <MathJaxDisplay tex={latex} />
        </div>
      )}
    </motion.article>
  );
}

export function SelectedBanner({ children }) {
  return (
    <motion.div
      className="banner banner--success selected-info"
      variants={revealItem}
      initial="hidden"
      animate="visible"
    >
      <strong className="banner__label">
        <IconCheck aria-hidden />
        已选择
      </strong>
      {children}
    </motion.div>
  );
}
