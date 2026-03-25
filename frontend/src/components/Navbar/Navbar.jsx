import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../Button/Button';
import './Navbar.css';

export default function Navbar() {
  const navigate = useNavigate();
  
  return (
    <nav className="navbar">
      <div className="navbar-logo">
      </div>
      
      <div className="navbar-buttons">
        <Button onClick={() => navigate('/login')}>
          Вход
        </Button>
        
        <Button onClick={() => navigate('/register')}>
          Регистрация
        </Button>
      </div>
    </nav>
  );
}