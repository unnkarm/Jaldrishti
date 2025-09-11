import React from "react";
import { motion } from "framer-motion";
import "./Home.css";

const Home = () => {
  return (
    <div 
      className="home"
      
    >
      <div className="hero-section">
        <motion.div 
          className="content-box"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="hero-content">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              Welcome to Jal Drishti!
            </motion.h1>
            <motion.p
              className="hero-description"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              Monitor water hazards in real-time with our comprehensive safety
              platform. Get instant alerts, track current conditions, and contribute to
              water safety across Indian waters.
            </motion.p>
            <motion.button
              className="get-started-btn"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
            </motion.button>
          </div>

          <motion.div
            className="live-data-container"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <div className="live-data-header">
              <motion.span
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                ⚡
              </motion.span>
              <h3>Live Water Data</h3>
            </div>
            <motion.div 
              className="stats-grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              {/* Your existing stats content */}
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      <motion.div
        className="how-to-use"
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <motion.h2>How to Use the Platform</motion.h2>
        
      </motion.div>

      <div className="info-rows">
        <motion.div 
          className="info-row"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h3>Real-time Monitoring</h3>
          <p>Our advanced monitoring system provides up-to-the-minute data on water conditions across India. Using state-of-the-art sensors and satellite technology, we track water levels, flow rates, and potential hazards to ensure you have the most accurate information available.</p>
        </motion.div>

        <motion.div 
          className="info-row"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h3>Community-Driven Alerts</h3>
          <p>Join a network of active citizens contributing to water safety. Our platform enables users to report hazards, verify conditions, and share critical updates. Together, we create a more responsive and effective water monitoring system.</p>
        </motion.div>

        <motion.div 
          className="info-row"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h3>Data-Driven Decision Making</h3>
          <p>Transform raw data into actionable insights. Our analytics tools help authorities and communities make informed decisions about water management, emergency response, and infrastructure planning.</p>
        </motion.div>
      </div>
    </div>
  );
};

export default Home;
