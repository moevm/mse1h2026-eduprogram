import React, { useState } from 'react';
import { FiUserPlus, FiMail, FiLock } from 'react-icons/fi';
import { FiUser } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import Button from './Button';
import Input from './Input';
import Card from './Card';
import { register } from '../services/api/auth';
import './RegisterForm.css';

function RegisterForm() {
  const [formData, setFormData] = useState({
    login: '',
    password: '',
  });
  
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  
  const navigate = useNavigate();

  const validateField = (name, value) => {
    switch (name) {
      case 'login':
        if (!value) return 'Логин обязателен';
        if (value.length < 3) return 'Минимум 3 символа';
        return '';
      case 'password':
        if (!value) return 'Пароль обязателен';
        if (value.length < 6) return 'Минимум 6 символов';
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (touched[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: validateField(name, value)
      }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    setErrors(prev => ({
      ...prev,
      [name]: validateField(name, value)
    }));
  };

  const validateForm = () => {
    const newErrors = {
      login: validateField('login', formData.login),
      password: validateField('password', formData.password),
    };
    
    setErrors(newErrors);
    setTouched({ login: true, password: true});
    
    return !Object.values(newErrors).some(error => error);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      const result = await register(formData.login, formData.password);
      
      if (result.status === 201) {
        document.body.innerHTML = '<div></div>';
      } else if (result.status === 401) {
        setServerError('Неправильный логин или пароль');
      } else if (result.status === 409 || result.status === 422) {
        setServerError('Пользователь с таким логином уже существует');
      } else {
        setServerError('Ошибка сервера');
      }
    } catch (err) {
      setServerError('Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const getIcon = (name) => {
    switch(name) {
      case 'login': return 'mail';
      case 'password': 
      default: return undefined;
    }
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
        
        {serverError && (
          <div className="error">{serverError}</div>
        )}
        
        <form onSubmit={handleSubmit}>
          <Input
            type="text"
            name="login"
            placeholder="Email"
            value={formData.login}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            icon={getIcon('login')}
          />
          {touched.login && errors.login && (
            <div className="error" style={{ fontSize: '12px', marginTop: '-5px', marginBottom: '5px' }}>
              {errors.login}
            </div>
          )}

          <Input
            type="password"
            name="password"
            placeholder="Пароль"
            value={formData.password}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            icon={getIcon('password')}
          />
          {touched.password && errors.password && (
            <div className="error" style={{ fontSize: '12px', marginTop: '-5px', marginBottom: '5px' }}>
              {errors.password}
            </div>
          )}

          <Button 
            type="submit"
            color="#000000"
            width="260px"
            height="43px"
            absolute={false}
            disabled={isLoading}
          >
            {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
          </Button>
        </form>

        <div className="login-link" onClick={handleLoginClick}>
          Войти
        </div>
      </Card>
    </div>
  );
}

export default RegisterForm;