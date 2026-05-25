import { useNavigate } from 'react-router-dom';
import { logout as authLogout } from '../services/api/auth';

export const useLogout = () => {
  const navigate = useNavigate();

  const logout = () => {
    authLogout();
    localStorage.removeItem('compareData');
    navigate('/login');
  };

  return logout;
};
