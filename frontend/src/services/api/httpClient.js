import { getToken } from './auth';

/**
 * Добавление JWT токена в заголовок Authorization
 * @param {Object} headers - Объект заголовков
 * @returns {Object} Обновленные заголовки с токеном
 */
export const withAuthHeader = (headers = {}) => {
  const token = getToken();
  if (token) {
    return {
      ...headers,
      'Authorization': `Bearer ${token}`,
    };
  }
  return headers;
};

/**
 * fetch запрос с авторизацией
 * @param {string} url - URL запроса
 * @param {Object} options - Опции fetch
 * @returns {Promise<Response>} Ответ сервера
 */
export const fetchWithAuth = (url, options = {}) => {
  return fetch(url, {
    ...options,
    headers: withAuthHeader(options.headers),
  });
};
