import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser } from 'react-icons/fi';
import Button from './Button/Button';
import Input from './Input';
import Card from './Card/Card';
import './RegisterForm.css';

import { register, setToken } from '../services/api/auth';

function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    setError('');
    
    if (!email || !password) {
      setError('Заполните все поля');
      return;
    }
    
    const result = await register(email, password);
    
    if (result.success) {
      // сохранение JWT токена в localStorage
      if (result.token) {
        setToken(result.token);
      }
      localStorage.setItem('userLogin', email);
      navigate('/main');
    } else {
      setError(result.error);
    }
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <div className="register-container">
      <Card>
        <div className="register-frame">
          <FiUser className="user-icon" />
        </div>

        <div className="register-text">
          <h2>Регистрация</h2>
          <span>Зарегистрировать аккаунт с помощью электронной почты</span>
        </div>

        {error && <div className="error">{error}</div>}
        
        <Input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          icon="mail"
        />

        <Input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          icon="settings"
        />
        
        <Button 
          type="button"
          color="#000000"
          onClick={handleRegister}
          absolute={false}
        >
          Зарегистрироваться
        </Button>

        <div className="register-link-container" >
          Уже зарегистрированы? <button className="reg-button" onClick={handleLoginClick}>Войти</button>
        </div>
      </Card>
    </div>
  );
}

export default RegisterForm;