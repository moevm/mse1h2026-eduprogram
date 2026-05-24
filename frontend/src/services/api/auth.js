
const domain = process.env.REACT_APP_API_URL || 'localhost:8000';
const API_BASE_URL = domain.startsWith('http') ? domain : `http://${domain}`;

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

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
      if (body.access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, body.access_token);
      }
      if (body.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, body.refresh_token);
      }
      return { success: true, access_token: body.access_token, refresh_token: body.refresh_token, id: body.id };
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
      if (body.access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, body.access_token);
      }
      if (body.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, body.refresh_token);
      }
      return { success: true, access_token: body.access_token, refresh_token: body.refresh_token, id: body.id };
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
 * Получение access-токена из localStorage
 * @returns {string|null} Access-токен или null
 */
export const getAccessToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Получение refresh-токена из localStorage
 * @returns {string|null} 
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Получение access-токена из localStorage 
 * @returns {string|null} Access-токен или null
 */
export const getToken = () => {
  return getAccessToken();
};

/**
 * Сохранение обоих токенов
 * @param {string} accessToken - Access-токен
 * @param {string} refreshToken - Refresh-токен
 */
export const setTokens = (accessToken, refreshToken) => {
  if (accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  }
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};

/**
 * Сохранение access-токена в localStorage 
 * @param {string} token - Access-токен
 */
export const setToken = (token) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
};

/**
 * Удаление всех токенов из localStorage
 */
export const removeTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Удаление access-токена из localStorage 
 */
export const removeToken = () => {
  removeTokens();
};

/**
 * Проверка авторизации пользователя по наличию access-токена
 * @returns {boolean} true если токен присутствует
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

/**
 * Обновление токенов с использованием refresh-токена
 */
export const refreshTokens = async () => {
  try {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      return { success: false, error: 'No refresh token available' };
    }

    const response = await fetch(`${API_BASE_URL}/refresh-tokens`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    const body = await response.json().catch(() => ({}));

    if (response.status === 200) {
      if (body.access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, body.access_token);
      }
      if (body.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, body.refresh_token);
      }
      return { success: true, access_token: body.access_token, refresh_token: body.refresh_token };
    }

    if (response.status === 401) {
      removeTokens();
      return { success: false, error: 'Session expired, please login again' };
    }

    return { success: false, error: 'Failed to refresh tokens' };
  } catch (err) {
    return { success: false, error: 'Error refreshing tokens' };
  }
};

/**
 * Разлогинивание пользователя с отзывом refresh-токена
 */
export const logout = async () => {
  try {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      }).catch(() => {});
    }
  } catch (err) {
    console.error('Error during logout:', err);
  } finally {
    removeTokens();
    localStorage.removeItem('userLogin');
  }
};