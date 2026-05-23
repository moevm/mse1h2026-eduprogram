import React from 'react';
import { useNavigate } from 'react-router-dom';
import "./GraphAside.css"
import Button from "../../UI/Button/Button";

const GraphAside = ({
    onExpandAll,
    onCollapseAll,
    onHideSelected,
    onShowFromSelected,
    hasSelection = false,
}) => {
    const navigate = useNavigate();

    return (
        <aside className="graph-aside">
            <Button type="button" onClick={() => { navigate('/main'); }}>
                Назад
            </Button>

            <div className="graph-aside__divider" />

            <Button type="button" onClick={onExpandAll}>
                Показать все
            </Button>
            <Button type="button" onClick={onCollapseAll}>
                Скрыть все
            </Button>

            <div className="graph-aside__divider" />

            <Button
                type="button"
                onClick={onShowFromSelected}
                disabled={!hasSelection}
            >
                Показать выделенные
            </Button>
            <Button
                type="button"
                onClick={onHideSelected}
                disabled={!hasSelection}
            >
                Скрыть выделенные
            </Button>
        </aside>
    );
};

export default GraphAside;
