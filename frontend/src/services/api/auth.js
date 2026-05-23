
const domain = process.env.REACT_APP_API_URL || 'localhost:8000';
const API_BASE_URL = domain.startsWith('http') ? domain : `http://${domain}`;

export const login = async (login, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ login, password })
    });

    const body = await response.json().catch(() => ({}));

    if (response.status === 200) {
      return { success: true, token: body.token, id: body.id };
    }
    
    if (response.status === 401) {
      return { success: false, error: 'Неправильный логин или пароль' };
    }
    
    if (response.status === 409) {
      return { success: false, error: 'Конфликт данных' };
    }
    
    if (response.status === 500) {
      return { success: false, error: 'Внутренняя ошибка сервера' };
    }
    
    return { success: false, error: 'Ошибка сервера' };
    
  } catch (err) {
    return { success: false, error: 'Ошибка соединения' };
  }
};

export const register = async (login, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/registration`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ login, password })
    });

    const body = await response.json().catch(() => ({}));

    if (response.status === 201) {
      return { success: true, token: body.token, id: body.id };
    }
    
    if (response.status === 401) {
      return { success: false, error: 'Неправильный логин или пароль' };
    }
    
    if (response.status === 409 || response.status === 422) {
      return { success: false, error: 'Пользователь с таким логином уже существует' };
    }
    
    if (response.status === 500) {
      return { success: false, error: 'Внутренняя ошибка сервера' };
    }
    
    return { success: false, error: 'Ошибка сервера' };
    
  } catch (err) {
    return { success: false, error: 'Ошибка соединения' };
  }
};

/**
 * получение JWT токена из localStorage
 * @returns {string|null} JWT токен или null
 */
export const getToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * сохранение JWT токена в localStorage
 * @param {string} token - JWT токен
 */
export const setToken = (token) => {
  localStorage.setItem('authToken', token);
};

/**
 * удаление JWT токена из localStorage
 */
export const removeToken = () => {
  localStorage.removeItem('authToken');
};

/**
 * проверка авторизации пользователя по наличию JWT токена
 * @returns {boolean} true если токен присутствует
 */
export const isAuthenticated = () => {
  return !!getToken();
};

/**
 * разлогинивание пользователя 
 */
export const logout = () => {
  removeToken();
  localStorage.removeItem('userLogin');
};