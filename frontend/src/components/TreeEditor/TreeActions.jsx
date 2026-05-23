import React from 'react';
import './TreeEditor.css';
import Button from '../UI/Button/Button';

const TreeActions = ({ onAddDiscipline, onToggleJson, showJson, onSubmit }) => {
  return (
    <div className="actions">
      <Button onClick={onAddDiscipline}>
        Добавить дисциплину
      </Button>
      <Button onClick={onToggleJson}>
        {showJson ? 'Скрыть JSON' : 'Показать JSON'}
      </Button>
      <Button className="align-end" onClick={onSubmit}>
        Отправить программу
      </Button>
    </div>
  );
};

export default TreeActions;