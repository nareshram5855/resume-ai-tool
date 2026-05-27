import React from "react";
import { getDownloadUrl } from "../api";

export default function Download({ fileId }) {
  if (!fileId) return null;

  return (
    <div className="download-section">
      <a
        href={getDownloadUrl(fileId)}
        className="download-btn"
        download="updated_resume.docx"
      >
        Download Updated Resume
      </a>
    </div>
  );
}
