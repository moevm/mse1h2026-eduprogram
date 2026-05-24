import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../services/api/auth';

/**
 * Компонент для защиты маршрутов (ProtectedRoute).
 * Перенаправление на login, если юзер не авторизован.
 * 
 * @param {Object} props - Свойства компонента
 * @param {React.ReactNode} props.children - Элемент для отображения если авторизован
 * @returns {React.ReactNode}
 */
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
