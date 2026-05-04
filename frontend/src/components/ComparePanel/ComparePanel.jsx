import CompareNavbar from './CompareNavbar/CompareNavbar';
import CompareAside from './CompareAside/CompareAside';
import CompareField from './GraphField/CompareField';
import './ComparePanel.css';

const ComparePanel = ({ data }) => {

    if (!data) {
        return <div className="graph-panel-empty">Данные графа не загружены</div>;
    }

    const getColorByOverlap = (value) => {
        const v = Math.max(0, Math.min(100, Number(value)));
        const red = Math.round(255 * (1 - v / 100));
        const green = Math.round(255 * (v / 100));
        return `rgb(${red}, ${green}, 0)`;
    };

    const buildGraph = () => {
        const nodes = [];
        const edges = [];

        Object.entries(data).forEach(([programName, disciplines]) => {

            if (programName === "Recomendations") return;

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

    const { nodes, edges } = buildGraph();

    return (
        <>
            <CompareNavbar />
            <div className="graph-panel">
                <CompareAside />
                <CompareField nodes={nodes} edges={edges} />
            </div>
        </>
    );
};

export default ComparePanel;