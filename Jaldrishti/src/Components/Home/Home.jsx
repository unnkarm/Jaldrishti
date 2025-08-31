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
          </div>
          
        </div>
      </div>

      <div className="buttons-container">
        <div className="buttons">
          <a href="/report" className="btn-primary">Report Hazard</a>
          <a href="/dashboard" className="btn-secondary">View Dashboard</a>
        </div>
      </div>
    </section>
  );
};

export default Home;
