import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage/LoginPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import GraphPage from './pages/GraphPage/GraphPage';
import './assets/styles/global.css';
import MainPage from './pages/MainPage/MainPage';
import ComparePage from "./pages/ComparePage/ComparePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/graph" element={<GraphPage />} />
        <Route path="/main" element={< MainPage/>} />
        <Route path="/compare" element={<ComparePage/>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;