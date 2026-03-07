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
  return (
    <div className="input-wrapper">
      {icon === 'mail' && <FiMail className="input-icon" />}
      {icon === 'settings' && <FiSettings className="input-icon" />}
      
      <input
        type={type}
        name={name}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        required={required}
        className="custom-input"
      />
    </div>
  );
}

export default Input;