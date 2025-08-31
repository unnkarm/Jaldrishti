import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1>Water Hazard Dashboard</h1>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Total Reports</h3>
          <p className="stat">156</p>
        </div>
        <div className="dashboard-card">
          <h3>Active Hazards</h3>
          <p className="stat">42</p>
        </div>
        <div className="dashboard-card">
          <h3>Resolved Issues</h3>
          <p className="stat">114</p>
        </div>
        <div className="dashboard-card">
          <h3>Response Time</h3>
          <p className="stat">24h</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;