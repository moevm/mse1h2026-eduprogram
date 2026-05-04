import React from 'react';
import Button from './Button/Button';
import './CompareProgramsModal.css';

const CompareProgramsModal = ({
  isOpen,
  onClose,
  programs,
  selectedMainProgramId,
  selectedCompareProgramIds,
  onMainProgramChange,
  onToggleCompareProgram,
  onCompare,
  error,
  canCompare,
}) => {
  if (!isOpen) return null;

  const selectedMainProgram = programs.find((program) => program.id === selectedMainProgramId) || null;
  const comparePrograms = programs.filter((program) => program.id !== selectedMainProgramId);

  return (
    <div className="compare-modal-overlay" onClick={onClose}>
      <div className="compare-modal-content" onClick={(event) => event.stopPropagation()}>
        <h3 className="compare-modal-title">Сравнение программ</h3>

        {error ? <p className="compare-modal-error">{error}</p> : null}

        <div className="compare-modal-section">
          <label className="compare-modal-label" htmlFor="compare-main-program">
            Что сравниваем
          </label>
          <select
            id="compare-main-program"
            className="compare-modal-select"
            value={selectedMainProgramId}
            onChange={(event) => onMainProgramChange(event.target.value)}
          >
            <option value="">Выберите программу</option>
            {programs.map((program) => (
              <option key={program.id} value={program.id}>
                {program.displayName}
              </option>
            ))}
          </select>
        </div>

        <div className="compare-modal-section">
          <div className="compare-modal-label">С чем сравниваем</div>
          <div className="compare-modal-list">
            {comparePrograms.length === 0 ? (
              <p className="compare-modal-empty">Нет доступных программ для сравнения</p>
            ) : (
              comparePrograms.map((program) => (
                <label key={program.id} className="compare-modal-item">
                  <input
                    type="checkbox"
                    checked={selectedCompareProgramIds.includes(program.id)}
                    onChange={() => onToggleCompareProgram(program.id)}
                  />
                  <span>{program.displayName}</span>
                </label>
              ))
            )}
          </div>
        </div>

        <div className="compare-modal-actions">
          <Button
            type="button"
            onClick={onClose}
            width="180px"
            height="43px"
          >
            Отмена
          </Button>

          <Button
            type="button"
            onClick={onCompare}
            width="180px"
            height="43px"
            disabled={!canCompare || !selectedMainProgram}
          >
            Сравнить
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CompareProgramsModal;