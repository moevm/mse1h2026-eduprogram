import React from 'react';
import Navbar from "../../components/Navbar/Navbar";
import "./RegisterPage.css"
import RegisterForm from "../../components/Register/RegisterForm";

function RegisterPage() {
  return (
    <>
        <Navbar/>
        <div className="register-container">
            <RegisterForm />
        </div>
    </>
  );
}

export default RegisterPage;