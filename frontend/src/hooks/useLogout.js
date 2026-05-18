import { useNavigate } from 'react-router-dom';

export const useLogout = () => {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('userLogin');
    localStorage.removeItem('compareData');
    navigate('/login');
  };

  return logout;
};
