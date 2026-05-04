import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgramsModal from '../../components/ProgramsModal';
import CompareProgramsModal from '../../components/CompareProgramsModal';
import Button from '../../components/Button/Button';
import Navbar from "../../components/Navbar/Navbar";
import "./MainPage.css"

const MainPage = () => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState('');
  const [selectedMainProgramId, setSelectedMainProgramId] = useState('');
  const [selectedCompareProgramIds, setSelectedCompareProgramIds] = useState([]);
  const userId = Number(localStorage.getItem('userId'));

  const domain = process.env.REACT_APP_API_URL_GET_PROGRAMMS || process.env.REACT_APP_API_URL || 'localhost:8000';
  const API_BASE_URL = domain.startsWith('http') ? domain : `http://${domain}`;

  const normalizePrograms = (programItems = []) => programItems.map((programItem, index) => {
    if (programItem && typeof programItem === 'object' && !Array.isArray(programItem)) {
      const universityName = String(programItem.university_name || programItem.universityName || '').trim();
      const programName = String(programItem.program_name || programItem.programName || '').trim();
      const id = `${universityName}::${programName}::${index}`;

      return {
        id,
        universityName,
        programName,
        displayName: universityName ? `${programName} (${universityName})` : programName,
      };
    }

    if (Array.isArray(programItem) && programItem.length >= 2) {
      const universityName = String(programItem[0] || '').trim();
      const programName = String(programItem[1] || '').trim();
      const id = `${universityName}::${programName}::${index}`;

      return {
        id,
        universityName,
        programName,
        displayName: universityName ? `${programName} (${universityName})` : programName,
      };
    }

    const rawValue = String(programItem || '');
    const programName = rawValue.replace(/^frontend\//i, '');
    const id = `frontend::${programName}::${index}`;

    return {
      id,
      universityName: 'frontend',
      programName,
      displayName: programName,
    };
  });

  const applyPrograms = (normalizedPrograms) => {
    setPrograms(normalizedPrograms);

    if (normalizedPrograms.length > 0) {
      setSelectedMainProgramId((current) => {
        if (current && normalizedPrograms.some((program) => program.id === current)) {
          return current;
        }
        return normalizedPrograms[0].id;
      });
    } else {
      setSelectedMainProgramId('');
      setSelectedCompareProgramIds([]);
    }
  };

  const loadPrograms = async () => {
    const response = await fetch(`${API_BASE_URL}/get-programs?userId=${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return normalizePrograms(data.programs || []);
  };

  const fetchPrograms = async () => {
    if (!Number.isInteger(userId) || userId <= 0) {
      alert('Пользователь не авторизован. Войдите заново.');
      return;
    }

    setLoading(true);
    try {
      const normalizedPrograms = await loadPrograms();
      applyPrograms(normalizedPrograms);
      setPrograms(normalizedPrograms);
      setIsOpen(true);
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Не удалось получить программы');
    } finally {
      setLoading(false);
    }
  };

  const handleShowGraph = (program) => {
    const programName = program?.programName;
    const universityName = program?.universityName;

    if (!programName) {
      return;
    }

    setIsOpen(false);

    const params = new URLSearchParams({
      folder: programName,
    });

    if (universityName) {
      params.set('university', universityName);
    }

    navigate(`/graph?${params.toString()}`);
  };

  const handleComparePrograms = async () => {
    if (!Number.isInteger(userId) || userId <= 0) {
      alert('Пользователь не авторизован. Войдите заново.');
      return;
    }

    setCompareLoading(true);
    setCompareError('');

    try {
      const normalizedPrograms = programs.length > 0 ? programs : await loadPrograms();
      applyPrograms(normalizedPrograms);

      if (normalizedPrograms.length === 0) {
        setCompareError('У Вас нет загруженных программ');
        setIsCompareOpen(true);
        return;
      }

      setIsCompareOpen(true);
    } catch (error) {
      console.error('Ошибка:', error);
      setCompareError('Не удалось получить программы для сравнения');
      setIsCompareOpen(true);
    } finally {
      setCompareLoading(false);
    }
  };

  const selectedMainProgram = useMemo(
    () => programs.find((program) => program.id === selectedMainProgramId) || null,
    [programs, selectedMainProgramId]
  );

  const compareCandidates = useMemo(
    () => programs.filter((program) => program.id !== selectedMainProgramId),
    [programs, selectedMainProgramId]
  );

  const handleMainProgramChange = (programId) => {
    setSelectedMainProgramId(programId);
    setSelectedCompareProgramIds((current) => current.filter((compareId) => compareId !== programId));
  };

  const handleToggleCompareProgram = (programId) => {
    setSelectedCompareProgramIds((current) => (
      current.includes(programId)
        ? current.filter((compareId) => compareId !== programId)
        : [...current, programId]
    ));
  };

  const handleCancelCompare = () => {
    setIsCompareOpen(false);
    setCompareError('');
  };

  const handleCompareSubmit = async () => {
    if (!selectedMainProgram) {
      setCompareError('Выберите программу для сравнения');
      return;
    }

    const comparePrograms = programs.filter((program) => selectedCompareProgramIds.includes(program.id));

    if (comparePrograms.length === 0) {
      setCompareError('Выберите хотя бы одну программу для сравнения');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/compare_graphs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: String(userId),
          university_name: selectedMainProgram.universityName,
          program_name: selectedMainProgram.programName,
          compare_programs: comparePrograms.map((program) => ({
            university_name: program.universityName,
            program_name: program.programName,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await response.json();
      setIsCompareOpen(false);
      setCompareError('');
    } catch (error) {
      console.error('Ошибка сравнения программ:', error);
      setCompareError('Не удалось отправить запрос на сравнение программ');
    }
  };

  const handleAddProgram = () => {
    navigate('/work_program');
  };

  const handleManualAdd = () => {
    navigate('/upload_programs');
  };

  return (
    <>
      <Navbar/>
      <main className="main-page-center">
        <Button
          onClick={fetchPrograms}
          width="260px"
          height="43px"
          disabled={loading}
        >
          {loading ? 'Загрузка...' : 'Выберите рабочую программу'}
        </Button>
        <Button
          onClick={handleAddProgram}
          width="260px"
          height="43px"
        >
          Добавить программу
        </Button>
        <Button
            onClick={handleManualAdd}
            width="260px"
            height="43px"
        >
          Добавить свою программу
        </Button>
        <Button
            onClick={handleComparePrograms}
            width="260px"
            height="43px"
            disabled={compareLoading}
        >
          {compareLoading ? 'Загрузка...' : 'Сравнить программы'}
        </Button>
      </main>

      <ProgramsModal 
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        programs={programs}
        onShowGraph={handleShowGraph}
      />

      <CompareProgramsModal
        isOpen={isCompareOpen}
        onClose={handleCancelCompare}
        programs={programs}
        selectedMainProgramId={selectedMainProgramId}
        selectedCompareProgramIds={selectedCompareProgramIds}
        onMainProgramChange={handleMainProgramChange}
        onToggleCompareProgram={handleToggleCompareProgram}
        onCompare={handleCompareSubmit}
        error={compareError}
        canCompare={compareCandidates.length > 0}
      />


    </>
  );
};

export default MainPage;