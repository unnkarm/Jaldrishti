import React from "react";
import "./Navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="logo">🌊 Jaldrishti</div>
      <ul className="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/reports">Report</a></li>
        <li><a href="/about">Map</a></li>
      </ul>
      <button className="login-btn">Login</button>
    </nav>
  );
};

export default Navbar;
