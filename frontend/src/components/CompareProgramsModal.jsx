import React from 'react';
import Modal from './UI/Modal/Modal';
import Button from './UI/Button/Button';
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
  isSubmitting = false,
}) => {
  const selectedMainProgram = programs.find((program) => program.id === selectedMainProgramId) || null;
  const comparePrograms = programs.filter((program) => program.id !== selectedMainProgramId);
  const handleClose = isSubmitting ? undefined : onClose;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Сравнение программ"
      showClose={!isSubmitting}
      size="small"
    >
      <div className="compare-modal-body-wrap">
        {isSubmitting ? (
          <div className="compare-modal-loading" aria-live="polite" aria-busy="true">
            <div className="compare-modal-loading__spinner" />
            <p className="compare-modal-loading__text">Сравниваем программы...</p>
          </div>
        ) : null}

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
            disabled={isSubmitting}
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
                    disabled={isSubmitting}
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
            onClick={onCompare}
            disabled={!canCompare || !selectedMainProgram || isSubmitting}
            width="100%"
          >
            {isSubmitting ? 'Сравнение...' : 'Сравнить'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default CompareProgramsModal;
