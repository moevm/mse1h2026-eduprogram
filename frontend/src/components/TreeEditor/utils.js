
export const generateId = () => Date.now() + '-' + Math.random().toString(36).substr(2, 9);

export const getChildType = (parentType) => {
  const map = {
    'discipline': 'topic',
    'topic': 'subtopic',
    'subtopic': null
  };
  return map[parentType];
};

export const getRussianType = (type) => {
  const map = {
    'discipline': 'дисциплина',
    'topic': 'тема',
    'subtopic': 'подтема'
  };
  return map[type] || type;
};

export const getPlaceholder = (type) => {
  const map = {
    'discipline': 'Название дисциплины',
    'topic': 'Название темы',
    'subtopic': 'Название подтемы'
  };
  return map[type] || 'Введите название';
};