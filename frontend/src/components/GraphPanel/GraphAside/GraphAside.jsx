import React from 'react';
import { useNavigate } from 'react-router-dom';
import "./GraphAside.css"
import Button from "../../Button/Button";

const GraphAside = () => {
    const navigate = useNavigate();

    return (
        <aside className="graph-aside">
        <Button 
          type="button"
          onClick={() => { navigate('/main'); }}
        >
            Программы с сервера
        </Button>
        <Button 
          type="button"
          onClick={() => { navigate('/work_program'); }}
        >
            Ввод рабочей программы
        </Button>
        </aside>
    );
};

export default GraphAside;