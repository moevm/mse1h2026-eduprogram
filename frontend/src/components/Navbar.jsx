import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Button from './Button';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <div className="logo-placeholder"></div>
      </div>
      
      <div className="navbar-buttons">
        <Button 
          color="#000000"
          onClick={() => navigate('/login')}
          absolute={false}
          width="99px"
          height="43px"
        >
          Вход
        </Button>
        
        <Button 
          color="#000000"
          onClick={() => navigate('/register')}
          absolute={false}
          width="162px"
          height="43px"
        >
          Регистрация
        </Button>
      </div>
    </nav>
  );
}

export default Navbar;