import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage/LoginPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import GraphPage from './pages/GraphPage/GraphPage';
import './assets/styles/global.css';
import MainPage from './pages/MainPage/MainPage';
import ComparePage from "./pages/ComparePage/ComparePage";
import { NotificationProvider } from './components/UI/Notification/Notification';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <NotificationProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/graph" element={<ProtectedRoute><GraphPage /></ProtectedRoute>} />
          <Route path="/main" element={<ProtectedRoute><MainPage/></ProtectedRoute>} />
          <Route path="/compare" element={<ProtectedRoute><ComparePage/></ProtectedRoute>}/>
        </Routes>
      </BrowserRouter>
    </NotificationProvider>
  );
}

export default App;
