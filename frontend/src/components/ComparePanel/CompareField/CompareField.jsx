import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import './CompareField.css'

cytoscape.use(dagre);

const normalizeBridgePairs = (pairs) => {
    if (!Array.isArray(pairs)) return [];
    return pairs
        .map((pair) => {
            if (Array.isArray(pair) && pair.length >= 2) {
                return [pair[0], pair[1]];
            }
            if (pair && typeof pair === 'object') {
                const values = Object.values(pair);
                if (values.length >= 2) return [values[0], values[1]];
            }
            return null;
        })
        .filter(Boolean);
};

const CompareField = ({ nodes, edges, viewMode = 'graph', bridgePairs = [] }) => {
    const cyRef = useRef(null);
    const isBridges = viewMode === 'bridges';

    useEffect(() => {
        if (!nodes || !edges) return;

        const cy = cytoscape({
            container: cyRef.current,

            elements: [...nodes, ...edges],

            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'shape': 'round-rectangle',
                        'width': 'label',
                        'height': 'label',
                        'padding': '12px',
                        'font-size': '12px',
                        'color': '#000000',
                        'font-weight': 600,
                        'text-max-width': 200,
                        'background-color': 'data(color)',
                        'text-wrap': 'wrap',
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#ccc',
                        'target-arrow-color': '#ccc',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier'
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

            layout: {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 50,
                rankSep: 100,
                edgeSep: 10
            }
        });

        if (isBridges) {
            const pairs = normalizeBridgePairs(bridgePairs);
            const bridgeNodeIds = new Set();
            const bridgeEdgeKeys = new Set();

            pairs.forEach(([sourceId, targetId]) => {
                bridgeNodeIds.add(sourceId);
                bridgeNodeIds.add(targetId);
                bridgeEdgeKeys.add(`${sourceId}::${targetId}`);
                bridgeEdgeKeys.add(`${targetId}::${sourceId}`);
            });

            cy.batch(() => {
                cy.nodes().forEach((node) => {
                    const id = node.data('id');
                    if (bridgeNodeIds.has(id)) {
                        node.addClass('bridge-highlight');
                    } else {
                        node.addClass('bridge-muted');
                    }
                });

                cy.edges().forEach((edge) => {
                    const edgeKey = `${edge.data('source')}::${edge.data('target')}`;
                    if (bridgeEdgeKeys.has(edgeKey)) {
                        edge.addClass('bridge-highlight');
                    } else {
                        edge.addClass('bridge-muted');
                    }
                });
            });
        }

        return () => {
            cy.destroy();
        };

    }, [nodes, edges, viewMode, bridgePairs, isBridges]);

    return (
        <div>
            <div className="graph-field-shell">
                <div ref={cyRef} className="graph-field" />
            </div>
            {!isBridges && (
                <div className="thermometr">
                    <ul className="thermometr-list">
                        <li>100</li>
                        <li>75</li>
                        <li>50</li>
                        <li>25</li>
                        <li>0</li>
                    </ul>
                </div>
            )}
        </div>
    );
};

export default CompareField;
