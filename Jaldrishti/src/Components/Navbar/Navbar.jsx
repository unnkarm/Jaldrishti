import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Navbar.css";
import logo from "../../assets/logo.png";

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/"><img 
            src={logo} 
            alt="Jaldrishti Logo" 
            style={{ height: "30px", width: "30px", display: "inline-block", marginRight: "8px",marginTop: "8px" }} 
          /> <div className="logo-text">Jaldrishti</div></Link>
      </div>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/report">Report</Link></li>
        <li><Link to="/map">Map</Link></li>
      </ul>
      <button className="login-btn" onClick={handleLogin}>Login</button>
    </nav>
  );
};

export default Navbar;
