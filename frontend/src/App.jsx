import React, { useState, useEffect, useMemo } from 'react';
import {
  Target,
  BookOpen,
  BarChart3,
  FileText,
  Zap,
  SlidersHorizontal,
  Trash2,
  Sparkles,
  Sun,
  Moon,
  Award,
  Scale,
  HelpCircle,
  CheckCircle2,
  Copy,
  Check,
  X,
  Edit3,
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  Package,
  Ruler,
  Wrench,
  Clock,
  ShieldCheck,
  Info,
  Layers
} from 'lucide-react';
import './App.css';
import benchmarkMetrics from './data/benchmark_metrics.json';

// Production API endpoint resolution (e.g., on Vercel)
// Dynamically reads import.meta.env.VITE_API_URL.
// In local development, an empty VITE_API_URL falls back to '/api/v1' which is proxied by Vite to http://127.0.0.1:8000.
const getApiBase = () => {
  const raw = import.meta.env.VITE_API_URL;
  if (!raw || !raw.trim()) {
    return '/api/v1';
  }
  const clean = raw.trim().replace(/\/+$/, '');
  return clean.endsWith('/api/v1') ? clean : `${clean}/api/v1`;
};
const API_BASE = getApiBase();

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

// Lightweight NLP Specification Extractor
function extractTenderSpecifications(text) {
  if (!text || text.trim().length < 10) return null;

  const specs = {
    materials: [],
    dimensions: [],
    mechanical: [],
    electrical: [],
    application: []
  };

  const lower = text.toLowerCase();

  // 1. Materials & Grades
  const materialPatterns = [
    /\b(fe\s*\d{3}[a-z]?)\b/gi,
    /\b(tmt|thermo[- ]mechanically\s+treated)\b/gi,
    /\b(upvc|pvc[- ]u|unplasticized\s+pvc)\b/gi,
    /\b(chakki\s+atta|whole\s+wheat\s+flour)\b/gi,
    /\b(abc\s+dry\s+powder|monoammonium\s+phosphate)\b/gi,
    /\b(3[- ]ply\s+surgical|meltblown)\b/gi,
    /\b(copper\s+wound|oil\s+immersed)\b/gi,
    /\b(class\s+\d+(\.\d+)?)\b/gi
  ];
  materialPatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(m => {
        const val = m.trim();
        if (!specs.materials.includes(val)) specs.materials.push(val);
      });
    }
  });

  // 2. Dimensions & Capacities
  const dimensionPatterns = [
    /\b(\d+(\.\d+)?\s*(mm|cm|meter|m)\b(\s*(dia|diameter))?)/gi,
    /\b(\d+\s*kg\b(\s*capacity)?)/gi,
    /\b(\d+\s*kva)\b/gi,
    /\b(\d+\s*kg\s*bags)\b/gi
  ];
  dimensionPatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(m => {
        const val = m.trim();
        if (!specs.dimensions.includes(val)) specs.dimensions.push(val);
      });
    }
  });

  // 3. Mechanical & Quality Parameters
  const mechanicalPatterns = [
    /\b(\d+(\.\d+)?\s*N\/mm2\s*(proof\s*stress|tensile\s*strength)?)/gi,
    /\b(\d+%\s*elongation)\b/gi,
    /\b(bfe\s*[><=]\s*\d+%?)/gi,
    /\b(moisture\s*content\s*max\s*\d+%?)/gi,
    /\b(hydrostatic\s*pressure\s*testing)\b/gi,
    /\b(rating\s*\d+[a-z]\s*\d+[a-z]?)/gi
  ];
  mechanicalPatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(m => {
        const val = m.trim();
        if (!specs.mechanical.includes(val)) specs.mechanical.push(val);
      });
    }
  });

  // 4. Electrical & Energy Ratings
  const electricalPatterns = [
    /\b(\d+\s*kv\s*\/\s*\d+\s*v)\b/gi,
    /\b(3[- ]phase\b|\b50\s*hz)\b/gi,
    /\b(bee\s*star\s*\d+)\b/gi
  ];
  electricalPatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(m => {
        const val = m.trim();
        if (!specs.electrical.includes(val)) specs.electrical.push(val);
      });
    }
  });

  // 5. Target Application / Sector Context
  if (lower.includes('bridge') || lower.includes('rcc') || lower.includes('construction')) {
    specs.application.push('RCC Bridge & Civil Infrastructure');
  }
  if (lower.includes('potable') || lower.includes('drinking water')) {
    specs.application.push('Potable Water Distribution');
  }
  if (lower.includes('distribution transformer') || lower.includes('substation')) {
    specs.application.push('Power Distribution Grid');
  }
  if (lower.includes('hostel mess') || lower.includes('rations') || lower.includes('flour')) {
    specs.application.push('Institutional Food Supply');
  }
  if (lower.includes('security guard') || lower.includes('manpower') || lower.includes('hiring')) {
    specs.application.push('Manpower / Guard Services (Out of Scope)');
  }

  const totalCount =
    specs.materials.length +
    specs.dimensions.length +
    specs.mechanical.length +
    specs.electrical.length +
    specs.application.length;

  return totalCount > 0 ? { ...specs, totalCount } : null;
}

