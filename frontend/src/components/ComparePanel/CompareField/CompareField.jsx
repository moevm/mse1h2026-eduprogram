import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import './CompareField.css'

cytoscape.use(dagre);

const CompareField = ({ nodes, edges, searchResults = [], currentSearchNodeId = null }) => {
    const cyRef = useRef(null);

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
                    selector: 'node.search-match',
                    style: {
                        'border-color': '#1976d2',
                        'border-width': 4,
                        'overlay-color': '#1976d2',
                        'overlay-opacity': 0.08,
                        'z-index': 998
                    }
                },
                {
                    selector: 'node.search-result',
                    style: {
                        'border-color': '#d32f2f',
                        'border-width': 6,
                        'overlay-color': '#d32f2f',
                        'overlay-opacity': 0.1,
                        'z-index': 1000
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

        cyRef.current = cy;

        return () => {
            cy.destroy();
            cyRef.current = null;
        };

    }, [nodes, edges]);

    useEffect(() => {
        if (!cyRef.current) return;

        const cy = cyRef.current;

        if (!searchResults.length) {
            cy.nodes().removeClass('search-result search-match');
            return;
        }

        cy.nodes().removeClass('search-result search-match');

        searchResults.forEach((nodeId) => {
            const node = cy.getElementById(nodeId);
            if (node.nonempty()) {
                node.addClass('search-match');
            }
        });

        if (!currentSearchNodeId) return;

        const searchNode = cy.getElementById(currentSearchNodeId);

        if (!searchNode.nonempty()) return;

        searchNode.removeClass('search-match');
        searchNode.addClass('search-result');
        cy.animate({
            fit: { eles: searchNode, padding: 120 },
            duration: 350,
            easing: 'ease-in-out'
        });
    }, [searchResults, currentSearchNodeId, nodes, edges]);

    return (
        <div>
            <div className="graph-field-shell">
                <div ref={cyRef} className="graph-field" />
            </div>
            <div className="thermometr">
                <ul className="thermometr-list">
                    <li>100</li>
                    <li>75</li>
                    <li>50</li>
                    <li>25</li>
                    <li>0</li>
                </ul>
            </div>
        </div>
    );
};

export default CompareField;