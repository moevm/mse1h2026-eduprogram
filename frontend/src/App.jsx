import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import WorkProgramPage from './pages/WorkProgramPage';
import GraphPage from "./pages/GraphPage/GraphPage";
import "./assets/styles/global.css"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<GraphPage/>} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/work_program" element={< WorkProgramPage/>} />
        <Route path="/graph" element={<GraphPage/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;