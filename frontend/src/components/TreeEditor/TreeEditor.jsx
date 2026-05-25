import React, { useState } from 'react';
import TreeNode from './TreeNode';
import EmptyState from './EmptyState';
import TreeActions from './TreeActions';
import JsonViewer from './JsonViewer';
import Modal from '../UI/Modal/Modal';
import Input from '../UI/Input/Input';
import { useNotification } from '../UI/Notification/Notification';
import { generateId, convertToBackendFormat, submitProgram } from './utils';
import './TreeEditor.css';

const TreeEditor = ({ isOpen, onClose }) => {
  const notify = useNotification();
  const [programName, setProgramName] = useState('');
  const [universityName, setUniversityName] = useState('');

  const [disciplines, setDisciplines] = useState([
    {
      id: generateId(),
      name: '',
      type: 'discipline',
      previousDisciplines: [],
      children: []
    }
  ]);

  const [showJson, setShowJson] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleAddDiscipline = () => {
    setDisciplines([
      ...disciplines,
      {
        id: generateId(),
        name: '',
        type: 'discipline',
        previousDisciplines: [],
        children: []
      }
    ]);
  };

  const handleDisciplineUpdate = (index, updated) => {
    if (updated === null) {
      setDisciplines(disciplines.filter((_, i) => i !== index));
    } else {
      const copy = [...disciplines];
      copy[index] = updated;
      setDisciplines(copy);
    }
  };

  const handleToggleJson = () => {
    setShowJson(!showJson);
  };

  const handleSubmitProgram = async () => {
    setSubmitting(true);
    try {
      const result = await submitProgram(programName, universityName, disciplines);
      if (result.success) {
        notify('Рабочая программа успешно добавлена', { type: 'success' });
        onClose();
        return;
      }
      notify(result.error || 'Ошибка отправки программы', { type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Редактор учебной программы"
      showClose
      size="large"
    >
      <div className="tree-editor-container">
        <Input
          type="text"
          placeholder="Название университета"
          icon="settings"
          value={universityName}
          onChange={(e) => setUniversityName(e.target.value)}
        />
        <Input
          type="text"
          placeholder="Название образовательной программы"
          icon="settings"
          value={programName}
          onChange={(e) => setProgramName(e.target.value)}
        />

        <p className="subtitle">
          Дисциплины → Темы → Подтемы
        </p>

        <div className="tree-root">
          {disciplines.length === 0
            ? <EmptyState />
            : disciplines.map((discipline, index) => (
                <TreeNode
                  key={discipline.id}
                  node={discipline}
                  level={0}
                  onAddSibling={() => {
                    const newNode = {
                      id: generateId(),
                      name: '',
                      type: 'discipline',
                      previousDisciplines: [],
                      children: []
                    };

                    const updated = [
                      ...disciplines.slice(0, index + 1),
                      newNode,
                      ...disciplines.slice(index + 1)
                    ];

                    setDisciplines(updated);
                  }}
                  onUpdate={(updated) =>
                    handleDisciplineUpdate(index, updated)
                  }
                />
              ))
          }
        </div>

        <TreeActions
          onAddDiscipline={handleAddDiscipline}
          onToggleJson={handleToggleJson}
          showJson={showJson}
          onSubmit={handleSubmitProgram}
          submitting={submitting}
        />

        {showJson &&
          <JsonViewer
            data={convertToBackendFormat(programName, disciplines)}
          />
        }
      </div>
    </Modal>
  );
};

export default TreeEditor;
