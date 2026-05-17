import './HistoryModal.css';
import Button from '../components/Button/Button';

const HistoryModal = ({ isOpen, onClose, historyData, onShowHistory }) => {
  if (!isOpen) return null;

  const handleShowHistory = (item) => {
    if (onShowHistory) {
      onShowHistory(item);
    }
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="title-window">История сравнений</h3>
        
        {historyData.length === 0 ? (
          <p className="text-program">Нет сохранённых сравнений</p>
        ) : (
          <ul>
            {historyData.map((item, index) => (
              <li key={index}>
                <div className="history-info">
                  <span className="text-program program-name">
                    {item.program_name || `Сравнение ${index + 1}`}
                  </span>
                  {item.hash && (
                    <span className="text-program program-hash">
                      {item.hash.substring(0, 20)}...
                    </span>
                  )}
                </div>
                <Button
                  type="button"
                  color="#000000"
                  onClick={() => handleShowHistory(item)}
                  width="160px"
                  height="43px"
                  absolute={false}
                >
                  <p className="text-program">Просмотр</p>
                </Button>
              </li>
            ))}
          </ul>
        )}
        
        <Button
          className="close-button"
          type="button"
          color="#2058c7"
          onClick={onClose}
          width="260px"
          height="43px"
        >
          <p className="text-program">Закрыть</p>
        </Button>
      </div>
    </div>
  );
};

export default HistoryModal;