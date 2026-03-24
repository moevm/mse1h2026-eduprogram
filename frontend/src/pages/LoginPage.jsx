import React from 'react';
import LoginForm from '../components/LoginForm';
import Navbar from "../components/Navbar";

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