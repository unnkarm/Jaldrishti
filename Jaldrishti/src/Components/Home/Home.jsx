import React from "react";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import "./Home.css";

const Home = () => {
  return (
    <section className="home">
      <div className="hero-section">
        <div className="carousel-container">
          <Carousel
            autoPlay={true}
            infiniteLoop={true}
            interval={3000}
            showStatus={false}
            showThumbs={false}
          >
            <div>
              <img src="/src/assets/slide1.jpg" alt="Slide 1" />
            </div>
            <div>
              <img src="/src/assets/slide2.jpg" alt="Slide 2" />
            </div>
            <div>
              <img src="/src/assets/slide3.jpg" alt="Slide 3" />
            </div>
          </Carousel>
        </div>

        <div className="overlay">
          <div className="home-content">
            <h1>Welcome to Jaldrishti</h1>
            <div className="buttons">
              <a href="/report" className="btn-primary">Report Hazard</a>
              <a href="/dashboard" className="btn-secondary">View Dashboard</a>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2>Our Platform Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Citizen Reporting</h3>
            <p>Simple mobile-first interface for reporting water hazards with photo uploads and automatic GPS location</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Real-time Analytics</h3>
            <p>Interactive dashboards with map visualization, social media monitoring, and trend analysis</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI Intelligence</h3>
            <p>Smart assistant that analyzes patterns, sentiment, and provides actionable insights</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">👥</div>
            <h3>Multi-Role Access</h3>
            <p>Tailored interfaces for citizens, officials, and analysts with appropriate access controls</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🚨</div>
            <h3>Emergency Alerts</h3>
            <p>Automated hazard detection and notification system for rapid community response</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">✅</div>
            <h3>Verified Reports</h3>
            <p>Official validation system ensuring data accuracy and reliability for decision making</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Home;
