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
    onSearch,
    onSearchClear,
    onSearchPrev,
    onSearchNext,
    hasSearchResults = false,
    hasMultipleSearchResults = false,
    searchResultIndex = 0,
    searchResultCount = 0,
    searchMessage = '',
}) => {
    const navigate = useNavigate();
    const [searchValue, setSearchValue] = React.useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        onSearch?.(searchValue);
    };

    const handleClear = () => {
        setSearchValue('');
        onSearchClear?.();
    };

    return (
        <aside className="graph-aside">
            <Button type="button" onClick={() => { navigate('/main'); }}>
                Назад
            </Button>

            <div className="graph-aside__divider" />

            <form className="graph-aside__search" onSubmit={handleSubmit}>
                <label className="graph-aside__search-label" htmlFor="graph-node-search">
                    Поиск вершины
                </label>
                <input
                    id="graph-node-search"
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
