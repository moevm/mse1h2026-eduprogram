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
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  // ========== Построение карт узлов ==========
  const { nodeOptions, childrenMap, nodeTypeMap } = useMemo(() => {
    if (!data) return { nodeOptions: [], childrenMap: {}, nodeTypeMap: {} };

    const nodesMap = new Map();
    const childrenMap = {};
    const nodeTypeMap = {};
    const allSubjects = Object.keys(data);

    allSubjects.forEach((subject) => {
      nodesMap.set(subject, { id: subject, label: subject, nodeType: 'discipline' });
      nodeTypeMap[subject] = 'discipline';
      childrenMap[subject] = [];

      const subjectData = data[subject] || {};
      const predecessors = subjectData.предметы_до || [];
      const successors = subjectData.предметы_после || [];

      [...predecessors, ...successors].forEach((name) => {
        if (!nodesMap.has(name)) {
          nodesMap.set(name, { id: name, label: name, nodeType: 'discipline' });
          nodeTypeMap[name] = 'discipline';
          if (!childrenMap[name]) childrenMap[name] = [];
        }
      });

      const topics = Array.isArray(subjectData.темы) ? subjectData.темы : [];
      topics.forEach((topic) => {
        const topicName = topic?.name;
        if (!topicName) return;

        const topicId = `topic::$${subject}::$${topicName}`;
        nodesMap.set(topicId, {
          id: topicId,
          label: `$${topicName} ($${subject})`,
          nodeType: 'topic'
        });
        nodeTypeMap[topicId] = 'topic';
        childrenMap[subject].push(topicId);
        childrenMap[topicId] = [];

        const subtopics = Array.isArray(topic.subtopics) ? topic.subtopics : [];
        subtopics.forEach((subtopic) => {
          if (!subtopic) return;
          const subtopicId = `subtopic::$${subject}::$${topicName}::${subtopic}`;
          nodesMap.set(subtopicId, {
            id: subtopicId,
            label: `$${subtopic} ($${subject})`,
            nodeType: 'subtopic'
          });
          nodeTypeMap[subtopicId] = 'subtopic';
          childrenMap[topicId].push(subtopicId);
        });
      });
    });

    return {
      nodeOptions: Array.from(nodesMap.values()).sort((a, b) => a.label.localeCompare(b.label, 'ru')),
      childrenMap,
      nodeTypeMap
    };
  }, [data]);

  // ========== Expand / Collapse ==========
  const handleToggleExpand = useCallback((nodeId) => {
    const children = childrenMap[nodeId] || [];
    if (children.length === 0) return;

    const willExpand = !expandedNodes.has(nodeId);

    setExpandedNodes((prev) => {
      const next = new Set(prev);

      if (next.has(nodeId)) {
        const removeRecursive = (parentId) => {
          next.delete(parentId);
          const kids = childrenMap[parentId] || [];
          kids.forEach((kidId) => removeRecursive(kidId));
        };
        removeRecursive(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });

    // При раскрытии — возвращаем скрытых прямых детей
    if (willExpand) {
      const childSet = new Set(children);
      setHiddenNodeIds((prev) =>
        prev.length === 0 ? prev : prev.filter((id) => !childSet.has(id))
      );
    }
  }, [childrenMap, expandedNodes]);

  const handleExpandAll = useCallback(() => {
    const allParents = new Set();
    Object.keys(childrenMap).forEach((parentId) => {
      if (childrenMap[parentId] && childrenMap[parentId].length > 0) {
        allParents.add(parentId);
      }
    });
    setExpandedNodes(allParents);
    setHiddenNodeIds([]);
  }, [childrenMap]);

  const handleCollapseAll = useCallback(() => {
    setExpandedNodes(new Set());
    setHiddenNodeIds([]);
  }, []);

  // ========== Export ==========
  const handleExportPNG = () => {
    if (graphFieldRef.current) graphFieldRef.current.exportPNG();
  };

  // ========== Selection ==========
  const handleToggleNodeSelection = (nodeId) => {
    setSelectedNodeIds((prev) =>
        prev.includes(nodeId) ? prev.filter((id) => id !== nodeId) : [...prev, nodeId]
    );
  };

  const handleSelectionChange = (nodeIds) => {
    setSelectedNodeIds(nodeIds);
  };

  // ========== Cascade (получить узел + всех потомков) ==========
  const getCascadeNodeIds = useCallback((baseNodeIds) => {
    const cascadeNodeIds = new Set(baseNodeIds);

    baseNodeIds.forEach((nodeId) => {
      const node = nodeOptions.find((candidate) => candidate.id === nodeId);
      if (!node) return;

      if (node.nodeType === 'discipline') {
        nodeOptions.forEach((candidate) => {
          if (candidate.nodeType !== 'topic' && candidate.nodeType !== 'subtopic') return;
          if (candidate.id.startsWith(`topic::$${nodeId}::`) || candidate.id.startsWith(`subtopic::$${nodeId}::`)) {
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

        const subtopicPrefix = `subtopic::$${subject}::$${topicName}::`;
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

  // ========== Hide / Show selected ==========
  // Скрывает то, что отходит от выделенных (сами выделенные узлы остаются видимыми)
  const handleHideSelected = useCallback(() => {
    if (selectedNodeIds.length === 0) return;
    const selectedSet = new Set(selectedNodeIds);
    const toHide = getCascadeNodeIds(selectedNodeIds).filter(
      (id) => !selectedSet.has(id)
    );
    if (toHide.length === 0) return;
    setHiddenNodeIds((prev) => Array.from(new Set([...prev, ...toHide])));
  }, [selectedNodeIds, getCascadeNodeIds]);

  // Показывает то, что было скрыто и отходит от выделенных узлов
  const handleShowFromSelected = useCallback(() => {
    if (selectedNodeIds.length === 0) return;
    const cascade = new Set(getCascadeNodeIds(selectedNodeIds));
    setHiddenNodeIds((prev) => prev.filter((id) => !cascade.has(id)));
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      cascade.forEach((id) => {
        if (childrenMap[id] && childrenMap[id].length > 0) {
          next.add(id);
        }
      });
      return next;
    });
  }, [selectedNodeIds, getCascadeNodeIds, childrenMap]);

  if (!data) {
    return <div className="graph-panel-empty">Данные графа не загружены</div>;
  }

  return (
      <>
        <GraphNavbar onExportPNG={handleExportPNG} />
        <div className="graph-panel">
          <GraphAside
              onExpandAll={handleExpandAll}
              onCollapseAll={handleCollapseAll}
              onHideSelected={handleHideSelected}
              onShowFromSelected={handleShowFromSelected}
              hasSelection={selectedNodeIds.length > 0}
          />
          <GraphField
              ref={graphFieldRef}
              data={data}
              selectedNodeIds={selectedNodeIds}
              hiddenNodeIds={hiddenNodeIds}
              expandedNodes={expandedNodes}
              childrenMap={childrenMap}
              nodeTypeMap={nodeTypeMap}
              onToggleExpand={handleToggleExpand}
              onToggleNodeSelection={handleToggleNodeSelection}
              onSelectionChange={handleSelectionChange}
          />
        </div>
      </>
  );
};

export default GraphPanel;