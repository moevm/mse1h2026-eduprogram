import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ComparePanel from '../../components/ComparePanel/ComparePanel'
import "./ComparePage.css"

const ComparePage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [compareData, setCompareData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

        useEffect(() => {
        if (location.state?.data) {
            setCompareData(location.state.data);
            setLoading(false);
        }
    }, [location.state]);

    if (loading) {
        return (
            <main className="graph-page__main">
                <div className="graph-page__loading">Загрузка данных...</div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="graph-page__main">
                <div className="graph-page__loading">{error}</div>
                <button
                    type="button"
                    onClick={() => navigate('/main')}
                    style={{ marginTop: '16px' }}
                >
                    Перейти к списку программ
                </button>
            </main>
        );
    }

    return (
        <main className="graph-page__main">
            <ComparePanel data={compareData} />
        </main>
    );
};

export default ComparePage;