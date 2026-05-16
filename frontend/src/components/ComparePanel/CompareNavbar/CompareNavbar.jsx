import React from 'react';
import Button from '../../Button/Button';
import NavbarSelect from "../../NavbarSelect/NavbarSelect";
import { useLogout } from '../../../hooks/useLogout';
import './CompareNavbar.css';

export default function CompareNavbar({ onSectionChange }) {
    const handleLogout = useLogout();

    return (
        <nav className="graph-navbar">
            <div className="navbar-start">
                <div className="logo"></div>
            </div>

            <div className="navbar-end">
                <NavbarSelect
                    options={[
                        { label: "Граф", value: "graph", onClick: () => onSectionChange?.('graph') },
                        { label: "Мосты", value: "bridges", onClick: () => onSectionChange?.('bridges') },
                        { label: "Отчет", value: "report", onClick: () => onSectionChange?.('report') },
                    ]}
                />

                <Button className="navbar-logout-button" onClick={handleLogout}>
                    Выйти
                </Button>
            </div>
        </nav>
    );
}