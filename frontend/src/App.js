import React, { useState } from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";
import JDInput from "./components/JDInput";
import Results from "./components/Results";
import Summaries from "./components/Summaries";
import Download from "./components/Download";
import { uploadResume, deleteResume, analyzeResume } from "./api";

function App() {
  const [fileId, setFileId] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [summaries, setSummaries] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    setAnalysis(null);
    setSummaries(null);
    try {
      const data = await uploadResume(file);
      setFileId(data.file_id);
      setFileName(data.filename);
      setResumeData(data.resume_data);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!fileId) return;
    try {
      await deleteResume(fileId);
      setFileId(null);
      setFileName(null);
      setResumeData(null);
      setAnalysis(null);
      setSummaries(null);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Delete failed");
    }
  };

  const handleAnalyze = async (jdText, jdUrl) => {
    setAnalyzing(true);
    setError(null);
    try {
      const data = await analyzeResume(fileId, jdText, jdUrl);
      setAnalysis(data.analysis);
      setSummaries(data.summaries);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Resume Updater</h1>
        <p>Upload your resume, provide a job description, and get an optimized resume</p>
      </header>

      <main className="app-main">
        {!resumeData ? (
          <FileUpload onUpload={handleUpload} loading={uploading} />
        ) : (
          <div className="resume-preview">
            <div className="resume-preview-header">
              <h3>Uploaded Resume</h3>
              <div className="resume-actions">
                <button className="replace-btn" onClick={handleDelete}>
                  Remove & Upload New
                </button>
              </div>
            </div>

            <div className="resume-filename">{fileName}</div>

            <div className="resume-details">
              {resumeData.summary && (
                <div className="detail-block">
                  <h4>Summary</h4>
                  <p>{resumeData.summary}</p>
                </div>
              )}

              <div className="detail-block">
                <h4>Skills ({resumeData.skills?.length || 0})</h4>
                <div className="skills-preview">
                  {resumeData.skills?.length > 0 ? (
                    resumeData.skills.map((s, i) => (
                      <span key={i} className="skill-tag">{s}</span>
                    ))
                  ) : (
                    <span className="no-data">No skills detected</span>
                  )}
                </div>
              </div>

              <div className="detail-block">
                <h4>Experience ({resumeData.experience?.length || 0} sections)</h4>
                {resumeData.experience?.length > 0 ? (
                  resumeData.experience.map((exp, i) => (
                    <div key={i} className="exp-preview">
                      <strong>{exp.client}</strong>
                      {exp.role && <span className="exp-role"> — {exp.role}</span>}
                      {exp.duration && <span className="exp-duration"> ({exp.duration})</span>}
                      <ul>
                        {exp.points?.slice(0, 3).map((p, j) => (
                          <li key={j}>{p}</li>
                        ))}
                        {exp.points?.length > 3 && (
                          <li className="more-points">...and {exp.points.length - 3} more</li>
                        )}
                      </ul>
                    </div>
                  ))
                ) : (
                  <span className="no-data">No experience sections detected</span>
                )}
              </div>

              {resumeData.education && (
                <div className="detail-block">
                  <h4>Education</h4>
                  <p>{resumeData.education}</p>
                </div>
              )}

              {resumeData.raw_text && (
                <div className="detail-block warning-block">
                  <h4>Parser Warning</h4>
                  <p>Could not detect structured sections. Raw text extracted:</p>
                  <pre className="raw-text">{resumeData.raw_text.substring(0, 500)}...</pre>
                </div>
              )}
            </div>
          </div>
        )}

        {error && <div className="error-msg">{error}</div>}

        {fileId && <JDInput onSubmit={handleAnalyze} loading={analyzing} />}

        {analysis && <Results analysis={analysis} />}
        {summaries && <Summaries summaries={summaries} />}
        {analysis && <Download fileId={fileId} />}
      </main>
    </div>
  );
}

export default App;
