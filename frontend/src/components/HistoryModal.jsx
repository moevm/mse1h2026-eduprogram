import React, { useState } from 'react';
import Button from '../components/Button/Button';
import './HistoryModal.css';

const HistoryModal = ({ isOpen, onClose, historyData, onViewResult }) => {
  const [loadingHash, setLoadingHash] = useState(null);

  if (!isOpen) return null;

  const handleViewResult = async (item) => {
    setLoadingHash(item.hash);
    try {
      await onViewResult(item);
    } finally {
      setLoadingHash(null);
    }
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
                      Hash: {item.hash.substring(0, 16)}...
                    </span>
                  )}
                </div>
                <Button
                  type="button"
                  color="#000000"
                  onClick={() => handleViewResult(item)}
                  width="200px"
                  height="43px"
                  absolute={false}
                  disabled={loadingHash === item.hash}
                >
                  <p className="text-program">
                    {loadingHash === item.hash ? 'Загрузка...' : 'Посмотреть результат сравнения'}
                  </p>
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