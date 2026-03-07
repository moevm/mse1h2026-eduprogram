import React from 'react';
import './Button.css';

function Button({ 
  children, 
  color, 
  onClick, 
  type = 'button', 
  absolute = false,
  width,
  height,
  className = ''
}) {
  const buttonStyle = {
    backgroundColor: color,
    position: absolute ? 'absolute' : 'relative',
    width: width || (absolute ? '260px' : 'auto'),
    height: height || (absolute ? '43px' : 'auto'),
    top: absolute ? '346.09px' : 'auto',
    left: absolute ? '50px' : 'auto'
  };

  return (
    <button 
      className={`custom-button ${className}`}
      style={buttonStyle}
      onClick={onClick}
      type={type}
    >
      {children}
    </button>
  );
}

export default Button;