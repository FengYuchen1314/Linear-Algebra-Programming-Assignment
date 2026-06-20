import { AnimatePresence, motion } from 'framer-motion';
import { fadeUp, revealItem, staggerResults } from '../../motion/presets';

export default function PageLayout({ title, description, children }) {
  return (
    <div className="page">
      <header className="page-hero">
        <h1 className="text-h1 page-title">{title}</h1>
        {description && <p className="page-description text-body-lg">{description}</p>}
      </header>
      <div className="page-body">{children}</div>
    </div>
  );
}

export function WorkflowSection({ children }) {
  return (
    <motion.section
      className="workflow-section workflow-zone"
      variants={fadeUp}
      initial="hidden"
      animate="visible"
      transition={{ ...fadeUp.visible.transition, delay: 0.06 }}
    >
      <div className="zone-header zone-header--input">
        <span className="zone-badge zone-badge--input">输入</span>
        <span className="zone-header__hint text-muted">选择数据并配置参数</span>
      </div>
      <div className="workflow-zone__content">{children}</div>
    </motion.section>
  );
}

export function ActionPanel({ title = '分析参数', children }) {
  return (
    <motion.div
      className="card action-panel"
      variants={revealItem}
      initial="hidden"
      animate="visible"
      transition={{ ...revealItem.visible.transition, delay: 0.1 }}
    >
      <h3 className="text-h4 action-panel-title">{title}</h3>
      <div className="action-panel-body">{children}</div>
    </motion.div>
  );
}

export function ResultsSection({ children, placeholder = '选择输入并点击分析后，结果将显示在此处。' }) {
  const hasContent = children != null && children !== false;

  return (
    <section className="results-section results-zone">
      <div className="zone-header zone-header--output">
        <h2 className="text-h2 results-section-title">分析结果</h2>
        <span className="zone-badge zone-badge--output">输出</span>
      </div>
      <div className="results-zone__content">
        <AnimatePresence mode="wait">
          {hasContent ? (
            <motion.div
              key="results"
              className="results"
              variants={staggerResults}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, transition: { duration: 0.18 } }}
            >
              {children}
            </motion.div>
          ) : (
            <motion.p
              key="empty"
              className="results-empty text-muted"
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              {placeholder}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
