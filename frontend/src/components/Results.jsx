import React from "react";

export default function Results({ analysis }) {
  if (!analysis) return null;

  const { matched_points, missing_points, missing_skills } = analysis;

  return (
    <div className="results-section">
      <h3>Analysis Results</h3>

      <div className="results-grid">
        <div className="results-col matched">
          <h4>Matched Points ({matched_points.length})</h4>
          {matched_points.map((mp, i) => (
            <div key={i} className="result-card matched-card">
              <span className="client-tag">{mp.client}</span>
              <p className="point-text">{mp.point}</p>
              <p className="match-text">Matches: {mp.jd_match}</p>
            </div>
          ))}
        </div>

        <div className="results-col gaps">
          <h4>Gaps & Suggestions ({missing_points.length})</h4>
          {missing_points.map((mp, i) => (
            <div key={i} className="result-card gap-card">
              <span className="client-tag">{mp.client}</span>
              <p className="point-text">+ {mp.suggested_point}</p>
              <p className="match-text">For: {mp.jd_requirement}</p>
            </div>
          ))}

          {missing_skills.length > 0 && (
            <div className="result-card gap-card">
              <h5>Missing Skills</h5>
              <div className="skills-list">
                {missing_skills.map((s, i) => (
                  <span key={i} className="skill-chip">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
