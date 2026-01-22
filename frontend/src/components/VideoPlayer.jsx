export default function VideoPlayer() {
  return (
    <div className="video-container box" style={{ flex: 3 }}>
      <h2>CCTV Footage</h2>
      <div className="video-placeholder">
        {/* Later, you'll put your <video> tag here */}
        <p>Live Stream Feed</p>
      </div>
    </div>
  );
}