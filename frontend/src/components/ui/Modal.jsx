import { useEffect, useRef } from 'react';
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

  return (
    <div className="md-dialog__scrim" role="presentation" onClick={onClose}>
      <div
        ref={dialogRef}
        className={`md-dialog md-dialog--${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="md-dialog__header">
          <h2 id="modal-title" className="md-headline-small">{title}</h2>
          <button
            type="button"
            className="md-icon-button md-state-layer md-dialog__close"
            onClick={onClose}
            aria-label="关闭"
          >
            <IconClose />
          </button>
        </header>
        <div className="md-dialog__content">{children}</div>
      </div>
    </div>
  );
}
