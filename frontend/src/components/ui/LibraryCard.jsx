import { motion, useReducedMotion } from 'framer-motion';
import { cardHover, cardTap } from '../../motion/presets';

export default function LibraryCard({
  selected = false,
  onSelect,
  children,
  className = '',
}) {
  const reduceMotion = useReducedMotion();

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect();
    }
  };

  return (
    <motion.div
      role="button"
      tabIndex={0}
      className={`library-card${selected ? ' selected' : ''}${className ? ` ${className}` : ''}`}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
      whileHover={cardHover(reduceMotion)}
      whileTap={cardTap(reduceMotion)}
      layout
    >
      {children}
    </motion.div>
  );
}
