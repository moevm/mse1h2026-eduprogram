import React from 'react';
import LoginForm from '../../components/Login/LoginForm';
import Navbar from "../../components/Navbar/Navbar";
import "./LoginPage.css"

function LoginPage() {
  return (
    <>
        <Navbar/>
        <div className="login-page">
            <LoginForm />
        </div>
    </>
  );
}

export default LoginPage;