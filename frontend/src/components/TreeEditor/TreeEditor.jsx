import React, { useState } from 'react';
import TreeNode from './TreeNode';
import EmptyState from './EmptyState';
import TreeActions from './TreeActions';
import JsonViewer from './JsonViewer';
import { generateId } from './utils';
import './TreeEditor.css';

const TreeEditor = () => {
  const [disciplines, setDisciplines] = useState([
    {
      id: generateId(),
      name: 'Математика',
      type: 'discipline',
      children: [
        {
          id: generateId(),
          name: 'Алгебра',
          type: 'topic',
          children: [
            {
              id: generateId(),
              name: 'Квадратные уравнения',
              type: 'subtopic',
              children: []
            }
          ]
        }
      ]
    }
  ]);

  const [showJson, setShowJson] = useState(false);
  
  const handleAddDiscipline = () => {
    setDisciplines([
      ...disciplines,
      {
        id: generateId(),
        name: '',
        type: 'discipline',
        children: []
      }
    ]);
  };

  const handleDisciplineUpdate = (index, updatedDiscipline) => {
    if (updatedDiscipline === null) {
      setDisciplines(disciplines.filter((_, i) => i !== index));
    } else {
      const newDisciplines = [...disciplines];
      newDisciplines[index] = updatedDiscipline;
      setDisciplines(newDisciplines);
    }
  };

  const handleToggleJson = () => {
    setShowJson(!showJson);
  };

  return (
    <div className="tree-editor-container">
      <div className="header">
        <h1>Редактор учебного графа</h1>
        <p className="subtitle">Дисциплины → Темы → Подтемы (можно сворачивать)</p>
      </div>

      <div className="tree-root">
        {disciplines.length === 0 ? (
          <EmptyState />
        ) : (
          disciplines.map((discipline, index) => (
            <TreeNode
              key={discipline.id}
              node={discipline}
              onUpdate={(updated) => handleDisciplineUpdate(index, updated)}
              level={0}
            />
          ))
        )}
      </div>

      <TreeActions 
        onAddDiscipline={handleAddDiscipline}
        onToggleJson={handleToggleJson}
        showJson={showJson}
      />

      {showJson && (
        <JsonViewer data={disciplines} />
      )}
    </div>
  );
};

export default TreeEditor;