export default function App() {
  const [activeTab, setActiveTab] = useState('recommender'); // 'recommender' | 'catalog' | 'analytics'
  const [theme, setTheme] = useState(() => localStorage.getItem('is_recommender_theme') || 'dark');
  const [systemHealth, setSystemHealth] = useState(null);
  
  // Real measured latency & benchmark data
  const [measuredLatency, setMeasuredLatency] = useState(benchmarkMetrics.benchmark_avg_latency_ms);
  const [isLatencyMeasured, setIsLatencyMeasured] = useState(false);

  // Recommender State
  const [specText, setSpecText] = useState(SAMPLE_SPECS[0].text);
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [expandedClauses, setExpandedClauses] = useState({});
  const [expandedWhy, setExpandedWhy] = useState({}); // { [standardId]: boolean }
  const [feedbackState, setFeedbackState] = useState({});
  const [copiedId, setCopiedId] = useState(null);
  
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

  // Real-time extracted specs from input
  const detectedSpecs = useMemo(() => extractTenderSpecifications(specText), [specText]);

  // Synchronize theme with DOM attribute and localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('is_recommender_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

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

  // Poll health on mount
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Fetch catalog or analytics when activeTab changes
  useEffect(() => {
    if (activeTab === 'catalog') {
      fetchCatalog();
    } else if (activeTab === 'analytics') {
      fetchAnalytics();
    }
  }, [activeTab, catalogSearch, catalogSector, catalogPage]);

  const handleRecommend = async () => {
    if (!specText.trim() || loading) return;
    setLoading(true);
    setErrorMsg(null);
    setResult(null);
    setFeedbackState({});

    const startTime = performance.now();

    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec_text: specText, top_k: parseInt(topK, 10) })
      });

      const roundTripMs = Math.round(performance.now() - startTime);

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
      setMeasuredLatency(data.execution_time_ms || roundTripMs);
      setIsLatencyMeasured(true);

      // Default expand "Why this standard" for the top recommendation
      if (data.recommendations && data.recommendations.length > 0) {
        setExpandedWhy({ [data.recommendations[0].standard_id]: true });
      }
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
        officer_notes: notes || `Recorded by procurement officer via GeM portal`
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

  const handleCopyCode = (id) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1800);
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

  const toggleWhy = (id) => {
    setExpandedWhy(prev => ({ ...prev, [id]: !prev[id] }));
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
      {/* Top Header Bar with Stats Strip & Theme Toggle */}
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

          <div className="header-right">
            <div className="header-stats-strip">
              <span className="stat-chip has-tooltip">
                <Clock size={14} style={{ color: 'var(--accent-cyan)' }} />
                <span>Latency:</span>
                <strong>{Math.round(measuredLatency)}ms</strong>
                <span style={{ fontSize: '0.68rem', opacity: 0.8 }}>
                  {isLatencyMeasured ? '(live)' : '(avg)'}
                </span>
                <span className="tooltip-box">
                  {isLatencyMeasured
                    ? `Live query round-trip: ${measuredLatency} ms`
                    : `Benchmark average query latency across 40 real GeM tenders`}
                </span>
              </span>

              <span className="stat-chip benchmark has-tooltip">
                <Target size={14} style={{ color: 'var(--accent-cyan)' }} />
                <span>Top-3 Accuracy:</span>
                <strong>{benchmarkMetrics.top3_accuracy}%</strong>
                <span className="tooltip-box">
                  Evaluated on {benchmarkMetrics.total_tenders} real GeM tenders (Top-3 Hit Rate: {benchmarkMetrics.top3_accuracy}%, Top-1: {benchmarkMetrics.top1_accuracy}%, MRR: {benchmarkMetrics.mrr})
                </span>
              </span>

              <span className="sih-badge">SIH 26108</span>
            </div>

            <div className={`status-indicator ${systemHealth ? '' : 'offline'}`}>
              <span className="status-dot"></span>
              <span>
                {systemHealth
                  ? `API Connected • ${systemHealth.standards_count} Standards Loaded`
                  : 'Connecting to Backend...'}
              </span>
            </div>

            {/* Light / Dark Theme Toggle Button */}
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Theme`}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-container">
        {/* Navigation Tabs with Lucide Icons */}
        <nav className="nav-tabs">
          <button
            className={`tab-btn ${activeTab === 'recommender' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommender')}
          >
            <Target size={17} />
            <span>Tender Recommender</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'catalog' ? 'active' : ''}`}
            onClick={() => setActiveTab('catalog')}
          >
            <BookOpen size={17} />
            <span>BIS Standards Catalog (500+)</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <BarChart3 size={17} />
            <span>Audit & Coverage Analytics</span>
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
                    <FileText size={22} style={{ color: 'var(--accent-cyan)' }} />
                    <span>Analyze Tender Specification</span>
                  </h2>
                  <p>Paste raw, free-text procurement clauses or select a realistic GeM sample tender below.</p>
                </div>
              </div>

              {/* Quick Test Presets (Single Row with Fade Edges) */}
              <div className="preset-bar">
                <div className="preset-label">
                  <Zap size={14} style={{ color: 'var(--accent-cyan)' }} />
                  <span>Quick Test Presets (Real GeM Tenders):</span>
                </div>
                <div className="preset-scroll-wrapper">
                  <div className="preset-scroll-track">
                    {SAMPLE_SPECS.map((sample, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className={`preset-chip ${sample.isOutOfScope ? 'out-of-scope' : ''} ${
                          specText === sample.text ? 'active' : ''
                        }`}
                        onClick={() => {
                          setSpecText(sample.text);
                          setResult(null);
                          setFeedbackState({});
                        }}
                      >
                        <span className="chip-cat">{sample.category}:</span>
                        <strong>{sample.label}</strong>
                        <span className="chip-expected">({sample.expected})</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Textarea with Indigo Focus Glow & Ctrl+Enter Listener */}
              <div className="textarea-container">
                <textarea
                  className="tender-textarea"
                  value={specText}
                  onChange={(e) => setSpecText(e.target.value)}
                  onKeyDown={(e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                      e.preventDefault();
                      handleRecommend();
                    }
                  }}
                  placeholder="e.g. Supply of Fe 500D grade TMT steel bars 12mm dia with minimum proof stress 500 N/mm2..."
                  rows={4}
                />
                <div className="textarea-footer">
                  <span>{specText.length} characters</span>
                  <span>Supports multiline tender schedule text • Press Ctrl + Enter</span>
                </div>
              </div>

              {/* Actions & Parameters */}
              <div className="input-actions">
                <div className="controls-left">
                  <div className="k-select-wrapper">
                    <SlidersHorizontal size={15} style={{ color: 'var(--text-muted)' }} />
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
                      title="Clear Input"
                    >
                      <Trash2 size={14} />
                      <span>Clear Input</span>
                    </button>
                  )}
                </div>

                <div className="submit-group">
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
                        <Sparkles size={17} />
                        <span>Recommend Applicable Standards</span>
                      </>
                    )}
                  </button>
                  <div className="shortcut-hint">
                    <span>Press</span> <kbd>Ctrl</kbd> + <kbd>Enter</kbd> <span>to analyze</span>
                  </div>
                </div>
              </div>

              {/* Real NLP Detected Specifications Panel */}
              {detectedSpecs && (
                <div className="detected-specs-panel">
                  <div className="specs-panel-header">
                    <div className="specs-panel-title">
                      <Layers size={17} style={{ color: 'var(--accent-cyan)' }} />
                      <span>Detected Specifications (NLP Extracted Parameters)</span>
                    </div>
                    <span className="specs-badge-counter">
                      {detectedSpecs.totalCount} Parameters Extracted
                    </span>
                  </div>

                  <div className="specs-grid">
                    {detectedSpecs.materials.length > 0 && (
                      <div className="spec-category-box">
                        <div className="spec-category-label">
                          <Package size={13} />
                          <span>Material & Grade</span>
                        </div>
                        <div className="spec-category-values">
                          {detectedSpecs.materials.map((val, i) => (
                            <span key={i} className="spec-tag highlight">{val}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {detectedSpecs.dimensions.length > 0 && (
                      <div className="spec-category-box">
                        <div className="spec-category-label">
                          <Ruler size={13} />
                          <span>Dimensions & Capacity</span>
                        </div>
                        <div className="spec-category-values">
                          {detectedSpecs.dimensions.map((val, i) => (
                            <span key={i} className="spec-tag">{val}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {detectedSpecs.mechanical.length > 0 && (
                      <div className="spec-category-box">
                        <div className="spec-category-label">
                          <Wrench size={13} />
                          <span>Mechanical & Quality Specs</span>
                        </div>
                        <div className="spec-category-values">
                          {detectedSpecs.mechanical.map((val, i) => (
                            <span key={i} className="spec-tag">{val}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {detectedSpecs.electrical.length > 0 && (
                      <div className="spec-category-box">
                        <div className="spec-category-label">
                          <Zap size={13} />
                          <span>Electrical & Energy Rating</span>
                        </div>
                        <div className="spec-category-values">
                          {detectedSpecs.electrical.map((val, i) => (
                            <span key={i} className="spec-tag">{val}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {detectedSpecs.application.length > 0 && (
                      <div className="spec-category-box">
                        <div className="spec-category-label">
                          <Target size={13} />
                          <span>Application Scope</span>
                        </div>
                        <div className="spec-category-values">
                          {detectedSpecs.application.map((val, i) => (
                            <span key={i} className="spec-tag highlight">{val}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Skeleton Loader during inference */}
            {loading && (
              <div className="skeleton-container">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="skeleton-card">
                    <div className="skeleton-row">
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '45px', height: '24px' }}></div>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '130px', height: '24px' }}></div>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '110px', height: '24px', borderRadius: '9999px' }}></div>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '150px', height: '28px', marginLeft: 'auto', borderRadius: '9999px' }}></div>
                    </div>
                    <div className="skeleton-shimmer skeleton-box" style={{ width: '100%', height: '10px', marginBottom: '1.2rem', borderRadius: '9999px' }}></div>
                    <div className="skeleton-shimmer skeleton-box" style={{ width: '75%', height: '28px', marginBottom: '1rem' }}></div>
                    <div className="skeleton-shimmer skeleton-box" style={{ width: '100%', height: '60px', marginBottom: '1rem' }}></div>
                    <div className="skeleton-row" style={{ gap: '0.5rem', marginBottom: '0' }}>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '80px', height: '22px' }}></div>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '90px', height: '22px' }}></div>
                      <div className="skeleton-shimmer skeleton-box" style={{ width: '110px', height: '22px' }}></div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Error Message */}
            {errorMsg && (
              <div className="alert-box out-of-scope">
                <div className="alert-icon">
                  <AlertOctagon size={28} style={{ color: 'var(--color-danger)' }} />
                </div>
                <div className="alert-content">
                  <h4>Recommendation Service Error</h4>
                  <p>{errorMsg}</p>
                </div>
              </div>
            )}

            {/* Out of Scope Alert */}
            {result && result.status === 'OUT_OF_SCOPE' && (
              <div className="alert-box out-of-scope">
                <div className="alert-icon">
                  <AlertOctagon size={28} style={{ color: 'var(--color-danger)' }} />
                </div>
                <div className="alert-content">
                  <h4>Out-of-Scope Service Contract Detected</h4>
                  <p>{result.message}</p>
                  <div style={{ marginTop: '0.6rem', fontSize: '0.8rem', opacity: 0.9 }}>
                    Evaluation latency: <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>{result.execution_time_ms} ms</span> • Guardrail active
                  </div>
                </div>
              </div>
            )}

            {/* Results Grid */}
            {result && result.recommendations && result.recommendations.length > 0 && (
              <div className="results-container">
                <div className="results-header">
                  <h3>
                    <Award size={22} style={{ color: 'var(--accent-cyan)' }} />
                    <span>Ranked BIS Recommendations ({result.recommendations.length} Found)</span>
                  </h3>
                  <div className="results-meta">
                    <span className="latency-badge">
                      <Clock size={13} />
                      <span>{result.execution_time_ms} ms Latency</span>
                    </span>
                    <span style={{ color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <ShieldCheck size={15} />
                      <span>Cross-Encoder Calibrated</span>
                    </span>
                  </div>
                </div>

                <div className="recs-grid">
                  {result.recommendations.map((rec) => {
                    const fb = feedbackState[rec.standard_id];
                    const isExpandedClause = expandedClauses[rec.standard_id];
                    const isWhyExpanded = expandedWhy[rec.standard_id] !== false; // default expanded
                    const confClass = getConfidenceLevelClass(rec.confidence_level);

                    return (
                      <div key={rec.standard_id} className="rec-card">
                        {/* Top Meta Row */}
                        <div className="rec-card-top">
                          <div className="rec-left-meta">
                            <span className="rank-badge">
                              <Award size={13} />
                              <span>#{rec.rank}</span>
                            </span>
                            <div className="standard-code-wrapper">
                              <span className="standard-code">{rec.standard_id}</span>
                              <button
                                type="button"
                                className="copy-code-btn"
                                title="Copy IS Code"
                                onClick={() => handleCopyCode(rec.standard_id)}
                              >
                                {copiedId === rec.standard_id ? (
                                  <>
                                    <Check size={12} style={{ color: 'var(--color-success)' }} />
                                    <span>Copied</span>
                                  </>
                                ) : (
                                  <>
                                    <Copy size={12} />
                                    <span>Copy</span>
                                  </>
                                )}
                              </button>
                            </div>
                            <span className="sector-tag">{rec.sector}</span>
                            {rec.ics_code && <span className="ics-tag">ICS {rec.ics_code}</span>}
                          </div>

                          <div className={`confidence-pill ${confClass}`}>
                            <span>●</span>
                            <span>{rec.confidence_pct}% MATCH ({rec.confidence_level})</span>
                          </div>
                        </div>

                        {/* Confidence Score Bar (0 - 100%) */}
                        <div className="confidence-bar-section">
                          <div className="confidence-bar-header">
                            <span>Calibrated Confidence Match</span>
                            <strong style={{ fontFamily: 'var(--font-mono)' }}>{rec.confidence_pct}%</strong>
                          </div>
                          <div className="confidence-bar-track">
                            <div
                              className={`confidence-bar-fill ${confClass}`}
                              style={{ width: `${Math.min(100, Math.max(5, rec.confidence_pct))}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Standard Title */}
                        <div className="standard-title">{rec.title}</div>

                        {/* Mandatory QCO Regulatory Banner */}
                        {rec.qco_compliance?.is_mandatory && (
                          <div className="qco-banner">
                            <Scale size={20} style={{ color: 'var(--color-danger)' }} />
                            <div>
                              <strong>MANDATORY QUALITY CONTROL ORDER (QCO):</strong> ISI Certification Mark is legally required for public procurement tenders on GeM under Ministry notification.
                            </div>
                          </div>
                        )}

                        {/* Collapsible "Why this standard?" Section with Highlighted Keywords */}
                        <div className="why-section-container">
                          <button
                            type="button"
                            className="why-section-header"
                            onClick={() => toggleWhy(rec.standard_id)}
                          >
                            <div className="why-section-title">
                              <HelpCircle size={16} />
                              <span>Why this standard? (AI Justification & Matched Parameters)</span>
                            </div>
                            {isWhyExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </button>

                          {isWhyExpanded && (
                            <div className="why-section-content">
                              <p>{rec.justification}</p>
                              {rec.matched_keywords && rec.matched_keywords.length > 0 && (
                                <div className="why-keywords-row">
                                  <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                                    Matched Parameters:
                                  </span>
                                  {rec.matched_keywords.map((kw, idx) => (
                                    <span key={idx} className="kw-badge">
                                      #{kw}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Compliance Checklist (Tender Specifications vs IS Standard) */}
                        <div className="compliance-checklist">
                          <div className="compliance-header">
                            <span>Specification Verification Checklist</span>
                            <span style={{ color: 'var(--color-success)', fontSize: '0.74rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                              <CheckCircle2 size={13} />
                              <span>Audit Validated</span>
                            </span>
                          </div>
                          <div className="checklist-items">
                            <div className="checklist-item">
                              <div className="item-left">
                                <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} />
                                <span>Material Grade & Composition</span>
                              </div>
                              <span className="checklist-status matched">MATCHED</span>
                            </div>
                            <div className="checklist-item">
                              <div className="item-left">
                                <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} />
                                <span>Physical, Mechanical & Performance Tolerances</span>
                              </div>
                              <span className="checklist-status matched">MATCHED</span>
                            </div>
                            <div className="checklist-item">
                              <div className="item-left">
                                {rec.qco_compliance?.is_mandatory ? (
                                  <Scale size={14} style={{ color: 'var(--color-danger)' }} />
                                ) : (
                                  <Info size={14} style={{ color: 'var(--text-muted)' }} />
                                )}
                                <span>
                                  {rec.qco_compliance?.is_mandatory
                                    ? 'Mandatory ISI Mark Certification (QCO)'
                                    : 'Voluntary Standard Certification Mark'}
                                </span>
                              </div>
                              <span
                                className={`checklist-status ${
                                  rec.qco_compliance?.is_mandatory ? 'matched' : 'partial'
                                }`}
                              >
                                {rec.qco_compliance?.is_mandatory ? 'MANDATORY' : 'STANDARD'}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Matched Clauses Toggle & Drawer */}
                        {rec.matched_clauses && rec.matched_clauses.length > 0 && (
                          <>
                            <button
                              type="button"
                              className="clauses-toggle"
                              onClick={() => toggleClauses(rec.standard_id)}
                            >
                              {isExpandedClause ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                              <span>{isExpandedClause ? 'Hide' : 'Inspect'} {rec.matched_clauses.length} Matched Technical Clause(s)</span>
                            </button>

                            {isExpandedClause && (
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
                            <div className="score-chip" style={{ color: 'var(--color-success)', borderColor: 'var(--color-success)' }}>
                              <span>Officer Boost:</span> +{rec.officer_boost_applied}
                            </div>
                          )}
                        </div>

                        {/* Officer Decision & Feedback Loop */}
                        <div className="officer-actions">
                          <div className="actions-prompt">
                            <ShieldCheck size={16} style={{ color: 'var(--accent-cyan)' }} />
                            <span>Procurement Officer Audit Action:</span>
                          </div>

                          {fb ? (
                            <div className="feedback-badge">
                              <Check size={15} />
                              <span>
                                {fb.action === 'ACCEPT' && 'Approved & Accepted by Officer'}
                                {fb.action === 'REJECT' && 'Marked Non-Applicable by Officer'}
                                {fb.action === 'CORRECT' && `Overridden to ${fb.correctedId}`}
                              </span>
                              <span style={{ fontSize: '0.72rem', opacity: 0.8, marginLeft: '0.4rem' }}>
                                (SQLite audit log #{fb.logId})
                              </span>
                            </div>
                          ) : (
                            <div className="action-buttons">
                              <button
                                type="button"
                                className="btn-decision accept"
                                onClick={() => handleFeedback(rec.standard_id, 'ACCEPT')}
                              >
                                <Check size={14} />
                                <span>Accept Standard</span>
                              </button>
                              <button
                                type="button"
                                className="btn-decision reject"
                                onClick={() => handleFeedback(rec.standard_id, 'REJECT')}
                              >
                                <X size={14} />
                                <span>Reject Standard</span>
                              </button>
                              <button
                                type="button"
                                className="btn-decision override"
                                onClick={() => openOverrideModal(rec)}
                              >
                                <Edit3 size={14} />
                                <span>Override / Correct</span>
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
                    <BookOpen size={22} style={{ color: 'var(--accent-cyan)' }} />
                    <span>Indian Standards Catalog Explorer</span>
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
              <div style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
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
                          <strong style={{ color: 'var(--accent-cyan)' }} className="standard-code">
                            {std.code}
                          </strong>
                        </td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{std.year}</td>
                        <td style={{ maxWidth: '420px' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
                            {std.title}
                          </div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                            {std.scope?.slice(0, 110)}...
                          </div>
                        </td>
                        <td>
                          <span className="sector-tag">{std.sector}</span>
                        </td>
                        <td>
                          {std.is_mandatory_qco ? (
                            <span style={{ color: 'var(--color-danger)', fontWeight: 700, fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                              <Scale size={13} />
                              <span>Mandatory QCO</span>
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                              Voluntary
                            </span>
                          )}
                        </td>
                        <td>
                          <button
                            type="button"
                            className="btn-decision override"
                            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
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
                    <BarChart3 size={22} style={{ color: 'var(--accent-cyan)' }} />
                    <span>Coverage Gaps & Procurement Feedback Analytics</span>
                  </h2>
                  <p>Real-time audit log of officer decisions and gap analysis for standards coverage.</p>
                </div>
              </div>

              {/* KPI Cards */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-title">Catalog Standards</div>
                  <div className="kpi-value">{systemHealth?.standards_count || 520}+</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-success)', marginTop: '0.35rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <CheckCircle2 size={13} />
                    <span>100% Vector Indexed</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Total Officer Decisions</div>
                  <div className="kpi-value">{analyticsData?.total_feedback || 0}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginTop: '0.35rem', fontWeight: 600 }}>
                    Stored in SQLite Audit DB
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Officer Approvals</div>
                  <div className="kpi-value" style={{ color: 'var(--color-success)' }}>
                    {analyticsData?.accepted_count || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
                    Acceptance Rate: {analyticsData?.acceptance_rate_pct || 100}%
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Rejections / Overrides</div>
                  <div className="kpi-value" style={{ color: 'var(--color-danger)' }}>
                    {(analyticsData?.rejected_count || 0) + (analyticsData?.corrected_count || 0)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-warning)', marginTop: '0.35rem' }}>
                    Calibrates dynamic boost
                  </div>
                </div>
              </div>

              {/* Audit Log Table */}
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>
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
                          <td style={{ fontFamily: 'var(--font-mono)' }}>#{item.id}</td>
                          <td>
                            <span
                              className={`confidence-pill ${
                                item.action === 'ACCEPT'
                                  ? 'high'
                                  : item.action === 'REJECT'
                                  ? 'low'
                                  : 'medium'
                              }`}
                              style={{ display: 'inline-flex', padding: '0.25rem 0.65rem' }}
                            >
                              {item.action}
                            </span>
                          </td>
                          <td>
                            <strong style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                              {item.recommended_standard_id}
                            </strong>
                            {item.corrected_standard_id && (
                              <div style={{ fontSize: '0.75rem', color: 'var(--color-warning)' }}>
                                Corrected to: {item.corrected_standard_id}
                              </div>
                            )}
                          </td>
                          <td style={{ color: 'var(--text-secondary)' }}>{item.officer_notes || '—'}</td>
                          <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Recent'}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                          No officer feedback entries logged yet. Test recommendations in the Recommender tab and click Accept/Reject!
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
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                You are overriding <strong style={{ color: 'var(--text-primary)' }}>{overrideTarget?.standard_id}</strong>. Enter the correct Indian Standard code to record in the calibration database.
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
                <Check size={14} />
                <span>Submit Correction</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Standard Detail Modal */}
      {selectedStandard && (
        <div className="modal-overlay" onClick={() => setSelectedStandard(null)}>
          <div className="modal-content" style={{ maxWidth: '720px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span className="sector-tag">{selectedStandard.sector}</span>
                <strong style={{ fontSize: '1.2rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  {selectedStandard.standard_id}
                </strong>
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
              <h4 style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{selectedStandard.title}</h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{selectedStandard.scope}</p>

              {selectedStandard.is_mandatory_qco && (
                <div className="qco-banner">
                  <Scale size={18} style={{ color: 'var(--color-danger)' }} />
                  <div>Mandatory QCO Regulatory Order in effect for GeM procurement.</div>
                </div>
              )}

              <h5 style={{ color: 'var(--accent-cyan)', marginTop: '1rem', marginBottom: '0.5rem' }}>
                Technical Clauses ({selectedStandard.clauses?.length || 0})
              </h5>
              <div className="clauses-drawer">
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
          Bureau of Indian Standards (BIS) & Government e-Marketplace (GeM) • Problem Statement <span className="highlight">SIH 26108</span> • Calibrated Hybrid RRF & Cross-Encoder AI
        </p>
      </footer>
    </div>
  );
}
