import React from 'react';
import TreeEditor from '../../components/TreeEditor';
import './WorkProgramPage.css';
import Navbar from "../../components/Navbar/Navbar";

const WorkProgramPage = () => {
  return (
    <>
        <Navbar/>
        <div className="work-program-page">
            <div className="page-header">
                <h2>Рабочая программа</h2>
                <nav className="breadcrumbs">
                    <span>Главная</span>
                    <span className="separator">/</span>
                    <span className="current">Рабочая программа</span>
                </nav>
            </div>

            <div className="page-content">
                <TreeEditor />
            </div>
        </div>
    </>
  );
};

export default WorkProgramPage;