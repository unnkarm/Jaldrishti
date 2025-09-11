import React, { useState, useRef } from "react";
import './Report.css';

export default function JaldrishtiReport() {
  const [location, setLocation] = useState("");
  const [hazardType, setHazardType] = useState("");
  const [description, setDescription] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const inputFileRef = useRef(null);

  function handleFileChange(e) {
    const file = e?.target?.files && e.target.files[0];
    if (!file) {
      setImageFile(null);
      return;
    }
    setImageFile(file);
  }

  function handleSubmit() {
    console.log({ location, hazardType, description, imageFile });
    alert("Report submitted successfully!");
    
    // Reset form
    setLocation("");
    setHazardType("");
    setDescription("");
    setImageFile(null);
    if (inputFileRef.current) {
      inputFileRef.current.value = "";
    }
  }

  return (
    <div className="container">
      
      {/* Main Content */}
      <main className="main">
        <div className="form-container">
          <div className="form-card">
            <h1 className="form-title">
              Report Water Hazard
            </h1>

            {/* Location Field */}
            <div className="field">
              <label className="label">
                Location
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter location"
                className="input"
              />
            </div>

            {/* Hazard Type Field */}
            <div className="field">
              <label className="label">
                Type of Hazard
              </label>
              <div className="select-container">
                <select
                  value={hazardType}
                  onChange={(e) => setHazardType(e.target.value)}
                  className="select"
                >
                  <option value="">Select the type of hazard</option>
                  <option value="high-tide">High Tide/Coastal Flooding</option>
                  <option value="storm">Storm/Rough Seas</option>
                  <option value="tsunami">Tsunami Warning</option>
                  <option value="rip-current">Dangerous Rip Current</option>
                  <option value="marine-debris">Marine Debris</option>
                  <option value="oil-spill">Oil Spill</option>
                  <option value="algae-bloom">Algae Bloom</option>
                  <option value="shark-sighting">Shark Sighting</option>
                  <option value="jellyfish-swarm">Jellyfish Swarm</option>
                  <option value="other-hazard">Other Hazard</option>
                </select>
                <div className="select-arrow">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Description Field */}
            <div className="field">
              <label className="label">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the hazard in detail"
                className="textarea"
              />
            </div>

            {/* Upload Image Field */}
            <div className="field">
              <label className="label">
                Upload Image
              </label>
              <div className="file-upload">
                <label className="file-button">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span>Choose File</span>
                  <input
                    ref={inputFileRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="file-input"
                  />
                </label>
                <span className="file-status">
                  {imageFile ? imageFile.name : "No file chosen"}
                </span>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              className="submit-button"
            >
              Submit Report
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
