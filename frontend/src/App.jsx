import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage/LoginPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import WorkProgramPage from './pages/WorkProgramPage/WorkProgramPage';
import GraphPage from './pages/GraphPage/GraphPage';
import './assets/styles/global.css';
import MainPage from './pages/MainPage/MainPage';
import UploadProgram from './components/UploadProgram';
import ComparePage from "./pages/ComparePage/ComparePage";
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/work_program" element={<ProtectedRoute><WorkProgramPage/></ProtectedRoute>} />
        <Route path="/graph" element={<ProtectedRoute><GraphPage /></ProtectedRoute>} />
        <Route path="/main" element={<ProtectedRoute><MainPage/></ProtectedRoute>} />
        <Route path="/compare" element={<ProtectedRoute><ComparePage/></ProtectedRoute>}/>
        <Route path="/upload_programs" element={<ProtectedRoute><UploadProgram/></ProtectedRoute>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;