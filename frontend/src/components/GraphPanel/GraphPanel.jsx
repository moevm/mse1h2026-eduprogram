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

  // Получаем все дочерние узлы для выбранных (темы для дисциплин, подтемы для тем)
  const getCascadeNodeIds = useCallback((baseNodeIds) => {
    const cascadeNodeIds = new Set(baseNodeIds);

    baseNodeIds.forEach((nodeId) => {
      const node = nodeOptions.find((candidate) => candidate.id === nodeId);
      if (!node) return;

      if (node.nodeType === 'discipline') {
        nodeOptions.forEach((candidate) => {
          if (candidate.nodeType !== 'topic' && candidate.nodeType !== 'subtopic') return;
          if (candidate.id.startsWith(`topic::${nodeId}::`) || candidate.id.startsWith(`subtopic::${nodeId}::`)) {
            cascadeNodeIds.add(candidate.id);
          }
        });
        return;
      }

      if (node.nodeType === 'topic') {
        const parts = nodeId.split('::');
        const subject = parts[1];
        const topicName = parts[2];
        if (!subject || !topicName) return;

        const subtopicPrefix = `subtopic::${subject}::${topicName}::`;
        nodeOptions.forEach((candidate) => {
          if (candidate.nodeType !== 'subtopic') return;
          if (candidate.id.startsWith(subtopicPrefix)) {
            cascadeNodeIds.add(candidate.id);
          }
        });
      }
    });

    return Array.from(cascadeNodeIds);
  }, [nodeOptions]);

  const handleHideSelected = useCallback(() => {
    if (!selectedNodeIds.length) return;

    const nodesToHide = getCascadeNodeIds(selectedNodeIds);
    const newlyHidden = nodesToHide.filter((id) => !hiddenNodeIds.includes(id));
    
    if (newlyHidden.length) {
      historyStepRef.current += 1;
      setHiddenNodeIds((prev) => Array.from(new Set([...prev, ...newlyHidden])));
      setHideHistory((prev) => [
        ...prev,
        { step: historyStepRef.current, nodeIds: newlyHidden }
      ]);
    }

    setSelectedNodeIds([]);
  }, [getCascadeNodeIds, hiddenNodeIds, selectedNodeIds]);

  const handleKeepOnlySelectedAndDescendants = useCallback(() => {
    if (!selectedNodeIds.length) return;

    const nodesToKeep = new Set(getCascadeNodeIds(selectedNodeIds));
    const nextHiddenNodeIds = nodeOptions
      .map((node) => node.id)
      .filter((id) => !nodesToKeep.has(id));

    const currentHidden = new Set(hiddenNodeIds);
    const hasChanges =
      nextHiddenNodeIds.length !== hiddenNodeIds.length ||
      nextHiddenNodeIds.some((id) => !currentHidden.has(id));

    if (!hasChanges) return;

    historyStepRef.current += 1;
    setHiddenNodeIds(nextHiddenNodeIds);
    setHideHistory((prev) => [
      ...prev,
      {
        step: historyStepRef.current,
        type: 'snapshot',
        previousHiddenNodeIds: hiddenNodeIds
      }
    ]);
  }, [getCascadeNodeIds, hiddenNodeIds, nodeOptions, selectedNodeIds]);

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
          onHideSelected={handleHideSelected}
          hideButtonText={getHideButtonText}
          keepOnlyButtonText="Оставить только выделенные и потомков"
          onKeepOnlySelectedAndDescendants={handleKeepOnlySelectedAndDescendants}
        />
      </div>
    </>
  );
};

export default GraphPanel;