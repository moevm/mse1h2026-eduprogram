import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import "./CompareAside.css"
import Button from "../../UI/Button/Button";
import IconButton from "../../UI/IconButton/IconButton";
import { useNotification } from "../../UI/Notification/Notification";


const CompareAside = ({
    onSearch,
    onSearchClear,
    onSearchPrev,
    onSearchNext,
    hasSearchResults = false,
    hasMultipleSearchResults = false,
    searchResultIndex = 0,
    searchResultCount = 0,
    searchMessage = ''
}) => {
    const notify = useNotification();
    const [formats, setFormats] = useState([]);
    const [selected, setSelected] = useState('');
    const [downloading, setDownloading] = useState(false);
    const [reportDownloading, setReportDownloading] = useState(false);
    const [searchValue, setSearchValue] = useState('');
    const inputRef = useRef(null);

    useEffect(() => {
        const onKeyDown = (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'f') {
                e.preventDefault();
                if (inputRef.current) {
                    inputRef.current.focus();
                    inputRef.current.select();
                }
            }
        };

        document.addEventListener('keydown', onKeyDown);
        return () => document.removeEventListener('keydown', onKeyDown);
    }, []);

    const domain = process.env.REACT_APP_API_URL_GET_PROGRAMMS || process.env.REACT_APP_API_URL || 'localhost:8000';
    const API_BASE_URL = domain.startsWith('http') ? domain : `http://${domain}`;

    const navigate = useNavigate();

    useEffect(() => {
        fetch(`${API_BASE_URL}/get-available-export-formats`)
            .then(res => res.json())
            .then(data => {
                setFormats(data["available-export-formats"] || []);
            })
            .catch(err => console.error('Ошибка:', err));
      
    }, [API_BASE_URL]);

    const handleChange = (e) => {
        const value = e.target.value;
        setSelected(value);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        onSearch?.(searchValue);
    };

    const handleClear = () => {
        setSearchValue('');
        onSearchClear?.();
    };

    const downloadFile = async (endpoint, format, defaultFilename) => {
        setDownloading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/${endpoint}?format=${format}&graphId=${localStorage.getItem('graph_id')}`, {
                method: 'GET',
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            let filename = defaultFilename;
            const contentDisposition = response.headers.get('Content-Disposition');
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            console.log(`Файл ${filename} успешно скачан`);
        } catch (error) {
            console.error('Ошибка при скачивании:', error);
            notify(`Ошибка при скачивании: ${error.message}`, { type: 'error' });
        } finally {
            setDownloading(false);
        }
    };

    return (
        <aside className="graph-aside">
            <Button type="button" onClick={() => { navigate('/main'); }}>
                Назад
            </Button>

            <div className="graph-aside__divider" />

            <form className="graph-aside__search" onSubmit={handleSubmit}>
                <label className="graph-aside__search-label" htmlFor="compare-node-search">
                    Поиск вершины
                </label>
                <input
                    id="compare-node-search"
                    ref={inputRef}
                    className="graph-aside__search-input"
                    type="text"
                    value={searchValue}
                    onChange={(event) => setSearchValue(event.target.value)}
                    placeholder="Введите подстроку"
                />
                <div className="graph-aside__search-actions">
                    <Button type="submit">Найти</Button>
                    <Button type="button" onClick={handleClear}>Сбросить</Button>
                </div>
            </form>

            <div
                className="graph-aside__search-message"
                role="status"
                aria-hidden={!searchMessage}
            >
                {searchMessage}
            </div>

            {hasMultipleSearchResults ? (
                <div className="graph-aside__search-nav">
                    <Button type="button" onClick={onSearchPrev} disabled={!hasSearchResults}>
                        ←
                    </Button>
                    <div className="graph-aside__search-counter">
                        {searchResultIndex + 1} / {searchResultCount}
                    </div>
                    <Button type="button" onClick={onSearchNext} disabled={!hasSearchResults}>
                        →
                    </Button>
                </div>
            ) : null}

            <div className="graph-aside__divider" />

            <div className="graph-download-row">
                <select className="formats-panel" value={selected} onChange={handleChange}>
                    <option value="">Выберите формат</option>
                    {formats.map((format, idx) => (
                        <option key={idx} value={format}>{format}</option>
                    ))}
                </select>
                <IconButton
                    type="button"
                    onClick={() => downloadFile('download-graph', selected, `graph.${selected.toLowerCase()}`)}
                    disabled={!selected || downloading}
                    title="Скачать граф"
                >
                    {downloading ? '⏳' : '⬇️'}
                </IconButton>
            </div>

            <div className="graph-aside__divider" />

            <div className="report-download-section">
                <Button
                    type="button"
                    onClick={() => downloadFile('download-report', 'pdf', 'report.pdf')}
                    disabled={downloading}
                >
                    PDF
                </Button>

                <Button
                    type="button"
                    onClick={() => downloadFile('download-report', 'docx', 'report.docx')}
                    disabled={downloading}
                >
                    DOCX
                </Button>
            </div>

        </aside>
    );
};

export default CompareAside;