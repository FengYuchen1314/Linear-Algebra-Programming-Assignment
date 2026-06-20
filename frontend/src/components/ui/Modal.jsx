import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { modalBackdrop, modalPanel, pressableHover, pressableTap } from '../../motion/presets';
import { IconClose } from './Icons';

export default function Modal({ open, onClose, title, children, size = 'lg' }) {
  const dialogRef = useRef(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (!open) return undefined;

    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', onKeyDown);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  return createPortal(
    <AnimatePresence mode="wait">
      {open && (
        <motion.div
          className="modal-overlay"
          role="presentation"
          onClick={onClose}
          variants={modalBackdrop}
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          <motion.div
            ref={dialogRef}
            className={`modal modal--${size}`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            onClick={(e) => e.stopPropagation()}
            variants={modalPanel}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <header className="modal__header">
              <h2 id="modal-title" className="text-h3">{title}</h2>
              <motion.button
                type="button"
                className="icon-btn modal__close"
                onClick={onClose}
                aria-label="关闭"
                whileHover={pressableHover(reduceMotion)}
                whileTap={pressableTap(reduceMotion)}
              >
                <IconClose />
              </motion.button>
            </header>
            <div className="modal__body">{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  );
}
