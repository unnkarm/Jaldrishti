import React from 'react';
import './Map.css';

const Map = () => {
  return (
    <div className="map-container">
      <h1>Water Hazard Map</h1>
      <div className="map-wrapper">
        {/* TODO: Implement Google Maps or Leaflet integration */}
        <div className="map-placeholder">
          <p>Map will be integrated here</p>
        </div>
      </div>
      <div className="map-legend">
        <h3>Legend</h3>
        <div className="legend-item">
          <span className="legend-dot flooding"></span>
          <p>Flooding</p>
        </div>
        <div className="legend-item">
          <span className="legend-dot water-logging"></span>
          <p>Water Logging</p>
        </div>
        <div className="legend-item">
          <span className="legend-dot contamination"></span>
          <p>Water Contamination</p>
        </div>
        <div className="legend-item">
          <span className="legend-dot leakage"></span>
          <p>Pipeline Leakage</p>
        </div>
      </div>
    </div>
  );
};

export default Map;