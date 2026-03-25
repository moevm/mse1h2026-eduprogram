import React from 'react';
import { FiMail, FiSettings } from 'react-icons/fi';
import './Input.css';

function Input({ 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  onBlur,
  name,
  required,
  icon 
}) {
  const inputProps = {
    type,
    placeholder,
    value,
    onChange,
    required,
    className: "custom-input"
  };
  
  if (name) inputProps.name = name;
  if (onBlur) inputProps.onBlur = onBlur;
  
  return (
    <div className="input-wrapper">
      {icon === 'mail' && <FiMail className="input-icon" />}
      {icon === 'settings' && <FiSettings className="input-icon" />}
      
      <input {...inputProps} />
    </div>
  );
}

export default Input;