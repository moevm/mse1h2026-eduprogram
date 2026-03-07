import React from 'react';
import { FiMail, FiSettings } from 'react-icons/fi';
import './Input.css';

function Input({ 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  required,
  icon 
}) {
  return (
    <div className="input-wrapper">
      {icon === 'mail' && <FiMail className="input-icon" />}
      {icon === 'settings' && <FiSettings className="input-icon" />}
      
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        className="custom-input"
      />
    </div>
  );
}

export default Input;