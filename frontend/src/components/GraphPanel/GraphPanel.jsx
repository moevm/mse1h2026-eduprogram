import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import GraphNavbar from './GraphNavbar/GraphNavbar';
import GraphAside from './GraphAside/GraphAside';
import GraphField from './GraphField/GraphField';
import './GraphPanel.css';

const GraphPanel = ({ data }) => {
  const graphFieldRef = useRef(null);
  const historyStepRef = useRef(0);
  const [selectedNodeIds, setSelectedNodeIds] = useState([]);
  const [hiddenNodeIds, setHiddenNodeIds] = useState([]);
  const [hideHistory, setHideHistory] = useState([]);

  const nodeOptions = useMemo(() => {
    if (!data) return [];

    const nodesMap = new Map();
    const allSubjects = Object.keys(data);

    allSubjects.forEach((subject) => {
      nodesMap.set(subject, {
        id: subject,
        label: subject,
        nodeType: 'discipline'
      });

      const subjectData = data[subject] || {};
      const predecessors = subjectData.предметы_до || [];
      const successors = subjectData.предметы_после || [];

      [...predecessors, ...successors].forEach((name) => {
        if (!nodesMap.has(name)) {
          nodesMap.set(name, { id: name, label: name, nodeType: 'discipline' });
        }
      });

      const topics = Array.isArray(subjectData.темы) ? subjectData.темы : [];
      topics.forEach((topic) => {
        const topicName = topic?.name;
        if (!topicName) return;

        const topicId = `topic::${subject}::${topicName}`;
        nodesMap.set(topicId, {
          id: topicId,
          label: `${topicName} (${subject})`,
          nodeType: 'topic'
        });

        const subtopics = Array.isArray(topic.subtopics) ? topic.subtopics : [];
        subtopics.forEach((subtopic) => {
          if (!subtopic) return;
          const subtopicId = `subtopic::${subject}::${topicName}::${subtopic}`;
          nodesMap.set(subtopicId, {
            id: subtopicId,
            label: `${subtopic} (${subject})`,
            nodeType: 'subtopic'
          });
        });
      });
    });

    return Array.from(nodesMap.values()).sort((a, b) => a.label.localeCompare(b.label, 'ru'));
  }, [data]);

  const handleExportPNG = () => {
    if (graphFieldRef.current) graphFieldRef.current.exportPNG();
  };

  const handleExportGraphPDF = () => {
    if (graphFieldRef.current) graphFieldRef.current.exportPDF();
  };

  const handleToggleNodeSelection = (nodeId) => {
    setSelectedNodeIds((prev) =>
      prev.includes(nodeId) ? prev.filter((id) => id !== nodeId) : [...prev, nodeId]
    );
  };

  const handleSelectionChange = (nodeIds) => {
    setSelectedNodeIds(nodeIds);
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
          hiddenNodeIds={hiddenNodeIds}
        />
        <GraphField
          ref={graphFieldRef}
          data={data}
          selectedNodeIds={selectedNodeIds}
          hiddenNodeIds={hiddenNodeIds}
        />
      </div>
    </>
  );
};

export default GraphPanel;