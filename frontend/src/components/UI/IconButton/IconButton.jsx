import React from 'react';
import './IconButton.css';

const IconButton = ({
  icon,
  alt = '',
  children,
  onClick,
  type = 'button',
  disabled = false,
  className = '',
  title,
}) => {
  const hasIcon = Boolean(icon);

  const renderIcon = () => {
    if (typeof icon === 'string') {
      return <img src={icon} alt={alt} className="icon-button__icon" />;
    }
    return <span className="icon-button__icon">{icon}</span>;
  };

  return (
    <button
      type={type}
      className={`icon-button ${hasIcon ? 'icon-button--icon' : 'icon-button--text'} ${className}`}
      onClick={onClick}
      disabled={disabled}
      title={title}
      aria-label={hasIcon ? (alt || title) : undefined}
    >
      {hasIcon ? renderIcon() : <span className="icon-button__label">{children}</span>}
    </button>
  );
};

export default IconButton;
