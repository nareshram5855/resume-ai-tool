import React, { useCallback, useState } from "react";

export default function FileUpload({ onUpload, loading }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      if (file && file.name.endsWith(".docx")) onUpload(file);
    },
    [onUpload]
  );

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onUpload(file);
  };

  return (
    <div
      className={`upload-zone ${dragActive ? "drag-active" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
    >
      <div className="upload-content">
        <span className="upload-icon">📄</span>
        <p>Drag & drop your DOCX resume here</p>
        <span className="upload-or">or</span>
        <label className="upload-btn">
          Browse Files
          <input
            type="file"
            accept=".docx"
            onChange={handleChange}
            hidden
            disabled={loading}
          />
        </label>
      </div>
      {loading && <div className="upload-loading">Parsing resume...</div>}
    </div>
  );
}
