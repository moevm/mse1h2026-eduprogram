import React from 'react';
import './Modal.css';

const Modal = ({
  isOpen,
  onClose,
  title,
  showClose = true,
  size = 'medium',
  children,
}) => {
  if (!isOpen) return null;

  const handleOverlayClick = () => {
    if (onClose) onClose();
  };

  return (
    <div className="app-modal-overlay" onClick={handleOverlayClick}>
      <div
        className={`app-modal app-modal--${size}`}
        onClick={(e) => e.stopPropagation()}
      >
        {(title || showClose) && (
          <div className="app-modal-header">
            {title ? <h2 className="app-modal-title">{title}</h2> : <span />}
            {showClose && (
              <button
                type="button"
                className="app-modal-close"
                onClick={onClose}
                aria-label="Закрыть"
              >
                ×
              </button>
            )}
          </div>
        )}
        <div className="app-modal-body">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
