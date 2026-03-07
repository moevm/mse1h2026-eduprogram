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

export const register = async (login, password) => {
  try {
    const response = await fetch(`http://${domen}/sign-up`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ login, password })
    });

    if (response.status === 201) {
      return { 
        success: true,
        status: 201 
      };
    } else if (response.status === 401) {
      return { 
        success: false, 
        error: 'Неправильный логин или пароль',
        status: 401 
      };
    } else if (response.status === 409 || response.status === 422) {
      return { 
        success: false, 
        error: 'Пользователь с таким логином уже существует',
        status: response.status 
      };
    } else {
      return { 
        success: false, 
        error: 'Ошибка сервера',
        status: response.status 
      };
    }
  } catch (err) {
    return { 
      success: false, 
      error: 'Ошибка соединения',
      status: 0 
    };
  }
};