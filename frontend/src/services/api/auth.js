const domen = 'localhost:80';

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
    } else if (response.status === 401) {
      return { success: false, error: 'Неправильный логин или пароль' };
    } else {
      return { success: false, error: 'Ошибка сервера' };
    }
  } catch (err) {
    return { success: false, error: 'Ошибка соединения' };
  }
};