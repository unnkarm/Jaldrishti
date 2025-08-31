import React, { useState } from 'react';
import './Login.css';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [selectedRole, setSelectedRole] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add authentication logic here
    console.log('Login attempted with:', { role: selectedRole, email, password });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          
          <h1>Welcome to Jaldrishti</h1>
          <p>Sign in to continue</p>
        </div>

        <div className="role-selector">
          <button 
            className={`role-btn ${selectedRole === 'citizen' ? 'active' : ''}`}
            onClick={() => setSelectedRole('citizen')}
          >
            Citizen
          </button>
          <button 
            className={`role-btn ${selectedRole === 'admin' ? 'active' : ''}`}
            onClick={() => setSelectedRole('admin')}
          >
            Admin
          </button>
          <button 
            className={`role-btn ${selectedRole === 'analyst' ? 'active' : ''}`}
            onClick={() => setSelectedRole('analyst')}
          >
            Analyst
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="sign-in-btn">
            Sign in
          </button>
        </form>

        <div className="login-footer">
          <a href="#forgot-password">Forgot password?</a>
          <div className="signup-prompt">
            Need an account? <a href="#sign-up">Sign up</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;