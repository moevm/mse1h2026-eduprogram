import React, { useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgramsModal from '../../components/ProgramsModal';
import CompareProgramsModal from '../../components/CompareProgramsModal';
import HistoryModal from '../../components/HistoryModal';
import Button from '../../components/UI/Button/Button';
import Navbar from "../../components/Navbar/Navbar";
import TreeEditor from '../../components/TreeEditor';
import UploadProgram from '../../components/UploadProgram';
import { useNotification } from '../../components/UI/Notification/Notification';
import "./MainPage.css"
import { fetchWithAuth } from '../../services/api/httpClient';

const MainPage = () => {
  const navigate = useNavigate();
  const notify = useNotification();
  const [isOpen, setIsOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareSubmitting, setCompareSubmitting] = useState(false);
  const [compareError, setCompareError] = useState('');
  const [selectedMainProgramId, setSelectedMainProgramId] = useState('');
  const [selectedCompareProgramIds, setSelectedCompareProgramIds] = useState([]);
  const compareSubmitLockRef = useRef(false);

  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);



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
    const response = await fetchWithAuth(`${API_BASE_URL}/get-programs`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    return normalizePrograms(data.programs || []);
  };

  const fetchPrograms = async () => {
    setLoading(true);
    try {
      const normalizedPrograms = await loadPrograms();
      applyPrograms(normalizedPrograms);
      setPrograms(normalizedPrograms);
      setIsOpen(true);
    } catch (error) {
      console.error('Ошибка:', error);
      notify('Не удалось получить программы', { type: 'error' });
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
    if (compareSubmitLockRef.current) {
      return;
    }

    if (!selectedMainProgram) {
      setCompareError('Выберите программу для сравнения');
      return;
    }

    const comparePrograms = programs.filter((program) => selectedCompareProgramIds.includes(program.id));

    if (comparePrograms.length === 0) {
      setCompareError('Выберите хотя бы одну программу для сравнения');
      return;
    }

    compareSubmitLockRef.current = true;
    setCompareSubmitting(true);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/compare_graphs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
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
      const data = await response.json();
      localStorage.setItem('graph_id', data.graphId)
      delete data.graphId;
      const jsonData = JSON.stringify(data);
      localStorage.setItem('compareData', jsonData);
      setIsCompareOpen(false);
      setCompareError('');

      navigate('/compare');
    } catch (error) {
      console.error('Ошибка сравнения программ:', error);
      setCompareError('Не удалось отправить запрос на сравнение программ');
    } finally {
      compareSubmitLockRef.current = false;
      setCompareSubmitting(false);
    }
  };

  const fetchShowHistory = async () => {
    setHistoryLoading(true);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/get-history`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const comparedPrograms = data["compared-programs"] || [];

      setHistoryData(comparedPrograms);
      setIsHistoryOpen(true);

    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
      notify('Не удалось загрузить историю сравнений', { type: 'error' });
    } finally {
      setHistoryLoading(false);
    }
  };



  const fetchHistoryGraph = async (hash) => {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/get-history-graph?hash=${hash}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      localStorage.setItem('compareData', JSON.stringify(data));

      navigate('/compare');

      return data;
    } catch (error) {
      console.error('Ошибка загрузки результата сравнения:', error);
      notify('Не удалось загрузить результат сравнения', { type: 'error' });
      throw error;
    }
  };


  // Обработчик выбора элемента из истории
  const handleViewHistoryResult = async (historyItem) => {
    // Закрываем модальное окно истории
    setIsHistoryOpen(false);

    // Загружаем данные графа по hash
    await fetchHistoryGraph(historyItem.hash);
  };
  
  const handleAddProgram = () => {
    setIsEditorOpen(true);
  };

  const handleManualAdd = () => {
    setIsUploadOpen(true);
  };

  return (
    <>

      <Navbar showAuthButtons={false} showLogoutButton={true} />
      <main className="main-page">
        <header className="main-hero">
          <h1 className="main-title">Образовательные программы</h1>
        </header>

        <div className="main-grid ">
          <section className="main-card">
            <div className="main-card-header">
              <h2 className="main-card-title">Сравнение</h2>
              <span className="main-card-hint">Сопоставьте две и более программ</span>
            </div>
            <div className="main-card-actions">
              <Button onClick={handleComparePrograms} disabled={compareLoading}>
                {compareLoading ? 'Загрузка...' : 'Сравнить программы'}
              </Button>
              <Button onClick={fetchShowHistory} disabled={compareLoading}>
                {compareLoading ? 'Загрузка...' : 'История сравнения'}
              </Button>
            </div>
          </section>

          <section className="main-card">
            <div className="main-card-header">
              <h2 className="main-card-title">Добавление</h2>
              <span className="main-card-hint">Создайте или загрузите программу</span>
            </div>
            <div className="main-card-actions">
              <Button onClick={handleAddProgram}>
                Добавить программу
              </Button>
              <Button onClick={handleManualAdd}>
                Добавить свою программу
              </Button>
            </div>
          </section>
        </div>

        <section className="main-card">
            <div className="main-card-header">
              <h2 className="main-card-title">Просмотр</h2>
              <span className="main-card-hint">Ваши программы и история</span>
            </div>
            <div className="main-card-actions">
              <Button onClick={fetchPrograms} disabled={loading}>
                {loading ? 'Загрузка...' : 'Выберите рабочую программу'}
              </Button>
            </div>
          </section>
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
        isSubmitting={compareSubmitting}
      />
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        historyData={historyData}
        onViewResult={handleViewHistoryResult}
      />

      <TreeEditor
        isOpen={isEditorOpen}
        onClose={() => setIsEditorOpen(false)}
      />
      <UploadProgram
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />
    </>
  );
};

export default MainPage;