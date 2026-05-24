import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../UI/Button/Button';
import { useLogout } from '../../hooks/useLogout';
import './Navbar.css';

export default function Navbar({ showAuthButtons = true, showLogoutButton = false, onLogout }) {
  const navigate = useNavigate();
  const defaultLogout = useLogout();

  const handleLogout = () => {
    if (typeof onLogout === 'function') {
      onLogout();
      return;
    }
    defaultLogout();
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
      </div>

      {(showAuthButtons || showLogoutButton) ? (
        <div className="navbar-buttons">
          {showAuthButtons ? (
            <Button onClick={() => navigate('/login')}>
              Вход
            </Button>
          ) : null}

          {showAuthButtons ? (
            <Button onClick={() => navigate('/register')}>
              Регистрация
            </Button>
          ) : null}

          {showLogoutButton ? (
            <Button className="navbar-logout-button" onClick={handleLogout}>
              Выйти
            </Button>
          ) : null}
        </div>
      ) : null}
    </nav>
  );
}
