import React from 'react';
import { useNavigate } from 'react-router-dom';
import "./GraphAside.css"
import Button from "../../Button/Button";

const GraphAside = ({onExpandAll, onCollapseAll}) => {
    const navigate = useNavigate();

    return (
        <aside className="graph-aside">
            <Button type="button" onClick={() => { navigate('/main'); }}>
                Назад
            </Button>
            <Button type="button" onClick={onExpandAll}>
                Показать все
            </Button>
            <Button type="button" onClick={onCollapseAll}>
                Скрыть все
            </Button>
        </aside>
    );
};

export default GraphAside;