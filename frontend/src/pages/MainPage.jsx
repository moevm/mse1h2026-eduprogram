import { useState } from 'react';
import ProgramsModal from '../components/ProgramsModal';
import Button from '../components/Button';

const MainPage = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);

  const domain = process.env.REACT_APP_API_URL_GET_PROGRAMMS;

  const fetchPrograms = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://${domain}/get-programs`);
      const data = await response.json();
      setPrograms(data.programs);
      setIsOpen(true);
    } catch (error) {
      console.error('Ошибка:', error);
      // Для теста
      setPrograms(["program 1", "program2"]);
      setIsOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleShowGraph = (program) => {
    console.log('Показать граф для:', program);
    // логика показа графа
  };

  return (
    <>
        <Button 
          className="custom-button"
          type="button"
          color="#000000"
          onClick={fetchPrograms}
          width="260px"
          height="43px"
          absolute={false}
          disabled={loading}
        >
            {loading ? 'Загрузка...' : 'Показать граф'}
        </Button>

      <ProgramsModal 
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        programs={programs}
        onShowGraph={handleShowGraph}
      />

      <style>{`
        .custom-button {
            margin-top: 90px;
            margin-left: 10px;
        }
      `}</style>
    </>
  );
};

export default MainPage;