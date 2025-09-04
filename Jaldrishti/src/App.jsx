import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import Navbar from "./Components/Navbar/Navbar";
import Home from "./Components/Home/Home";
import Dashboard from "./Components/Dashboard/Dashboard";
import Report from "./Components/Report/Report";
import Map from "./Components/Map/Map";
import Footer from "./Components/Footer/Footer";
import Login from "./Components/Login/Login";
import Signup from './Components/Login/Signup';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import "./App.css";

const AppContent = () => {
  const location = useLocation();
  const isAuthPage = ['/login', '/signup'].includes(location.pathname);

  return (
    <div className="app">
      {!isAuthPage && <Navbar />}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/report" element={<Report />} />
          <Route path="/map" element={<Map />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </main>
      {!isAuthPage && <Footer />}
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
