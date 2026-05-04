import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ComparePanel from '../../components/ComparePanel/ComparePanel'
import { fetchCompareData } from '../../services/api/graph';
import "./ComparePage.css"

const ComparePage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [compareData, setCompareData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        setCompareData({
            "Информатика": [
                {
                    "Алгоритмы": {
                        previousDisciplines: [],
                        topics: [
                            {
                                "Сортировки": [
                                    {
                                        "QuickSort": { overlapValue: 90 }
                                    },
                                    {
                                        "MergeSort": { overlapValue: 10 }
                                    }
                                ]
                            },
                            {
                                "Графы": [
                                    {
                                        "Dijkstra": { overlapValue: 60 }
                                    },
                                    {
                                        "BFS": { overlapValue: 85 }
                                    }
                                ]
                            }
                        ]
                    }
                },
            ],
            Recomendations: [
            ]
        });

        setLoading(false);
    }, []);

    // useEffect(() => {
    //     const loadCompareData = async () => {
    //         const userId = Number(localStorage.getItem('userId'));
    //         const params = new URLSearchParams(location.search);
    //         const folder = params.get('folder');
    //
    //         if (!Number.isInteger(userId) || userId <= 0) {
    //             setError('Пользователь не авторизован. Войдите заново.');
    //             setLoading(false);
    //             return;
    //         }
    //
    //         if (!folder) {
    //             setError('Программа не выбрана. Откройте список программ на главной странице.');
    //             setLoading(false);
    //             return;
    //         }
    //
    //         try {
    //             const data = await fetchCompareData(userId, folder);
    //             setCompareData(data);
    //             setError('');
    //         } catch (err) {
    //             console.error('Failed to fetch graph data:', err);
    //             setError('Не удалось загрузить выбранную программу с сервера.');
    //             setCompareData(null);
    //         } finally {
    //             setLoading(false);
    //         }
    //     };
    //
    //     loadCompareData();
    // }, [location.search]);

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