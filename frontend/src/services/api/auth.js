
const domen = process.env.REACT_APP_API_URL;

export const login = async (email, password) => {
  try {
    const response = await fetch(`http://${domen}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    if (response.status === 200) {
      return { success: true };
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