import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import './CompareField.css'

cytoscape.use(dagre);

const CompareField = ({ nodes, edges }) => {
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

        return () => {
            cy.destroy();
        };

    }, [nodes, edges]);

    return (
        <div className="graph-field-shell">
            <div ref={cyRef} className="graph-field" />
        </div>
    );
};

export default CompareField;