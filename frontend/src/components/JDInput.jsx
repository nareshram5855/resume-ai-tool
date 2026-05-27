import React, { useState } from "react";

export default function JDInput({ onSubmit, loading }) {
  const [mode, setMode] = useState("text");
  const [jdText, setJdText] = useState("");
  const [jdUrl, setJdUrl] = useState("");

  const handleSubmit = () => {
    if (mode === "text" && jdText.trim()) {
      onSubmit(jdText.trim(), null);
    } else if (mode === "url" && jdUrl.trim()) {
      onSubmit(null, jdUrl.trim());
    }
  };

  return (
    <div className="jd-input-section">
      <h3>Job Description</h3>
      <div className="jd-tabs">
        <button
          className={`tab ${mode === "text" ? "active" : ""}`}
          onClick={() => setMode("text")}
        >
          Paste Text
        </button>
        <button
          className={`tab ${mode === "url" ? "active" : ""}`}
          onClick={() => setMode("url")}
        >
          From URL
        </button>
      </div>

      {mode === "text" ? (
        <textarea
          className="jd-textarea"
          placeholder="Paste the job description here..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          rows={10}
        />
      ) : (
        <input
          className="jd-url-input"
          type="url"
          placeholder="https://example.com/job-posting"
          value={jdUrl}
          onChange={(e) => setJdUrl(e.target.value)}
        />
      )}

      <button
        className="analyze-btn"
        onClick={handleSubmit}
        disabled={loading || (mode === "text" ? !jdText.trim() : !jdUrl.trim())}
      >
        {loading ? "Analyzing..." : "Analyze & Update Resume"}
      </button>
    </div>
  );
}
