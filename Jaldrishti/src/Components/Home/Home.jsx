import React from "react";
import "./Home.css";

const Home = () => {
  return (
    <section className="home">
      <div className="home-content">
        <h1>Welcome to <span>Jaldrishti</span></h1>
        <p>
          An integrated platform for <strong>crowdsourced ocean hazard reporting </strong> 
          and <strong>social media analytics</strong>.  
          Empowering coastal communities with real-time insights and alerts.
        </p>
        <div className="buttons">
          <a href="/report" className="btn-primary">Report Hazard</a>
          <a href="/dashboard" className="btn-secondary">View Dashboard</a>
        </div>
      </div>
      
    </section>
  );
};

export default Home;
