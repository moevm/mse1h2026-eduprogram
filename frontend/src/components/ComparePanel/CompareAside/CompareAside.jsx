import React from 'react';
import { useNavigate } from 'react-router-dom';
import "./CompareAside.css"
import Button from "../../Button/Button";

const CompareAside = () => {
    const navigate = useNavigate();

    return (
        <aside className="graph-aside">
            <Button type="button" onClick={() => { navigate('/main'); }}>
                Назад
            </Button>
            <Button type="button" >
                RDF
            </Button>
            <Button type="button" >
                PDF
            </Button>
            <Button type="button">
                DOCX
            </Button>
        </aside>
    );
};

export default CompareAside;