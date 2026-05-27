import React from "react";

export default function Summaries({ summaries }) {
  if (!summaries) return null;

  const { per_client_summaries, overall_summary } = summaries;

  return (
    <div className="summaries-section">
      <h3>Summaries</h3>

      <div className="overall-summary">
        <h4>Overall Professional Summary</h4>
        <p>{overall_summary}</p>
      </div>

      <div className="client-summaries">
        <h4>Per-Client Summaries</h4>
        <div className="summary-cards">
          {per_client_summaries.map((cs, i) => (
            <div key={i} className="summary-card">
              <h5>{cs.client}</h5>
              <p>{cs.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
