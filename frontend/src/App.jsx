import React, { useState } from "react";
import Navbar from "./components/Navbar";
import VideoPlayer from "./components/VideoPlayer";
import Sidebar from "./components/Sidebar";
import NLQBar from "./components/NLQBar";
import "./App.css";

/**
 * App Component
 * This is the root component that manages navigation and shared search state.
 * It is structured into two "Page Sections" that the user scrolls between.
 */
function App() {
  // --- STATE MANAGEMENT ---
  // Shared state for the search bar, used by both Page 1 and Page 2
  const [searchQuery, setSearchQuery] = useState("");
  const [frames, setFrames] = useState([]);

  // --- NAVIGATION LOGIC ---

  /**
   * Smooth scrolls the view back to the top Dashboard section.
   */
  const goBackUp = () => {
    const section = document.getElementById("dashboard-section");
    if (section) section.scrollIntoView({ behavior: "smooth" });
  };

  /**
   * Smooth scrolls the view down to the Analysis/Results section.
   * Triggered when a user presses 'Enter' in the NLQBar.
   */
  const goToResults = () => {
    const section = document.getElementById("results-section");
    if (section) section.scrollIntoView({ behavior: "smooth" });

    fetch("http://localhost:8000/ws/get_snaps")
      .then((res) => res.json())
      .then((data) => setFrames(data.snaps));
  };

  // useEffect(() => {}, [searchQuery]);

  return (
    <div className="app-container">
      {/* ==========================================
          PAGE 1: DASHBOARD SECTION
          Primary interface for live CCTV monitoring.
          ========================================== */}
      <div id="dashboard-section" className="page-section">
        <Navbar />

        <div className="main-layout">
          {/* Main video feed display */}
          <VideoPlayer />

          {/* Alerts and live event logs */}
          <Sidebar />
        </div>

        {/* Global Search Bar - Connected to shared state */}
        <NLQBar
          query={searchQuery}
          setQuery={setSearchQuery}
          onSearch={goToResults}
        />
      </div>

      {/* ==========================================
          PAGE 2: RESULTS SECTION
          Interface for AI-generated summaries and frame extraction.
          ========================================== */}
      <div id="results-section" className="page-section results-bg">
        {/* Results Header: Allows user to go back or refine query */}
        <div className="results-header">
          <button className="back-btn-small" onClick={goBackUp}>
            ← Back
          </button>

          <div className="results-search-container">
            <NLQBar
              query={searchQuery}
              setQuery={setSearchQuery}
              onSearch={goToResults}
            />
          </div>
        </div>

        {/* --- BACKEND INTEGRATION POINT --- 
            Developers: This container should be populated with data 
            fetched from the AI Backend based on 'searchQuery'.
        */}
        <div className="results-container">
          {/* AI Summary Text Area */}
          <div className="summary-section box">
            <h2>
              <b>Analysis for:</b>"{searchQuery}"
            </h2>
            <p className="summary-text">
              Based on the CCTV footage, the system identified the requested
              activity. The AI model has summarized the key events below.
            </p>
          </div>

          {/* Visual Evidence Area (Extracted Frames) */}
          <div className="frames-section">
            <h3 className="section-title">Extracted Frames</h3>
            <div className="frames-grid">
              {frames.length !== 0 ? (
                frames.map((f, i) => (
                  <img
                    key={i}
                    src={`data:image/jpeg;base64,${f}`}
                    alt="frame"
                    className="frame-card"
                    width={360}
                  />
                ))
              ) : (
                <>
                  {/* Developers: Replace these placeholders with <img> tags 
                    linked to backend-generated image URLs. */}
                  <div className="frame-card">
                    <span>Frame 1</span>
                  </div>
                  <div className="frame-card">
                    <span>Frame 2</span>
                  </div>
                  <div className="frame-card">
                    <span>Frame 3</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
