import React from 'react';
import './TreeEditor.css';

const JsonViewer = ({ data }) => {
  return (
    <pre className="json-output">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
};

export default JsonViewer;