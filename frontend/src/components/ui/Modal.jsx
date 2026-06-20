import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { IconClose } from './Icons';

export default function Modal({ open, onClose, title, children, size = 'lg' }) {
  const dialogRef = useRef(null);

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

  if (!open) return null;

  return createPortal(
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <div
        ref={dialogRef}
        className={`modal modal--${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal__header">
          <h2 id="modal-title" className="text-h3">{title}</h2>
          <button
            type="button"
            className="icon-btn modal__close"
            onClick={onClose}
            aria-label="关闭"
          >
            <IconClose />
          </button>
        </header>
        <div className="modal__body">{children}</div>
      </div>
    </div>,
    document.body,
  );
}
