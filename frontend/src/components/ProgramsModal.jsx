import './ProgramsModal.css';
import Button from '../components/Button/Button';

const ProgramsModal = ({ isOpen, onClose, programs, onShowGraph }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="title-window">Образовательные программы</h3>
        
        {programs.length === 0 ? (
          <p className="text-program">Нет данных</p>
        ) : (
          <ul>
            {programs.map((program, idx) => (
              <li key={idx}>
                <span className="text-program">{program.displayName || program}</span>
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
            ))}
          </ul>
        )}
        
        <Button
        className="close-button"
        type="button"
        onClick={onClose}
        width="260px"
        height="43px"
        >
          <span className="text-program">Закрыть</span>
        </Button>
      </div>

    </div>
  );
};

export default ProgramsModal;