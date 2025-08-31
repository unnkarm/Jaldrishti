import React from 'react';
import './Report.css';

const Report = () => {
  return (
    <div className="report">
      <h1>Report Water Hazard</h1>
      <form className="report-form">
        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input type="text" id="location" name="location" placeholder="Enter location" />
        </div>

        <div className="form-group">
          <label htmlFor="hazardType">Type of Hazard</label>
          <select id="hazardType" name="hazardType">
            <option value="">Select hazard type</option>
            <option value="flooding">Flooding</option>
            <option value="waterLogging">Water Logging</option>
            <option value="contamination">Water Contamination</option>
            <option value="leakage">Pipeline Leakage</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea 
            id="description" 
            name="description" 
            placeholder="Describe the hazard in detail"
            rows="4"
          ></textarea>
        </div>

        <div className="form-group">
          <label htmlFor="image">Upload Image</label>
          <input type="file" id="image" name="image" accept="image/*" />
        </div>

        <button type="submit" className="submit-btn">Submit Report</button>
      </form>
    </div>
  );
};

export default Report;