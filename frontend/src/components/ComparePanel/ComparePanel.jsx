import React, { useMemo, useState } from 'react';
import CompareNavbar from './CompareNavbar/CompareNavbar';
import CompareAside from './CompareAside/CompareAside';
import CompareField from './CompareField/CompareField';
import './ComparePanel.css';

const ComparePanel = ({ data }) => {
    const [activeSection, setActiveSection] = useState('graph');
    const [searchResults, setSearchResults] = useState([]);
    const [searchIndex, setSearchIndex] = useState(0);
    const [searchMessage, setSearchMessage] = useState('');

    const recommendations = Array.isArray(data?.Recomendations)
        ? data.Recomendations
        : [];

    const toEntriesArray = (value) => {
        if (Array.isArray(value)) {
            return value;
        }

        if (value && typeof value === 'object') {
            return Object.entries(value).map(([key, nestedValue]) => ({ [key]: nestedValue }));
        }

        return [];
    };

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
                    searchLabel: programName,
                    color: '#cccccc'
                }
            });

            toEntriesArray(disciplines).forEach((disciplineObj) => {
                Object.entries(disciplineObj).forEach(([disciplineName, disciplineData]) => {
                    const topics = toEntriesArray(disciplineData?.topics);

                    const disciplineId = `${programName}-${disciplineName}`;
                    nodes.push({
                        data: {
                            id: disciplineId,
                            label: disciplineName,
                            searchLabel: disciplineName,
                            color: '#999999'
                        }
                    });

                    edges.push({
                        data: {
                            source: programName,
                            target: disciplineId
                        }
                    });

                    topics.forEach((topicObj) => {
                        Object.entries(topicObj).forEach(([topicName, topicData]) => {
                            const normalizedSubtopics = toEntriesArray(topicData?.subtopics ?? topicData);

                            const topicId = `${disciplineId}-${topicName}`;

                            nodes.push({
                                data: {
                                    id: topicId,
                                    label: topicName,
                                    searchLabel: topicName,
                                    color: '#666666'
                                }
                            });

                            edges.push({
                                data: {
                                    source: disciplineId,
                                    target: topicId
                                }
                            });

                            normalizedSubtopics.forEach((subtopicObj) => {
                                Object.entries(subtopicObj).forEach(([subtopicName, subtopicData]) => {

                                    const overlap = Number(subtopicData.overlapValue);
                                    const subtopicId = `${topicId}-${subtopicName}`;

                                    nodes.push({
                                        data: {
                                            id: subtopicId,
                                            label: `${subtopicName} (${overlap})`,
                                            searchLabel: subtopicName,
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

    const handleSearch = (query) => {
        const normalizedQuery = query.trim();

        if (!normalizedQuery) {
            setSearchResults([]);
            setSearchIndex(0);
            setSearchMessage('Введите подстроку для поиска.');
            return;
        }

        const lowerQuery = normalizedQuery.toLowerCase();
        const matchedNodes = nodes.filter((node) => (node.data?.searchLabel || node.data?.label || '').toLowerCase().includes(lowerQuery));

        if (!matchedNodes.length) {
            setSearchResults([]);
            setSearchIndex(0);
            setSearchMessage(`Вершина по подстроке «${normalizedQuery}» не найдена.`);
            return;
        }

        setSearchResults(matchedNodes.map((node) => node.data.id));
        setSearchIndex(0);
        setSearchMessage(
            matchedNodes.length > 1
                ? `Найдено ${matchedNodes.length} вершин. Показана 1 из ${matchedNodes.length}: ${matchedNodes[0].data.label}`
                : `Найдена вершина: ${matchedNodes[0].data.label}`
        );
    };

    const handleSearchNavigate = (direction) => {
        if (searchResults.length <= 1) return;

        setSearchIndex((prev) => {
            const nextIndex = direction === 'prev'
                ? (prev - 1 + searchResults.length) % searchResults.length
                : (prev + 1) % searchResults.length;
            const activeNode = nodes.find((node) => node.data.id === searchResults[nextIndex]);

            if (activeNode) {
                setSearchMessage(`Найдено ${searchResults.length} вершин. Показана ${nextIndex + 1} из ${searchResults.length}: ${activeNode.data.label}`);
            }

            return nextIndex;
        });
    };

    const handleSearchClear = () => {
        setSearchResults([]);
        setSearchIndex(0);
        setSearchMessage('');
    };

    const currentSearchNodeId = searchResults.length > 0 ? searchResults[searchIndex] : null;

    if (!data) {
        return <div className="graph-panel-empty">Данные графа не загружены</div>;
    }

    const handleSectionChange = (section) => {
        setActiveSection(section);
    };

    return (
        <>
            <CompareNavbar onSectionChange={handleSectionChange} />
            <div className="graph-panel">
                <CompareAside
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
                {activeSection === 'report' ? (
                    <div className="report-view">
                        <article className="report-document">
                            <h1 className="report-document__title">Рекомендации</h1>
                            {recommendations.length === 0 ? (
                                <p className="report-document__empty">Нет рекомендаций</p>
                            ) : (
                                <ol className="report-document__list">
                                    {recommendations.map((rec, index) => (
                                        <li key={index} className="report-document__item">
                                            {rec || '—'}
                                        </li>
                                    ))}
                                </ol>
                            )}
                        </article>
                    </div>
                ) : (
                    <CompareField nodes={nodes} edges={edges} searchResults={searchResults} currentSearchNodeId={currentSearchNodeId} />
                )}
            </div>
        </>
    );
};

export default ComparePanel;