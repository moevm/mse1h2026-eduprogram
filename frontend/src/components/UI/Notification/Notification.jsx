import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import './Notification.css';

const NotificationContext = createContext(null);

let idCounter = 0;
const nextId = () => {
  idCounter += 1;
  return idCounter;
};

export const NotificationProvider = ({ children }) => {
  const [items, setItems] = useState([]);

  const remove = useCallback((id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const notify = useCallback((message, options = {}) => {
    const { type = 'info', duration = 4000 } = options;
    const id = nextId();
    setItems((prev) => [...prev, { id, message, type, duration }]);
    return id;
  }, []);

  return (
    <NotificationContext.Provider value={notify}>
      {children}
      <div className="notification-stack">
        {items.map((item) => (
          <NotificationItem key={item.id} item={item} onClose={() => remove(item.id)} />
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

const NotificationItem = ({ item, onClose }) => {
  useEffect(() => {
    if (item.duration <= 0) return undefined;
    const timer = setTimeout(onClose, item.duration);
    return () => clearTimeout(timer);
  }, [item.duration, onClose]);

  return (
    <div className={`notification notification--${item.type}`} role="alert">
      <span className="notification__message">{item.message}</span>
      <button
        type="button"
        className="notification__close"
        onClick={onClose}
        aria-label="Закрыть"
      >
        ×
      </button>
    </div>
  );
};

export const useNotification = () => {
  const notify = useContext(NotificationContext);
  if (!notify) {
    throw new Error('useNotification должен использоваться внутри <NotificationProvider>');
  }
  return notify;
};

export default NotificationProvider;
