import React, { useMemo, useState } from 'react';
import CompareNavbar from './CompareNavbar/CompareNavbar';
import CompareAside from './CompareAside/CompareAside';
import CompareField from './CompareField/CompareField';
import './ComparePanel.css';
import Button from "../Button/Button";

const ComparePanel = ({ data }) => {
    const [visible, setVisible] = useState(false);


    const recommendations = Array.isArray(data?.Recomendations)
        ? data.Recomendations
        : [];

    const getColorByOverlap = (value) => {
        const v = Math.max(0, Math.min(100, Number(value)));
        let red, green;
        if (v <= 50) {
            red = 255;
            green = Math.round(255 * (v / 50));
        } else {
            red = Math.round(255 * (1 - (v - 50) / 50));
            green = 255;
        }
        return `rgb(${red}, ${green}, 0)`;
    };

    const buildGraph = () => {
        const nodes = [];
        const edges = [];

        Object.entries(data).forEach(([programName, disciplines]) => {
            if (programName === "Recomendations") {
                return;
            }

            nodes.push({
                data: {
                    id: programName,
                    label: programName,
                    color: '#cccccc'
                }
            });

            disciplines.forEach((disciplineObj) => {
                Object.entries(disciplineObj).forEach(([disciplineName, disciplineData]) => {

                    const disciplineId = `${programName}-${disciplineName}`;
                    nodes.push({
                        data: {
                            id: disciplineId,
                            label: disciplineName,
                            color: '#999999'
                        }
                    });

                    edges.push({
                        data: {
                            source: programName,
                            target: disciplineId
                        }
                    });

                    disciplineData.topics.forEach((topicObj) => {
                        Object.entries(topicObj).forEach(([topicName, subtopics]) => {

                            const topicId = `${disciplineId}-${topicName}`;

                            nodes.push({
                                data: {
                                    id: topicId,
                                    label: topicName,
                                    color: '#666666'
                                }
                            });

                            edges.push({
                                data: {
                                    source: disciplineId,
                                    target: topicId
                                }
                            });

                            subtopics.forEach((subtopicObj) => {
                                Object.entries(subtopicObj).forEach(([subtopicName, subtopicData]) => {

                                    const overlap = Number(subtopicData.overlapValue);
                                    const subtopicId = `${topicId}-${subtopicName}`;

                                    nodes.push({
                                        data: {
                                            id: subtopicId,
                                            label: `${subtopicName} (${overlap})`,
                                            color: getColorByOverlap(overlap),
                                            overlap
                                        }
                                    });

                                    edges.push({
                                        data: {
                                            source: topicId,
                                            target: subtopicId
                                        }
                                    });

                                });
                            });

                        });
                    });

                });
            });

        });

        return { nodes, edges };
    };

    const { nodes, edges } = useMemo(() => {
        if (!data) return { nodes: [], edges: [] };
        return buildGraph();
    }, [data]);

    if (!data) {
        return <div className="graph-panel-empty">Данные графа не загружены</div>;
    }

    return (
        <>
            <CompareNavbar />
            <div className="graph-panel">
                <CompareAside showRecommendations={() => setVisible(prev => !prev)} />
                <CompareField nodes={nodes} edges={edges} />
            </div>
            {visible && (
                <div className="recommendations-drawer">
                    <Button onClick={() => setVisible(prev => !prev)}>
                        Скрыть рекомендации
                    </Button>
                    <div>
                        <h3>Рекомендации</h3>
                        {recommendations.length === 0 ? (
                            <p>Нет рекомендаций</p>
                        ) : (
                            <ul>
                                {recommendations.map((rec, index) => (
                                    <li key={index}>{rec || '—'}</li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            )}
        </>
    );
};

export default ComparePanel;