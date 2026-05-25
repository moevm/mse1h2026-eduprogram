import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import GraphNavbar from './GraphNavbar/GraphNavbar';
import GraphAside from './GraphAside/GraphAside';
import GraphField from './GraphField/GraphField';
import './GraphPanel.css';

const GraphPanel = ({ data, viewMode = 'graph', bridgePairs = [], onModeChange }) => {
  const graphFieldRef = useRef(null);
  const historyStepRef = useRef(0);

  const [selectedNodeIds, setSelectedNodeIds] = useState([]);
  const [hiddenNodeIds, setHiddenNodeIds] = useState([]);
  const [hideHistory, setHideHistory] = useState([]);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [searchResults, setSearchResults] = useState([]);
  const [searchIndex, setSearchIndex] = useState(0);
  const [searchMessage, setSearchMessage] = useState('');

  // ========== Построение карт узлов ==========
  const { nodeOptions, childrenMap, nodeTypeMap, parentMap } = useMemo(() => {
    if (!data) return { nodeOptions: [], childrenMap: {}, nodeTypeMap: {}, parentMap: {} };

    const nodesMap = new Map();
    const childrenMap = {};
    const nodeTypeMap = {};
    const parentMap = {};
    const allSubjects = Object.keys(data);

    allSubjects.forEach((subject) => {
      nodesMap.set(subject, { id: subject, label: subject, searchLabel: subject, nodeType: 'discipline' });
      nodeTypeMap[subject] = 'discipline';
      childrenMap[subject] = [];

      const subjectData = data[subject] || {};
      const predecessors = subjectData.предметы_до || [];
      const successors = subjectData.предметы_после || [];

      [...predecessors, ...successors].forEach((name) => {
        if (!nodesMap.has(name)) {
          nodesMap.set(name, { id: name, label: name, searchLabel: name, nodeType: 'discipline' });
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
          searchLabel: topicName,
          nodeType: 'topic'
        });
        nodeTypeMap[topicId] = 'topic';
        childrenMap[subject].push(topicId);
        childrenMap[topicId] = [];
        parentMap[topicId] = subject;

        const subtopics = Array.isArray(topic.subtopics) ? topic.subtopics : [];
        subtopics.forEach((subtopic) => {
          if (!subtopic) return;
          const subtopicId = `subtopic::$${subject}::$${topicName}::${subtopic}`;
          nodesMap.set(subtopicId, {
            id: subtopicId,
            label: `$${subtopic} ($${subject})`,
            searchLabel: subtopic,
            nodeType: 'subtopic'
          });
          nodeTypeMap[subtopicId] = 'subtopic';
          childrenMap[topicId].push(subtopicId);
          parentMap[subtopicId] = topicId;
        });
      });
    });

    return {
      nodeOptions: Array.from(nodesMap.values()).sort((a, b) => a.label.localeCompare(b.label, 'ru')),
      childrenMap,
      nodeTypeMap,
      parentMap
    };
  }, [data]);

  const buildSearchMatches = useCallback((query) => {
    const normalizedQuery = query.trim().toLowerCase();

    if (!normalizedQuery) {
      return [];
    }

    return nodeOptions.filter((node) => (node.searchLabel || node.label).toLowerCase().includes(normalizedQuery));
  }, [nodeOptions]);

  const getSearchDisplayName = useCallback((node) => {
    if (!node) return '';
    return node.searchLabel || node.label || '';
  }, []);

  const expandAncestorsForMatches = useCallback((matches) => {
    const nextExpanded = new Set();

    matches.forEach((matchedNode) => {
      if (matchedNode.nodeType === 'discipline') return;

      let currentId = matchedNode.id;
      while (parentMap[currentId]) {
        currentId = parentMap[currentId];
        nextExpanded.add(currentId);
      }
    });

    if (nextExpanded.size > 0) {
      setExpandedNodes((prev) => {
        const next = new Set(prev);
        nextExpanded.forEach((nodeId) => next.add(nodeId));
        return next;
      });
    }
  }, [parentMap]);

  const handleSearch = useCallback((query) => {
    const normalizedQuery = query.trim();

    if (!normalizedQuery) {
      setSearchResults([]);
      setSearchIndex(0);
      setSearchMessage('Введите подстроку для поиска.');
      return;
    }

    const matches = buildSearchMatches(normalizedQuery);

    if (!matches.length) {
      setSearchResults([]);
      setSearchIndex(0);
      setSearchMessage(`Вершина по подстроке «${normalizedQuery}» не найдена.`);
      return;
    }

    expandAncestorsForMatches(matches);
    setSearchResults(matches.map((node) => node.id));
    setSearchIndex(0);
    setSearchMessage(
      matches.length > 1
        ? `Найдено ${matches.length} вершин. Показана 1 из ${matches.length}: ${getSearchDisplayName(matches[0])}`
        : `Найдена вершина: ${getSearchDisplayName(matches[0])}`
    );
  }, [buildSearchMatches, expandAncestorsForMatches, getSearchDisplayName]);

  const handleSearchNavigate = useCallback((direction) => {
    if (searchResults.length <= 1) return;

    setSearchIndex((prev) => {
      const nextIndex = direction === 'prev'
        ? (prev - 1 + searchResults.length) % searchResults.length
        : (prev + 1) % searchResults.length;
      const activeNode = nodeOptions.find((node) => node.id === searchResults[nextIndex]);

      if (activeNode) {
        setSearchMessage(`Найдено ${searchResults.length} вершин. Показана ${nextIndex + 1} из ${searchResults.length}: ${getSearchDisplayName(activeNode)}`);
      }

      return nextIndex;
    });
  }, [getSearchDisplayName, nodeOptions, searchResults]);

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

  const handleSearchClear = useCallback(() => {
    setSearchResults([]);
    setSearchIndex(0);
    setSearchMessage('');
  }, []);

  const currentSearchNodeId = searchResults.length > 0 ? searchResults[searchIndex] : null;

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
      <GraphNavbar onExportPNG={handleExportPNG} onModeChange={onModeChange} />
        <div className="graph-panel">
          <GraphAside
              onExpandAll={handleExpandAll}
              onCollapseAll={handleCollapseAll}
              onHideSelected={handleHideSelected}
              onShowFromSelected={handleShowFromSelected}
              hasSelection={selectedNodeIds.length > 0}
              onSearch={handleSearch}
              onSearchClear={handleSearchClear}
                onSearchPrev={() => handleSearchNavigate('prev')}
                onSearchNext={() => handleSearchNavigate('next')}
                hasSearchResults={searchResults.length > 0}
                hasMultipleSearchResults={searchResults.length > 1}
                searchResultIndex={searchResults.length > 0 ? searchIndex : 0}
                searchResultCount={searchResults.length}
              searchMessage={searchMessage}
          />
          <GraphField
              ref={graphFieldRef}
              data={data}
          viewMode={viewMode}
          bridgePairs={bridgePairs}
              selectedNodeIds={selectedNodeIds}
              hiddenNodeIds={hiddenNodeIds}
              expandedNodes={expandedNodes}
              childrenMap={childrenMap}
              nodeTypeMap={nodeTypeMap}
                searchResults={searchResults}
                currentSearchNodeId={currentSearchNodeId}
              onToggleExpand={handleToggleExpand}
              onToggleNodeSelection={handleToggleNodeSelection}
              onSelectionChange={handleSelectionChange}
          />
        </div>
      </>
  );
};

export default GraphPanel;