import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import "./CompareAside.css"
import Button from "../../UI/Button/Button";


const CompareAside = () => {
    const [formats, setFormats] = useState([]);
    const [selected, setSelected] = useState('');
    const [downloading, setDownloading] = useState(false);
    const [reportDownloading, setReportDownloading] = useState(false);

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
            alert(`Ошибка при скачивании: ${error.message}`);
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

            <select className="formats-panel" value={selected} onChange={handleChange}>
                <option value="">Выберите формат</option>
                {formats.map((format, idx) => (
                    <option key={idx} value={format}>{format}</option>
                ))}
            </select>
            <Button
                type="button"
                onClick={() => downloadFile('download-graph', selected, `graph.${selected.toLowerCase()}`)}
                disabled={!selected || downloading}
            >
                {downloading ? '⏳' : 'Скачать граф'}
            </Button>

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