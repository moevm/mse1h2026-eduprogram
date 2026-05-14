import React from 'react';
import Button from '../../Button/Button';
import NavbarSelect from "../../NavbarSelect/NavbarSelect";
import './GraphNavbar.css';

export default function GraphNavbar() {
    return (
        <nav className="graph-navbar">
            <div className="navbar-start">
                <div className="logo"></div>
            </div>

            <div className="navbar-end">
                <NavbarSelect
                    options={[
                        { label: "Граф", value: "graph", onClick: (v) => console.log(v) },
                        { label: "Мосты", value: "bridges", onClick: (v) => console.log(v) },
                        { label: "Отчет", value: "report", onClick: (v) => console.log(v) },
                    ]}
                />

                <Button onClick={() => {}}>
                    Выйти
                </Button>
            </div>
        </nav>
    );
}