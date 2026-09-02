import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = '/api/v1';

const SAMPLE_SPECS = [
  {
    category: 'Civil',
    label: 'Fe 500D TMT Rebars',
    expected: 'IS 1786',
    text: 'Supply of Fe 500D grade TMT thermo-mechanically treated deformed steel bars 12mm and 16mm diameter with minimum 500 N/mm2 proof stress, 565 N/mm2 tensile strength, and 16% elongation for RCC bridge construction.'
  },
  {
    category: 'Electrical',
    label: '500 kVA Transformer',
    expected: 'IS 1180 Pt 1',
    text: 'Procurement of 500 kVA, 11 kV / 433 V, 3-phase, 50 Hz, outdoor type oil immersed copper wound distribution transformer conforming to BEE Star 2 energy efficiency loss levels.'
  },
  {
    category: 'Fire Safety',
    label: '6kg ABC Fire Extinguisher',
    expected: 'IS 15683',
    text: 'Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher containing monoammonium phosphate 50% min, with pressure gauge, squeeze grip valve, and fire rating 3A 89B.'
  },
  {
    category: 'Medical / PPE',
    label: '3-Ply Surgical Masks',
    expected: 'IS 16289',
    text: 'Disposable 3-ply surgical face masks with meltblown filter layer, bacterial filtration efficiency (BFE) > 98%, differential pressure < 29.4 Pa/cm2, and fluid splash resistance at 120 mmHg.'
  },
  {
    category: 'Water / Pipes',
    label: '110mm uPVC Potable Pipes',
    expected: 'IS 4985',
    text: 'Supply of unplasticized PVC (uPVC) pipes Class 3 (0.6 MPa) 110mm diameter for potable drinking water supply distribution with lead-free formulation and hydrostatic pressure testing.'
  },
  {
    category: 'Food / Rations',
    label: 'Chakki Atta (Whole Wheat)',
    expected: 'IS 1155',
    text: 'Supply of whole wheat flour (Chakki Atta) in 50 kg bags for government hostel mess: moisture content max 14%, total ash max 2.0%, gluten min 6.0%, free from insect infestation.'
  },
  {
    category: 'Service Contract',
    label: 'Security Guard Hiring',
    expected: 'OUT OF SCOPE',
    isOutOfScope: true,
    text: 'Hiring of 10 security guards and 2 supervisors for round-the-clock 8-hour shift security service at government office complex.'
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('recommender'); // 'recommender' | 'catalog' | 'analytics'
  const [systemHealth, setSystemHealth] = useState(null);
  
  // Recommender State
  const [specText, setSpecText] = useState(SAMPLE_SPECS[0].text);
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [expandedClauses, setExpandedClauses] = useState({});
  const [feedbackState, setFeedbackState] = useState({}); // { [standardId]: { action: 'ACCEPT'|'REJECT'|'CORRECT', logId: 1 } }
  
  // Override Modal State
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [overrideTarget, setOverrideTarget] = useState(null);
  const [correctStandardId, setCorrectStandardId] = useState('');
  const [officerNotes, setOfficerNotes] = useState('');

  // Catalog State
  const [catalogList, setCatalogList] = useState([]);
  const [catalogTotal, setCatalogTotal] = useState(0);
  const [catalogSearch, setCatalogSearch] = useState('');
  const [catalogSector, setCatalogSector] = useState('');
  const [catalogPage, setCatalogPage] = useState(1);
  const [selectedStandard, setSelectedStandard] = useState(null);

  // Analytics State
  const [analyticsData, setAnalyticsData] = useState(null);

  // Poll health on mount
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Fetch catalog when tab changes or search/filter changes
  useEffect(() => {
    if (activeTab === 'catalog') {
      fetchCatalog();
    } else if (activeTab === 'analytics') {
      fetchAnalytics();
    }
  }, [activeTab, catalogSearch, catalogSector, catalogPage]);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setSystemHealth(data);
      } else {
        setSystemHealth(null);
      }
    } catch {
      setSystemHealth(null);
    }
  };

  const handleRecommend = async () => {
    if (!specText.trim()) return;
    setLoading(true);
    setErrorMsg(null);
    setResult(null);
    setFeedbackState({});

    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec_text: specText, top_k: parseInt(topK, 10) })
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to reach recommendation engine. Ensure API is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (standardId, action, correctedId = null, notes = '') => {
    try {
      const payload = {
        spec_text: specText,
        recommended_standard_id: standardId,
        action: action,
        corrected_standard_id: correctedId,
        officer_notes: notes || `Recorded by officer via GeM portal`
      };

      const res = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setFeedbackState(prev => ({
          ...prev,
          [standardId]: { action, logId: data.log_id, correctedId }
        }));
      }
    } catch (err) {
      console.error('Feedback error:', err);
    }
  };

  const openOverrideModal = (standard) => {
    setOverrideTarget(standard);
    setCorrectStandardId('');
    setOfficerNotes('');
    setOverrideModalOpen(true);
  };

  const submitOverride = () => {
    if (!correctStandardId.trim() || !overrideTarget) return;
    handleFeedback(overrideTarget.standard_id, 'CORRECT', correctStandardId.trim(), officerNotes);
    setOverrideModalOpen(false);
  };

  const toggleClauses = (id) => {
    setExpandedClauses(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const fetchCatalog = async () => {
    try {
      const params = new URLSearchParams({
        page: catalogPage.toString(),
        page_size: '15'
      });
      if (catalogSearch) params.append('search', catalogSearch);
      if (catalogSector) params.append('sector', catalogSector);

      const res = await fetch(`${API_BASE}/standards?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setCatalogList(data.standards || []);
        setCatalogTotal(data.total_count || 0);
      }
    } catch (err) {
      console.error('Catalog fetch error:', err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/coverage-gaps`);
      if (res.ok) {
        const data = await res.json();
        setAnalyticsData(data);
      }
    } catch (err) {
      console.error('Analytics fetch error:', err);
    }
  };

  const getConfidenceLevelClass = (level) => {
    switch (level) {
      case 'HIGH': return 'high';
      case 'MEDIUM': return 'medium';
      case 'LOW': return 'low';
      default: return 'uncertain';
    }
  };

  return (
    <div className="app-wrapper">
      {/* Top Navigation Bar */}
      <header className="portal-header">
        <div className="header-inner">
          <div className="brand-section">
            <div className="brand-emblem">
              <div className="brand-emblem-inner">IS</div>
            </div>
            <div className="brand-text">
              <h1>
                IS-Recommender <span className="highlight">BIS & GeM Portal</span>
              </h1>
              <p>AI Recommendation System for Indian Standards in Public Procurement</p>
            </div>
          </div>

          <div className="header-status">
            <span className="sih-badge">SIH 26108</span>
            <div className={`status-indicator ${systemHealth ? '' : 'offline'}`}>
              <span className="status-dot"></span>
              <span>
                {systemHealth
                  ? `API Connected • ${systemHealth.standards_count} Standards Loaded`
                  : 'Connecting to Backend...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-container">
        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`tab-btn ${activeTab === 'recommender' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommender')}
          >
            🎯 Tender Recommender
          </button>
          <button
            className={`tab-btn ${activeTab === 'catalog' ? 'active' : ''}`}
            onClick={() => setActiveTab('catalog')}
          >
            📚 BIS Standards Catalog (500+)
          </button>
          <button
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            📊 Audit & Coverage Analytics
          </button>
        </nav>

        {/* Tab 1: Tender Recommender */}
        {activeTab === 'recommender' && (
          <section>
            {/* Input Card */}
            <div className="input-card">
              <div className="input-card-header">
                <div className="input-title">
                  <h2>
                    <span>📋</span> Analyze Tender Specification
                  </h2>
                  <p>Paste raw, free-text procurement clauses or select a realistic GeM sample tender below.</p>
                </div>
              </div>

              {/* Sample Presets */}
              <div className="preset-bar">
                <div className="preset-label">Quick Test Presets (Real GeM Tenders):</div>
                <div className="preset-chips">
                  {SAMPLE_SPECS.map((sample, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className={`preset-chip ${sample.isOutOfScope ? 'out-of-scope' : ''}`}
                      onClick={() => {
                        setSpecText(sample.text);
                        setResult(null);
                        setFeedbackState({});
                      }}
                    >
                      <span>{sample.category}:</span>
                      <strong>{sample.label}</strong>
                      <span style={{ opacity: 0.7 }}>({sample.expected})</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Textarea */}
              <div className="textarea-container">
                <textarea
                  className="tender-textarea"
                  value={specText}
                  onChange={(e) => setSpecText(e.target.value)}
                  placeholder="e.g. Supply of Fe 500D grade TMT steel bars 12mm dia with minimum proof stress 500 N/mm2..."
                  rows={4}
                />
                <div className="textarea-footer">
                  <span>{specText.length} characters</span>
                  <span>Supports multiline tender schedule text</span>
                </div>
              </div>

              {/* Actions & Parameters */}
              <div className="input-actions">
                <div className="controls-left">
                  <div className="k-select-wrapper">
                    <span>Rank Top-K:</span>
                    <select
                      className="k-select"
                      value={topK}
                      onChange={(e) => setTopK(e.target.value)}
                    >
                      <option value="3">Top 3 Standards</option>
                      <option value="5">Top 5 Standards</option>
                      <option value="10">Top 10 Standards</option>
                    </select>
                  </div>
                  {specText && (
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => {
                        setSpecText('');
                        setResult(null);
                      }}
                    >
                      Clear Input
                    </button>
                  )}
                </div>

                <button
                  type="button"
                  className="submit-btn"
                  onClick={handleRecommend}
                  disabled={loading || !specText.trim()}
                >
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      <span>Analyzing & Reranking...</span>
                    </>
                  ) : (
                    <>
                      <span>⚡ Recommend Applicable Standards</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="alert-box out-of-scope">
                <div className="alert-icon">⚠️</div>
                <div className="alert-content">
                  <h4>Recommendation Failed</h4>
                  <p>{errorMsg}</p>
                </div>
              </div>
            )}

            {/* Out of Scope Alert */}
            {result && result.status === 'OUT_OF_SCOPE' && (
              <div className="alert-box out-of-scope">
                <div className="alert-icon">🛑</div>
                <div className="alert-content">
                  <h4>Out-of-Scope Service Contract Detected</h4>
                  <p>{result.message}</p>
                  <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', opacity: 0.85 }}>
                    Processing latency: {result.execution_time_ms} ms
                  </div>
                </div>
              </div>
            )}

            {/* Results Grid */}
            {result && result.recommendations && result.recommendations.length > 0 && (
              <div className="results-container">
                <div className="results-header">
                  <h3>
                    <span>🎯</span> Ranked BIS Recommendations ({result.recommendations.length} Found)
                  </h3>
                  <div className="results-meta">
                    <span className="latency-badge">{result.execution_time_ms} ms Latency</span>
                    <span style={{ color: '#10b981' }}>✓ Cross-Encoder Calibrated</span>
                  </div>
                </div>

                <div className="recs-grid">
                  {result.recommendations.map((rec) => {
                    const fb = feedbackState[rec.standard_id];
                    const isExpanded = expandedClauses[rec.standard_id];

                    return (
                      <div key={rec.standard_id} className="rec-card">
                        {/* Top Meta Row */}
                        <div className="rec-card-top">
                          <div className="rec-left-meta">
                            <span className="rank-badge">#{rec.rank}</span>
                            <span className="standard-code">{rec.standard_id}</span>
                            <span className="sector-tag">{rec.sector}</span>
                            {rec.ics_code && <span className="ics-tag">ICS {rec.ics_code}</span>}
                          </div>

                          <div className={`confidence-pill ${getConfidenceLevelClass(rec.confidence_level)}`}>
                            <span>●</span>
                            <span>{rec.confidence_pct}% MATCH ({rec.confidence_level})</span>
                          </div>
                        </div>

                        {/* Standard Title */}
                        <div className="standard-title">{rec.title}</div>

                        {/* Mandatory QCO Regulatory Banner */}
                        {rec.qco_compliance?.is_mandatory && (
                          <div className="qco-banner">
                            <span>⚖️</span>
                            <span>MANDATORY QUALITY CONTROL ORDER: ISI Certification Mark is legally required for public procurement on GeM.</span>
                          </div>
                        )}

                        {/* Plain-English Justification */}
                        <div className="justification-box">
                          <strong>Justification:</strong> {rec.justification}
                        </div>

                        {/* Matched Technical Keywords */}
                        {rec.matched_keywords && rec.matched_keywords.length > 0 && (
                          <div className="keywords-row">
                            <span className="keywords-label">Matched Parameters:</span>
                            {rec.matched_keywords.map((kw, idx) => (
                              <span key={idx} className="kw-badge">
                                #{kw}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Matched Clauses Toggle & Drawer */}
                        {rec.matched_clauses && rec.matched_clauses.length > 0 && (
                          <>
                            <button
                              type="button"
                              className="clauses-toggle"
                              onClick={() => toggleClauses(rec.standard_id)}
                            >
                              <span>{isExpanded ? '▲ Hide' : '▼ View'} {rec.matched_clauses.length} Matched Technical Clause(s)</span>
                            </button>

                            {isExpanded && (
                              <div className="clauses-drawer">
                                {rec.matched_clauses.map((c, cIdx) => (
                                  <div key={cIdx} className="clause-item">
                                    <div className="clause-head">
                                      {c.clause_no}: {c.title}
                                    </div>
                                    <div className="clause-text">{c.text}</div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </>
                        )}

                        {/* Algorithmic Scoring Diagnostics */}
                        <div className="scores-row">
                          <div className="score-chip">
                            <span>Dense FAISS:</span> {rec.dense_score ? rec.dense_score.toFixed(3) : 'N/A'}
                          </div>
                          <div className="score-chip">
                            <span>Sparse BM25:</span> {rec.sparse_score ? rec.sparse_score.toFixed(3) : 'N/A'}
                          </div>
                          <div className="score-chip">
                            <span>Cross-Encoder:</span> {rec.cross_encoder_score ? rec.cross_encoder_score.toFixed(3) : 'N/A'}
                          </div>
                          {rec.officer_boost_applied !== 0 && (
                            <div className="score-chip" style={{ color: '#34d399', borderColor: '#10b981' }}>
                              <span>Officer Boost:</span> +{rec.officer_boost_applied}
                            </div>
                          )}
                        </div>

                        {/* Officer Decision & Feedback Loop */}
                        <div className="officer-actions">
                          <div className="actions-prompt">
                            <span>🛡️ Procurement Officer Action:</span>
                          </div>

                          {fb ? (
                            <div className="feedback-badge">
                              ✓ {fb.action === 'ACCEPT' && 'Approved & Accepted by Officer'}
                              {fb.action === 'REJECT' && 'Marked Non-Applicable by Officer'}
                              {fb.action === 'CORRECT' && `Overridden to ${fb.correctedId}`}
                              <span style={{ fontSize: '0.7rem', opacity: 0.8 }}>(Saved to SQLite audit log #{fb.logId})</span>
                            </div>
                          ) : (
                            <div className="action-buttons">
                              <button
                                type="button"
                                className="btn-decision accept"
                                onClick={() => handleFeedback(rec.standard_id, 'ACCEPT')}
                              >
                                ✓ Accept Standard
                              </button>
                              <button
                                type="button"
                                className="btn-decision reject"
                                onClick={() => handleFeedback(rec.standard_id, 'REJECT')}
                              >
                                ✗ Reject Standard
                              </button>
                              <button
                                type="button"
                                className="btn-decision override"
                                onClick={() => openOverrideModal(rec)}
                              >
                                ✎ Override / Correct
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </section>
        )}

        {/* Tab 2: Standards Catalog Explorer */}
        {activeTab === 'catalog' && (
          <section>
            <div className="input-card">
              <div className="input-card-header">
                <div className="input-title">
                  <h2>
                    <span>📚</span> Indian Standards Catalog Explorer
                  </h2>
                  <p>Browse, search, and inspect 500+ Indian Standards (BIS) curated for GeM procurement sectors.</p>
                </div>
              </div>

              {/* Filters */}
              <div className="catalog-controls">
                <input
                  type="text"
                  className="catalog-search-input"
                  value={catalogSearch}
                  onChange={(e) => {
                    setCatalogSearch(e.target.value);
                    setCatalogPage(1);
                  }}
                  placeholder="Search by IS code (e.g. IS 1786) or keywords (transformer, cement, steel)..."
                />

                <select
                  className="catalog-sector-select"
                  value={catalogSector}
                  onChange={(e) => {
                    setCatalogSector(e.target.value);
                    setCatalogPage(1);
                  }}
                >
                  <option value="">All Sectors</option>
                  <option value="Civil Engineering">Civil Engineering</option>
                  <option value="Electrotechnical">Electrotechnical</option>
                  <option value="Mechanical">Mechanical Engineering</option>
                  <option value="Chemical">Chemical</option>
                  <option value="Medical Equipment">Medical Equipment & Hospital</option>
                  <option value="Food & Agriculture">Food & Agriculture</option>
                  <option value="Textiles">Textiles</option>
                  <option value="Electronics & IT">Electronics & IT</option>
                  <option value="Petroleum">Petroleum, Coal & Related Products</option>
                </select>
              </div>

              {/* Results Summary */}
              <div style={{ marginBottom: '1rem', fontSize: '0.85rem', color: '#94a3b8' }}>
                Showing {catalogList.length} of {catalogTotal} Indian Standards
              </div>

              {/* Table */}
              <div className="catalog-table-wrapper">
                <table className="catalog-table">
                  <thead>
                    <tr>
                      <th>Standard Code</th>
                      <th>Year</th>
                      <th>Title & Scope</th>
                      <th>Sector</th>
                      <th>QCO Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalogList.map((std) => (
                      <tr key={std.standard_id}>
                        <td>
                          <strong style={{ color: '#60a5fa' }}>{std.code}</strong>
                        </td>
                        <td>{std.year}</td>
                        <td style={{ maxWidth: '420px' }}>
                          <div style={{ fontWeight: 600, color: '#f1f5f9', marginBottom: '0.2rem' }}>
                            {std.title}
                          </div>
                          <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                            {std.scope?.slice(0, 110)}...
                          </div>
                        </td>
                        <td>
                          <span className="sector-tag">{std.sector}</span>
                        </td>
                        <td>
                          {std.is_mandatory_qco ? (
                            <span style={{ color: '#ef4444', fontWeight: 700, fontSize: '0.75rem' }}>
                              ⚖️ Mandatory QCO
                            </span>
                          ) : (
                            <span style={{ color: '#64748b', fontSize: '0.75rem' }}>
                              Voluntary
                            </span>
                          )}
                        </td>
                        <td>
                          <button
                            type="button"
                            className="btn-decision override"
                            style={{ padding: '0.3rem 0.6rem' }}
                            onClick={() => setSelectedStandard(std)}
                          >
                            Inspect Clauses
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}

        {/* Tab 3: Admin Coverage Analytics */}
        {activeTab === 'analytics' && (
          <section>
            <div className="input-card">
              <div className="input-card-header">
                <div className="input-title">
                  <h2>
                    <span>📊</span> Coverage Gaps & Procurement Feedback Analytics
                  </h2>
                  <p>Real-time audit log of officer decisions and gap analysis for standards coverage.</p>
                </div>
              </div>

              {/* KPI Cards */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-title">Catalog Standards</div>
                  <div className="kpi-value">{systemHealth?.standards_count || 500}+</div>
                  <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '0.3rem' }}>
                    100% Vector Indexed
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Total Officer Decisions</div>
                  <div className="kpi-value">{analyticsData?.total_feedback || 0}</div>
                  <div style={{ fontSize: '0.75rem', color: '#60a5fa', marginTop: '0.3rem' }}>
                    Stored in SQLite DB
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Officer Approvals</div>
                  <div className="kpi-value" style={{ color: '#34d399' }}>
                    {analyticsData?.accepted_count || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.3rem' }}>
                    Acceptance Rate: {analyticsData?.acceptance_rate_pct || 100}%
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Rejections / Overrides</div>
                  <div className="kpi-value" style={{ color: '#fb7185' }}>
                    {(analyticsData?.rejected_count || 0) + (analyticsData?.corrected_count || 0)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#f59e0b', marginTop: '0.3rem' }}>
                    Calibrates dynamic boost
                  </div>
                </div>
              </div>

              {/* Audit Log Table */}
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#ffffff' }}>
                Recent Procurement Officer Audit Entries
              </h3>

              <div className="catalog-table-wrapper">
                <table className="catalog-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Decision</th>
                      <th>Recommended Standard</th>
                      <th>Officer Notes</th>
                      <th>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData?.recent_feedback && analyticsData.recent_feedback.length > 0 ? (
                      analyticsData.recent_feedback.map((item) => (
                        <tr key={item.id}>
                          <td>#{item.id}</td>
                          <td>
                            <span
                              className={`confidence-pill ${
                                item.action === 'ACCEPT'
                                  ? 'high'
                                  : item.action === 'REJECT'
                                  ? 'uncertain'
                                  : 'medium'
                              }`}
                              style={{ display: 'inline-flex' }}
                            >
                              {item.action}
                            </span>
                          </td>
                          <td>
                            <strong style={{ color: '#93c5fd' }}>
                              {item.recommended_standard_id}
                            </strong>
                            {item.corrected_standard_id && (
                              <div style={{ fontSize: '0.75rem', color: '#f59e0b' }}>
                                Corrected to: {item.corrected_standard_id}
                              </div>
                            )}
                          </td>
                          <td style={{ color: '#94a3b8' }}>{item.officer_notes || '—'}</td>
                          <td style={{ fontSize: '0.75rem', color: '#64748b' }}>
                            {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Recent'}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                          No officer feedback entries logged yet. Test recommendations and click Accept/Reject!
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Override Standard Modal */}
      {overrideModalOpen && (
        <div className="modal-overlay" onClick={() => setOverrideModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Override Standard for Specification</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setOverrideModalOpen(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                You are overriding <strong>{overrideTarget?.standard_id}</strong>. Enter the correct Indian Standard code to record in the calibration database.
              </p>

              <div>
                <label>Correct Indian Standard ID / Code:</label>
                <input
                  type="text"
                  className="modal-input"
                  placeholder="e.g. IS 2062:2011 or IS 432"
                  value={correctStandardId}
                  onChange={(e) => setCorrectStandardId(e.target.value)}
                />
              </div>

              <div>
                <label>Officer Audit Justification (Optional):</label>
                <input
                  type="text"
                  className="modal-input"
                  placeholder="e.g. Structural grade E250 requires IS 2062 instead"
                  value={officerNotes}
                  onChange={(e) => setOfficerNotes(e.target.value)}
                />
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setOverrideModalOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-decision accept"
                onClick={submitOverride}
                disabled={!correctStandardId.trim()}
              >
                Submit Correction
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Standard Detail Modal */}
      {selectedStandard && (
        <div className="modal-overlay" onClick={() => setSelectedStandard(null)}>
          <div className="modal-content" style={{ maxWidth: '680px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <span className="sector-tag" style={{ marginRight: '0.5rem' }}>{selectedStandard.sector}</span>
                <strong style={{ fontSize: '1.2rem', color: '#60a5fa' }}>{selectedStandard.standard_id}</strong>
              </div>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setSelectedStandard(null)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
              <h4 style={{ color: '#ffffff', fontSize: '1.1rem' }}>{selectedStandard.title}</h4>
              <p style={{ fontSize: '0.88rem', color: '#cbd5e1' }}>{selectedStandard.scope}</p>

              {selectedStandard.is_mandatory_qco && (
                <div className="qco-banner">
                  <span>⚖️</span>
                  <span>Mandatory QCO Regulatory Order in effect for GeM procurement.</span>
                </div>
              )}

              <h5 style={{ color: '#93c5fd', marginTop: '1rem', marginBottom: '0.5rem' }}>
                Technical Clauses ({selectedStandard.clauses?.length || 0})
              </h5>
              <div className="clauses-drawer" style={{ background: '#0a1020' }}>
                {selectedStandard.clauses?.map((cl, idx) => (
                  <div key={idx} className="clause-item">
                    <div className="clause-head">{cl.clause_no}: {cl.title}</div>
                    <div className="clause-text">{cl.text}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setSelectedStandard(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="portal-footer">
        <p>
          Bureau of Indian Standards (BIS) & Government e-Marketplace (GeM) • Problem Statement <span className="highlight">SIH26108</span> • Built with Hybrid RRF & Cross-Encoder AI
        </p>
      </footer>
    </div>
  );
}
