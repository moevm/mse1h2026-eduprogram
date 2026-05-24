import React, { useEffect, useRef, forwardRef, useImperativeHandle, useCallback } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import './GraphField.css';

cytoscape.use(dagre);

const GraphField = forwardRef(({
                                   data,
                                   viewMode = 'graph',
                                   bridgePairs = [],
                                   selectedNodeIds = [],
                                   hiddenNodeIds = [],
                                   expandedNodes = new Set(),
                                   childrenMap = {},
                                   nodeTypeMap = {},
                                   onToggleExpand,
                                   onToggleNodeSelection,
                                   onSelectionChange
                               }, ref) => {
    const containerRef = useRef(null);
    const cyRef = useRef(null);
    const ignoreTapCloseUntilRef = useRef(0);
    const selectedNodeIdsRef = useRef(selectedNodeIds);
    const onToggleNodeSelectionRef = useRef(onToggleNodeSelection);
    const onSelectionChangeRef = useRef(onSelectionChange);
    const onToggleExpandRef = useRef(onToggleExpand);
    const layoutRunningRef = useRef(false);

    const expandedNodesRef = useRef(expandedNodes);
    const childrenMapRef = useRef(childrenMap);
    const nodeTypeMapRef = useRef(nodeTypeMap);
    const bridgePairsRef = useRef(bridgePairs);
    const viewModeRef = useRef(viewMode);

    useEffect(() => { selectedNodeIdsRef.current = selectedNodeIds; }, [selectedNodeIds]);
    useEffect(() => { onToggleNodeSelectionRef.current = onToggleNodeSelection; }, [onToggleNodeSelection]);
    useEffect(() => { onSelectionChangeRef.current = onSelectionChange; }, [onSelectionChange]);
    useEffect(() => { onToggleExpandRef.current = onToggleExpand; }, [onToggleExpand]);
    useEffect(() => { expandedNodesRef.current = expandedNodes; }, [expandedNodes]);
    useEffect(() => { childrenMapRef.current = childrenMap; }, [childrenMap]);
    useEffect(() => { nodeTypeMapRef.current = nodeTypeMap; }, [nodeTypeMap]);
    useEffect(() => { bridgePairsRef.current = bridgePairs; }, [bridgePairs]);
    useEffect(() => { viewModeRef.current = viewMode; }, [viewMode]);

    useImperativeHandle(ref, () => ({
        exportPNG: () => {
            if (cyRef.current) {
                const png = cyRef.current.png();
                const link = document.createElement('a');
                link.download = 'graph.png';
                link.href = png;
                link.click();
            }
        },
        exportPDF: () => {
            if (cyRef.current) {
                const png = cyRef.current.png({ full: true, maxWidth: 1920, maxHeight: 1080 });
                const link = document.createElement('a');
                link.download = 'graph.pdf';
                link.href = png;
                link.click();
            }
        }
    }));

    const computeVisibleNodeIds = useCallback((expanded, hidden) => {
        const visible = new Set();
        const cm = childrenMapRef.current;
        const ntm = nodeTypeMapRef.current;


        Object.keys(ntm).forEach((nodeId) => {
            if (ntm[nodeId] === 'discipline') {
                visible.add(nodeId);
            }
        });

        expanded.forEach((parentId) => {
            const children = cm[parentId] || [];
            children.forEach((childId) => {
                visible.add(childId);
                const grandChildren = cm[childId] || [];
                grandChildren.forEach((gc) => visible.add(gc));
            });
        });

        hidden.forEach((id) => visible.delete(id));

        return visible;
    }, []);

    const normalizeBridgePairs = useCallback((pairs) => {
        if (!Array.isArray(pairs)) {
            return [];
        }

        return pairs
            .map((pair) => {
                if (Array.isArray(pair) && pair.length >= 2) {
                    return [pair[0], pair[1]];
                }

                if (pair && typeof pair === 'object') {
                    const values = Object.values(pair);
                    if (values.length >= 2) {
                        return [values[0], values[1]];
                    }
                }

                return null;
            })
            .filter(Boolean);
    }, []);

    const applyBridgeMode = useCallback((cy, visibleIds) => {
        if (!cy || cy.destroyed()) return;

        const bridgePairsNormalized = normalizeBridgePairs(bridgePairsRef.current);
        const bridgeNodeIds = new Set();
        const bridgeEdgeKeys = new Set();

        bridgePairsNormalized.forEach(([sourceId, targetId]) => {
            bridgeNodeIds.add(sourceId);
            bridgeNodeIds.add(targetId);
            bridgeEdgeKeys.add(`${sourceId}::${targetId}`);
            bridgeEdgeKeys.add(`${targetId}::${sourceId}`);
        });

        cy.batch(() => {
            cy.nodes().style('display', 'none');
            cy.edges().style('display', 'none');

            cy.elements().removeClass('bridge-muted bridge-highlight');

            visibleIds.forEach((nodeId) => {
                const node = cy.getElementById(nodeId);
                if (node.nonempty()) node.style('display', 'element');
            });

            cy.edges().forEach((edge) => {
                const src = edge.data('source');
                const tgt = edge.data('target');
                if (visibleIds.has(src) && visibleIds.has(tgt)) {
                    edge.style('display', 'element');
                }
            });

            cy.nodes().forEach((node) => {
                if (node.style('display') !== 'element') return;
                const id = node.data('id');
                if (bridgeNodeIds.has(id)) {
                    node.addClass('bridge-highlight');
                } else {
                    node.addClass('bridge-muted');
                }
            });

            cy.edges().forEach((edge) => {
                if (edge.style('display') !== 'element') return;
                const edgeKey = `${edge.data('source')}::${edge.data('target')}`;
                if (bridgeEdgeKeys.has(edgeKey)) {
                    edge.addClass('bridge-highlight');
                } else {
                    edge.addClass('bridge-muted');
                }
            });

            cy.nodes().removeClass('highlighted expanded');
            cy.nodes().unselect();
        });
    }, [normalizeBridgePairs]);

    const applyVisibility = useCallback((cy, expanded, selected, hidden, shouldFit = false) => {
        if (!cy || cy.destroyed()) return;
        if (layoutRunningRef.current) return;

        const visibleIds = computeVisibleNodeIds(expanded, new Set(hidden));

        if (viewModeRef.current === 'bridges') {
            applyBridgeMode(cy, visibleIds);
        } else {
            cy.batch(() => {
                cy.elements().removeClass('bridge-muted bridge-highlight');
                cy.nodes().style('display', 'none');
                cy.edges().style('display', 'none');

                visibleIds.forEach((nodeId) => {
                    const node = cy.getElementById(nodeId);
                    if (node.nonempty()) {
                        node.style('display', 'element');
                    }
                });

                cy.edges().forEach((edge) => {
                    const srcId = edge.data('source');
                    const tgtId = edge.data('target');
                    if (visibleIds.has(srcId) && visibleIds.has(tgtId)) {
                        edge.style('display', 'element');
                    }
                });

                cy.nodes().removeClass('highlighted expanded');
                cy.nodes().unselect();

                selected.forEach((nodeId) => {
                    const node = cy.getElementById(nodeId);
                    if (node.nonempty() && visibleIds.has(nodeId)) {
                        node.addClass('highlighted');
                        node.select();
                    }
                });

                expanded.forEach((nodeId) => {
                    const node = cy.getElementById(nodeId);
                    if (node.nonempty() && visibleIds.has(nodeId)) {
                        node.addClass('expanded');
                    }
                });
            });
        }

        const visibleNodes = cy.nodes().filter(n => n.style('display') === 'element');
        const visibleEdges = cy.edges().filter(e => e.style('display') === 'element');
        const visibleElements = visibleNodes.union(visibleEdges);

        if (visibleNodes.length === 0) return;

        layoutRunningRef.current = true;

        const layout = visibleElements.layout({
            name: 'dagre',
            rankDir: 'TB',
            spacingFactor: 1.4,
            animate: true,
            animationDuration: 300,
            animationEasing: 'ease-in-out',
            nodeDimensionsIncludeLabels: true,
            rankSep: 80,
            nodeSep: 40,
            edgeSep: 20,
            fit: false
        });

        layout.on('layoutstop', () => {
            layoutRunningRef.current = false;
            if (cy && !cy.destroyed()) {
                cy.resize();
                if (shouldFit) {
                    cy.animate({
                        fit: { eles: visibleNodes, padding: 40 },
                        duration: 200,
                        easing: 'ease-in-out'
                    });
                }
            }
        });

        layout.run();
    }, [computeVisibleNodeIds]);

    // ========== СОЗДАНИЕ ГРАФА ==========
    useEffect(() => {
        if (!containerRef.current || !data) return;

        if (cyRef.current) {
            cyRef.current.destroy();
            cyRef.current = null;
        }

        layoutRunningRef.current = false;

        const allSubjects = Object.keys(data);
        const nodesSet = new Set(allSubjects);

        allSubjects.forEach(subject => {
            const subjectData = data[subject];
            const predecessors = subjectData.предметы_до || [];
            const successors = subjectData.предметы_после || [];
            predecessors.forEach(p => nodesSet.add(p));
            successors.forEach(s => nodesSet.add(s));
        });

        const nodes = [];
        const edges = [];
        const edgesSet = new Set();

        Array.from(nodesSet).forEach(name => {
            nodes.push({
                data: {
                    id: name,
                    label: name,
                    isMain: allSubjects.includes(name) ? 'true' : 'false',
                    nodeType: 'discipline',
                    hasChildren: 'false'
                }
            });
        });

        allSubjects.forEach(subject => {
            const subjectData = data[subject];
            const predecessors = subjectData.предметы_до || [];
            const successors = subjectData.предметы_после || [];

            predecessors.forEach(p => {
                const edgeKey = `$${p}->$${subject}`;
                if (!edgesSet.has(edgeKey)) {
                    edges.push({ data: { source: p, target: subject, edgeType: 'discipline' } });
                    edgesSet.add(edgeKey);
                }
            });

            successors.forEach(s => {
                const edgeKey = `$${subject}->$${s}`;
                if (!edgesSet.has(edgeKey)) {
                    edges.push({ data: { source: subject, target: s, edgeType: 'discipline' } });
                    edgesSet.add(edgeKey);
                }
            });

            const topics = Array.isArray(subjectData.темы) ? subjectData.темы : [];
            topics.forEach((topic) => {
                const topicName = topic?.name;
                if (!topicName) return;

                const topicId = `topic::$${subject}::$${topicName}`;
                nodes.push({
                    data: {
                        id: topicId,
                        label: topicName,
                        isMain: 'false',
                        nodeType: 'topic',
                        parentDiscipline: subject,
                        hasChildren: 'false'
                    }
                });

                const subjectToTopicEdge = `$${subject}->$${topicId}`;
                if (!edgesSet.has(subjectToTopicEdge)) {
                    edges.push({ data: { source: subject, target: topicId, edgeType: 'hierarchy' } });
                    edgesSet.add(subjectToTopicEdge);
                }

                const subtopics = Array.isArray(topic.subtopics) ? topic.subtopics : [];
                subtopics.forEach((subtopic) => {
                    if (!subtopic) return;

                    const subtopicId = `subtopic::$${subject}::$${topicName}::${subtopic}`;
                    nodes.push({
                        data: {
                            id: subtopicId,
                            label: subtopic,
                            isMain: 'false',
                            nodeType: 'subtopic',
                            parentTopic: topicId,
                            parentDiscipline: subject,
                            hasChildren: 'false'
                        }
                    });

                    const topicToSubtopicEdge = `$${topicId}->$${subtopicId}`;
                    if (!edgesSet.has(topicToSubtopicEdge)) {
                        edges.push({ data: { source: topicId, target: subtopicId, edgeType: 'hierarchy' } });
                        edgesSet.add(topicToSubtopicEdge);
                    }
                });
            });
        });

        // Проставляем hasChildren по childrenMap из пропсов
        const cm = childrenMapRef.current;
        Object.keys(cm).forEach((parentId) => {
            if (cm[parentId] && cm[parentId].length > 0) {
                const nodeData = nodes.find(n => n.data.id === parentId);
                if (nodeData) {
                    nodeData.data.hasChildren = 'true';
                }
            }
        });

        try {
            const cy = cytoscape({
                container: containerRef.current,
                elements: { nodes, edges },
                boxSelectionEnabled: true,
                selectionType: 'additive',
                userZoomingEnabled: true,
                userPanningEnabled: true,
                zoomingEnabled: true,
                panningEnabled: true,
                minZoom: 0.1,
                maxZoom: 5,
                wheelSensitivity: 0.3,

                style: [
                    // В секции style cytoscape, заменяем базовый стиль node:

                    {
                        selector: 'node',
                        style: {
                            'background-color': '#ffffff',
                            'label': 'data(label)',
                            'shape': 'round-rectangle',
                            'width': 'label',
                            'height': 'label',
                            'padding': '12px',
                            'font-size': '12px',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': '#000000',
                            'font-weight': 600,
                            'text-wrap': 'wrap',
                            'text-max-width': 200,
                            'transition-property': 'background-color',
                            'transition-duration': '0.2s'
                        }
                    },
                    {
                        selector: 'node[isMain = "true"]',
                        style: {
                            'background-color': '#000000',
                            'color': '#ffffff',
                            'border-color': '#595959',
                            'border-width': '2px',
                            'font-weight': 'normal',
                            'font-size': '14px',
                            'line-height': 2,
                            'padding': '12px',
                            'text-max-width': 200,
                        }
                    },
                    {
                        selector: 'node[nodeType = "discipline"][isMain = "false"]',
                        style: {
                            'background-color': '#000000',
                            'color': '#ffffff',
                            'border-color': '#959595',
                            'border-width': '3px',
                            'font-weight': 'normal',
                            'font-size': '14px',
                            'line-height': 2,
                            'padding': '12px',
                            'text-max-width': 200,
                        }
                    },
                    {
                        selector: 'node[nodeType = "topic"]',
                        style: {
                            'background-color': '#2494ff',
                            'color': '#ffffff',
                            'border-color': '#185a98',
                            'border-width': '3px',
                            'font-weight': 'normal',
                            'font-size': '14px',
                            'line-height': 2,
                            'padding': '12px',
                            'text-max-width': 200
                        }
                    },
                    {
                        selector: 'node[nodeType = "subtopic"]',
                        style: {
                            'background-color': '#75b178',
                            'color': '#ffffff',
                            'border-color': '#3f6040',
                            'border-width': '3px',
                            'font-weight': 'normal',
                            'font-size': '14px',
                            'line-height': 2,
                            'padding': '12px',
                            'text-max-width': 200
                        }
                    },
                    {
                        selector: 'node.expanded',
                        style: {
                            'border-color': '#42444a',
                            'border-width': 2,
                            'border-style': 'solid'
                        }
                    },
                    {
                        selector: 'node.highlighted',
                        style: {
                            'border-color': '#FF9800',
                            'border-width': 5,
                            'overlay-opacity': 0,
                            'z-index': 999
                        }
                    },
                    {
                        selector: 'edge[edgeType = "discipline"]',
                        style: {
                            'width': 2.5,
                            'line-color': '#555555',
                            'target-arrow-color': '#555555',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'arrow-scale': 1.2
                        }
                    },
                    {
                        selector: 'edge[edgeType = "hierarchy"]',
                        style: {
                            'width': 1.5,
                            'line-color': '#90A4AE',
                            'target-arrow-color': '#90A4AE',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'line-style': 'dashed',
                            'arrow-scale': 0.9
                        }
                    },
                    {
                        selector: 'edge.bridge-muted',
                        style: {
                            'width': 2,
                            'line-color': '#c8c8c8',
                            'target-arrow-color': '#c8c8c8',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'arrow-scale': 1.0
                        }
                    },
                    {
                        selector: 'edge.bridge-highlight',
                        style: {
                            'width': 3.5,
                            'line-color': '#2e7d32',
                            'target-arrow-color': '#2e7d32',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'arrow-scale': 1.1
                        }
                    },
                    {
                        selector: 'node.bridge-muted',
                        style: {
                            'background-color': '#d9d9d9',
                            'color': '#4d4d4d',
                            'border-color': '#b0b0b0',
                            'border-width': '3px'
                        }
                    },
                    {
                        selector: 'node.bridge-highlight',
                        style: {
                            'background-color': '#2e7d32',
                            'color': '#ffffff',
                            'border-color': '#1b5e20',
                            'border-width': '4px'
                        }
                    }
                ],
                layout: { name: 'preset' }
            });

            cyRef.current = cy;

            // ===== ОБРАБОТКА ЛЕВОГО КЛИКА =====
            cy.on('tap', 'node', (event) => {
                if (Date.now() < ignoreTapCloseUntilRef.current) return;

                const nativeEvent = event.originalEvent;
                if (nativeEvent && nativeEvent.button !== 0) return;

                const tappedNode = event.target;
                const nodeId = tappedNode.data('id');
                const nodeType = tappedNode.data('nodeType');
                const hasChildren = tappedNode.data('hasChildren') === 'true';

                if (hasChildren && (nodeType === 'discipline' || nodeType === 'topic')) {
                    if (onToggleExpandRef.current) {
                        onToggleExpandRef.current(nodeId);
                    }
                }

                if (onToggleNodeSelectionRef.current) {
                    onToggleNodeSelectionRef.current(nodeId);
                }
            });

            // ===== СИНХРОНИЗАЦИЯ ВЫДЕЛЕНИЯ =====
            const syncSelectedFromGraph = () => {
                if (!onSelectionChangeRef.current) return;
                const selectedIds = cy.nodes(':selected').map((node) => node.id());
                onSelectionChangeRef.current(selectedIds);
            };

            cy.on('boxend', syncSelectedFromGraph);
            cy.on('select unselect', 'node', syncSelectedFromGraph);

            // ===== RESIZE OBSERVER =====
            const resizeObserver = new ResizeObserver(() => {
                if (cyRef.current && !cyRef.current.destroyed()) {
                    cyRef.current.resize();
                }
            });
            resizeObserver.observe(containerRef.current);

            // Первоначальная отрисовка
            requestAnimationFrame(() => {
                if (cy && !cy.destroyed()) {
                    cy.resize();
                    applyVisibility(cy, expandedNodesRef.current, selectedNodeIdsRef.current, hiddenNodeIds, true);
                }
            });

            return () => {
                resizeObserver.disconnect();
                if (cyRef.current) {
                    cyRef.current.destroy();
                    cyRef.current = null;
                }
            };

        } catch (err) {
            console.error('Error creating cytoscape graph:', err);
        }

        return () => {
            if (cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [data]);

    // ===== РЕАКЦИЯ НА ИЗМЕНЕНИЕ expandedNodes =====
    useEffect(() => {
        if (!cyRef.current || cyRef.current.destroyed()) return;
        applyVisibility(cyRef.current, expandedNodes, selectedNodeIds, hiddenNodeIds, false);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [expandedNodes]);

    useEffect(() => {
        if (!cyRef.current || cyRef.current.destroyed()) return;

        const cy = cyRef.current;

        const runApply = () => applyVisibility(cy, expandedNodesRef.current, selectedNodeIdsRef.current, hiddenNodeIds, false);

        if (viewMode === 'bridges') {
            // If a layout is running, schedule highlighting after it finishes
            if (layoutRunningRef.current) {
                try {
                    cy.once('layoutstop', () => {
                        // small timeout to ensure styles settle
                        setTimeout(() => runApply(), 30);
                    });
                } catch (e) {
                    runApply();
                }
            } else {
                runApply();
            }
        } else {
            runApply();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [bridgePairs, viewMode]);

    // ===== РЕАКЦИЯ НА ИЗМЕНЕНИЕ selectedNodeIds / hiddenNodeIds =====
    useEffect(() => {
        if (!cyRef.current || cyRef.current.destroyed()) return;
        applyVisibility(cyRef.current, expandedNodes, selectedNodeIds, hiddenNodeIds, false);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedNodeIds, hiddenNodeIds]);

    return (
        <div className="graph-field-shell">
            <div ref={containerRef} className="graph-field" />
        </div>
    );
});

export default GraphField;