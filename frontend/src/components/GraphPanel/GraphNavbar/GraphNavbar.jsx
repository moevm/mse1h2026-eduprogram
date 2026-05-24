import React from 'react';
import Button from '../../Button/Button';
import NavbarSelect from "../../NavbarSelect/NavbarSelect";
import { useLogout } from '../../../hooks/useLogout';
import './GraphNavbar.css';

export default function GraphNavbar({ onModeChange }) {
    const handleLogout = useLogout();

    return (
        <nav className="graph-navbar">
            <div className="navbar-start">
                <div className="logo"></div>
            </div>

            <div className="navbar-end">
                <NavbarSelect
                    options={[
                        { label: "Граф", value: "graph", onClick: (v) => onModeChange?.(v) },
                        { label: "Мосты", value: "bridges", onClick: (v) => onModeChange?.(v) },
                    ]}
                />

                <Button className="navbar-logout-button" onClick={handleLogout}>
                    Выйти
                </Button>
            </div>
        </nav>
    );
}