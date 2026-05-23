import React, { useState } from 'react';
import Modal from './UI/Modal/Modal';
import Button from './UI/Button/Button';
import './HistoryModal.css';

const HistoryModal = ({ isOpen, onClose, historyData, onViewResult }) => {
  const [loadingHash, setLoadingHash] = useState(null);

  const handleViewResult = async (item) => {
    setLoadingHash(item.hash);
    try {
      await onViewResult(item);
    } finally {
      setLoadingHash(null);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="История сравнений"
      showClose
      size="small"
    >
      {historyData.length === 0 ? (
        <p className="text-program">Нет сохранённых сравнений</p>
      ) : (
        <ul className="history-modal-list">
          {historyData.map((item, index) => (
            <li key={index} className="history-modal-item">
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
    </Modal>
  );
};

export default HistoryModal;
