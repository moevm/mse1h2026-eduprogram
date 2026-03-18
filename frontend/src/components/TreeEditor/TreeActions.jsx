import React from 'react';
import './TreeEditor.css';

const TreeActions = ({ onAddDiscipline, onToggleJson, showJson }) => {
  return (
    <div className="actions">
      <button className="primary-btn" onClick={onAddDiscipline}>
        Добавить дисциплину
      </button>
      <button className="secondary-btn" onClick={onToggleJson}>
        {showJson ? 'Скрыть JSON' : 'Показать JSON'}
      </button>
    </div>
  );
};

export default TreeActions;