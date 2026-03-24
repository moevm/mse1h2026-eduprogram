import React from 'react';
import GraphNavbar from "./GraphNavbar/GraphNavbar";
import GraphAside from "./GraphAside/GraphAside";
import GraphField from "./GraphField/GraphField";
import "./GraphPanel.css"

export default function GraphPanel() {
    return (
        <>
            <GraphNavbar/>
            <div className="graph-panel">
                <GraphAside/>
                <GraphField/>
            </div>
        </>
    );
};