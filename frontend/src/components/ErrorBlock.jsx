import { motion } from 'framer-motion';
import { IconAlert } from './ui/Icons';
import { revealItem } from '../motion/presets';

export default function ErrorBlock({ errors }) {
  if (!errors?.length) return null;
  return (
    <motion.div
      className="error-block alert--error"
      variants={revealItem}
      initial="hidden"
      animate="visible"
    >
      <span className="alert-icon"><IconAlert /></span>
      <div className="alert-content">
        {errors.map((e, i) => (
          <p key={i}>{e}</p>
        ))}
      </div>
    </motion.div>
  );
}

export function WarningBlock({ warnings }) {
  if (!warnings?.length) return null;
  return (
    <motion.div
      className="warning-block alert--warning"
      variants={revealItem}
      initial="hidden"
      animate="visible"
    >
      <span className="alert-icon"><IconAlert /></span>
      <div className="alert-content">
        {warnings.map((w, i) => (
          <p key={i}>{w}</p>
        ))}
      </div>
    </motion.div>
  );
}
