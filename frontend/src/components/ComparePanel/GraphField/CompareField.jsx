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
                        'background-color': 'data(color)',
                        'color': '#000',
                        'font-size': '10px',
                        'text-wrap': 'wrap',
                        'text-max-width': '80px',
                        'width': 'label',
                        'height': 'label',
                        'padding': '10px',
                        'shape': 'roundrectangle'
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