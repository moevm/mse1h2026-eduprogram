import React, { useRef, useState } from 'react';
import GraphNavbar from './GraphNavbar/GraphNavbar';
import GraphAside from './GraphAside/GraphAside';
import GraphField from './GraphField/GraphField';
import './GraphPanel.css';

const GraphPanel = ({ data }) => {
  const graphFieldRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedDirection, setSelectedDirection] = useState('Программная Инженерия');

  const handleExportPNG = () => {
    if (graphFieldRef.current) graphFieldRef.current.exportPNG();
  };

  const handleExportGraphPDF = () => {
    if (graphFieldRef.current) graphFieldRef.current.exportPDF();
  };

  const handleNodeSelect = (nodeData) => {
    setSelectedNode(nodeData);
  };

  if (!data) {
    return <div className="graph-panel-empty">Данные графа не загружены</div>;
  }

  return (
    <>
      <GraphNavbar
        onExportPNG={handleExportPNG}
      />
      <div className="graph-panel">
        <GraphAside 
          selectedNode={selectedNode}
          selectedDirection={selectedDirection}
          onDirectionChange={setSelectedDirection}
          onExportGraphPDF={handleExportGraphPDF}
        />
        <GraphField
          ref={graphFieldRef}
          data={data}
          onNodeSelect={handleNodeSelect}
        />
      </div>
    </>
  );
};

export default GraphPanel;