import { getAccessToken, refreshTokens, removeTokens } from './auth';

/**
 * Добавление JWT токена в заголовок Authorization
 * @param {Object} headers - Объект заголовков
 * @returns {Object} Обновленные заголовки с токеном
 */
export const withAuthHeader = (headers = {}) => {
  const token = getAccessToken();
  if (token) {
    return {
      ...headers,
      'Authorization': `Bearer ${token}`,
    };
  }
  return headers;
};

/**
 * fetch запрос с авторизацией и автоматическим обновлением токена
 * @param {string} url - URL запроса
 * @param {Object} options - Опции fetch
 * @returns {Promise<Response>} Ответ сервера
 */
export const fetchWithAuth = async (url, options = {}) => {
  let response = await fetch(url, {
    ...options,
    headers: withAuthHeader(options.headers),
  });

  // попытка обновить токен при 401 (Unauthorized)
  if (response.status === 401) {
    const refreshResult = await refreshTokens();
    if (refreshResult.success) {
      response = await fetch(url, {
        ...options,
        headers: withAuthHeader(options.headers),
      });
    } else {
      removeTokens();
    }
  }

  return response;
};
