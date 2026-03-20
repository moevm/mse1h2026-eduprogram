import { useState } from 'react';
import './ProgramsModal.css';

const ProgramsModal = ({ isOpen, onClose, programs, onShowGraph }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>Образовательные программы</h3>
        
        {programs.length === 0 ? (
          <p>Нет данных</p>
        ) : (
          <ul>
            {programs.map((program, idx) => (
              <li key={idx}>
                <span>{program}</span>
                <button onClick={() => onShowGraph(program)} name={program}>
                  Показать граф программы
                </button>
              </li>
            ))}
          </ul>
        )}
        
        <button className="close-btn" onClick={onClose}>Закрыть</button>
      </div>

    </div>
  );
};

export default ProgramsModal;