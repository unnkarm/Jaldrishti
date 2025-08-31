import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-newsletter">
        <h3>NEWSLETTER</h3>
        <div className="newsletter-form">
          <input type="email" placeholder="Enter email address" />
          <button type="submit">SUBMIT</button>
        </div>
      </div>

      <div className="footer-content">
        <div className="footer-section">
          <h4>Information</h4>
          <ul>
            <li><Link to="/about">About Us</Link></li>
            <li><Link to="/privacy">Privacy Policy</Link></li>
            <li><Link to="/terms">Terms & Conditions</Link></li>
            <li><Link to="/contact">Contact Us</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Services</h4>
          <ul>
            <li><Link to="/report">Report Hazard</Link></li>
            <li><Link to="/dashboard">View Analytics</Link></li>
            <li><Link to="/map">Hazard Map</Link></li>
            <li><Link to="/support">Support</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li><Link to="/documentation">Documentation</Link></li>
            <li><Link to="/api">API Access</Link></li>
            <li><Link to="/developers">Developer Info</Link></li>
            <li><Link to="/guidelines">Guidelines</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Jaldrishti</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/features">Features</Link></li>
            <li><Link to="/pricing">Pricing</Link></li>
            <li><Link to="/download">Download App</Link></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} All rights reserved | Jaldrishti - Water Hazard Management Platform</p>
      </div>
    </footer>
  );
};

export default Footer;