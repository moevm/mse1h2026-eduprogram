import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../Button/Button';
import NavbarSelect from "../../NavbarSelect/NavbarSelect";
import './CompareNavbar.css';

export default function CompareNavbar() {
    const navigate = useNavigate();

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
                    <svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.77611 7.45789e-06C5.70505 -0.003746 4.02307 1.67214 4.01932 3.74321C4.01557 5.81427 5.69145 7.49624 7.76252 7.5C9.83358 7.50375 11.5156 5.82786 11.5193 3.7568C11.5231 1.68573 9.84718 0.00376091 7.77611 7.45789e-06Z" fill="white"/>
                        <path d="M3.7589 9.49274C1.68784 9.48899 0.00586315 11.1649 0.0021097 13.2359L-4.38593e-05 14.4242C-0.00140896 15.1775 0.54331 15.8207 1.28648 15.9434C5.56403 16.6497 9.92783 16.6576 14.2079 15.9668C14.9515 15.8468 15.4986 15.2055 15.4999 14.4523L15.5021 13.264C15.5058 11.193 13.83 9.51099 11.7589 9.50724L11.418 9.50662C11.2335 9.50629 11.0501 9.53513 10.8747 9.59208L10.0086 9.87313C8.54549 10.348 6.96923 10.3451 5.50781 9.86497L4.64281 9.58079C4.46754 9.5232 4.28426 9.49369 4.09977 9.49336L3.7589 9.49274Z" fill="white"/>
                    </svg>
                </Button>

                <Button onClick={() => {}}>
                    Выйти
                </Button>
            </div>
        </nav>
    );
}