import Modal from './UI/Modal/Modal';
import Button from './UI/Button/Button';
import './ProgramsModal.css';

const ProgramsModal = ({ isOpen, onClose, programs, onShowGraph }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Образовательные программы"
      showClose
      size="small"
    >
      {programs.length === 0 ? (
        <p className="text-program">Нет данных</p>
      ) : (
        <ul className="programs-modal-list">
          {programs.map((program, idx) => {
            const label = program.displayName || program;
            return (
              <li key={idx} className="programs-modal-item">
                <span
                  className="text-program programs-modal-item__label"
                  title={label}
                >
                  {label}
                </span>
                <Button
                  type="button"
                  color="#000000"
                  onClick={() => onShowGraph(program)}
                  width="160px"
                  height="43px"
                  absolute={false}
                >
                  <span className="text-program">Показать граф программы</span>
                </Button>
              </li>
            );
          })}
        </ul>
      )}
    </Modal>
  );
};

export default ProgramsModal;
