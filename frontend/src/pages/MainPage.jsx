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
      alert('Не удалось получить программы');
    } finally {
      setLoading(false);
    }
  };

  const handleShowGraph = async (program) => {
    const response = await fetch(`http://${domain}/show-graph?name=${program}`);
    if (response.status == 200){
      console.log('Рисуется граф', program);
    }
  };

  return (
    <>
        <Button
          className="custom-button-margin"
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


    </>
  );
};

export default MainPage;