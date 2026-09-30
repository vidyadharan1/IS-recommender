import React, { useState, useEffect } from 'react';
import {
  Search,
  BookOpen,
  Copy,
  Check,
  AlertCircle,
  Sparkles,
  Layers,
  ArrowRight,
  ShieldCheck,
  Building2,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Database,
  X
} from 'lucide-react';

// Read API base URL from import.meta.env.VITE_API_URL with sensible local fallback
const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

const EXAMPLE_QUERIES = [
  {
    category: 'Cement',
    icon: '🏗️',
    title: '43 Grade Portland Cement',
    text: 'Portland cement for residential construction, 43 grade'
  },
  {
    category: 'Steel',
    icon: '🔩',
    title: 'Fe 500D TMT Steel Rebars',
    text: 'Supply of Fe 500D grade TMT deformed steel bars 12mm and 16mm diameter for RCC structure'
  },
  {
    category: 'Safety',
    icon: '🧯',
    title: 'ABC Fire Extinguisher',
    text: 'Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher'
  },
  {
    category: 'Pipes',
    icon: '🚰',
    title: 'uPVC Potable Water Pipes',
    text: 'Unplasticized PVC pipes for potable drinking water supply Class 3'
  },
  {
    category: 'Textiles',
    icon: '😷',
    title: '3-Ply Surgical Masks',
    text: 'Disposable 3-ply surgical face masks with meltblown filter layer'
  }
];

const CATEGORY_COLORS = {
  Cement: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  Steel: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  Electrical: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  Food: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  Textiles: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
  Pipes: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  Paints: 'bg-pink-500/10 text-pink-400 border-pink-500/30',
  Packaging: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
  'Safety Equipment': 'bg-rose-500/10 text-rose-400 border-rose-500/30',
};

export default function App() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);
  const [backendHealth, setBackendHealth] = useState({ online: false, count: 0 });

  // Catalog Browser Modal state
  const [showCatalog, setShowCatalog] = useState(false);
  const [catalogStandards, setCatalogStandards] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [catalogCategory, setCatalogCategory] = useState('All');
  const [catalogSearch, setCatalogSearch] = useState('');
  const [catalogPage, setCatalogPage] = useState(1);
  const [catalogTotal, setCatalogTotal] = useState(0);

  // Check health on mount
  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const url = `${API_BASE_URL}/api/health`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setBackendHealth({ online: true, count: data.standards_count });
      } else {
        setBackendHealth({ online: false, count: 0 });
      }
    } catch {
      setBackendHealth({ online: false, count: 0 });
    }
  };

  const handleRecommend = async (overrideQuery) => {
    const textToSearch = (overrideQuery ?? query).trim();
    if (!textToSearch) {
      setError('Please enter a procurement specification before searching.');
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const url = `${API_BASE_URL}/api/recommend`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: textToSearch, top_k: Number(topK) }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned error status ${res.status}`);
      }

      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to recommendation server.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (isCode) => {
    navigator.clipboard.writeText(isCode);
    setCopiedCode(isCode);
    setTimeout(() => {
      setCopiedCode((curr) => (curr === isCode ? null : curr));
    }, 2000);
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleRecommend();
    }
  };

  // Fetch catalog when modal opens or filter changes
  useEffect(() => {
    if (showCatalog) {
      fetchCatalog(catalogPage, catalogCategory, catalogSearch);
    }
  }, [showCatalog, catalogPage, catalogCategory]);

  const fetchCatalog = async (page = 1, category = 'All', search = '') => {
    setCatalogLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '8',
      });
      if (category && category !== 'All') {
        params.append('category', category);
      }
      if (search && search.trim()) {
        params.append('search', search.trim());
      }

      const url = `${API_BASE_URL}/api/standards?${params.toString()}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setCatalogStandards(data.standards || []);
        setCatalogTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Catalog fetch error:', err);
    } finally {
      setCatalogLoading(false);
    }
  };

  const handleCatalogSearchSubmit = (e) => {
    e.preventDefault();
    setCatalogPage(1);
    fetchCatalog(1, catalogCategory, catalogSearch);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Background ambient lighting */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Navigation Header */}
      <header className="relative z-10 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0">
        <div className="max-w-6xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  StandardsFinder
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  SIH26108
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Bureau of Indian Standards (BIS) Recommendation Engine
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCatalog(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
              title="View full standards dataset"
            >
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Browse Catalog</span>
            </button>

            {/* Health pill */}
            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                backendHealth.online
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
              title={
                backendHealth.online
                  ? `Backend active (${backendHealth.count} standards indexed)`
                  : 'Backend offline or connecting...'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendHealth.online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
                }`}
              ></span>
              <span className="hidden sm:inline">
                {backendHealth.online ? `${backendHealth.count} Standards` : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 flex-1 max-w-5xl mx-auto w-full px-4 py-8 flex flex-col gap-8">
        {/* Hero Section */}
        <section className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-medium text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Ministry of Consumer Affairs, Food & Public Distribution</span>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
            Procurement to <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400">Indian Standards</span> in Seconds
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
            Input unstructured procurement specifications, RFPs, or tender requirements. Get accurately ranked BIS / IS codes powered by TF-IDF similarity and keyword boosting.
          </p>
        </section>

        {/* Input Card */}
        <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl backdrop-blur-md transition-all">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label htmlFor="procurement-spec" className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Search className="w-4 h-4 text-cyan-400" />
                <span>Procurement Specification / Tender Description</span>
              </label>
              <div className="flex items-center gap-2">
                <label htmlFor="top-k" className="text-xs text-slate-400">Top Results:</label>
                <select
                  id="top-k"
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                >
                  <option value={3}>Top 3</option>
                  <option value={5}>Top 5</option>
                  <option value={10}>Top 10</option>
                </select>
              </div>
            </div>

            {/* Big Textarea */}
            <div className="relative">
              <textarea
                id="procurement-spec"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={4}
                placeholder="e.g. Portland cement for residential construction, 43 grade with compressive strength..."
                className="w-full bg-slate-950/70 border border-slate-800 focus:border-cyan-500 rounded-xl p-4 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition resize-y"
              ></textarea>
              <div className="absolute right-3 bottom-3 text-xs text-slate-500 pointer-events-none hidden sm:block">
                Press <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">Enter</kbd>
              </div>
            </div>

            {/* Buttons Row */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
              <div className="flex items-center gap-2">
                {query && (
                  <button
                    onClick={() => setQuery('')}
                    className="text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition"
                  >
                    Clear Text
                  </button>
                )}
              </div>

              <button
                id="find-standards-btn"
                onClick={() => handleRecommend()}
                disabled={loading || !query.trim()}
                className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg shadow-indigo-500/25"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-white" />
                    <span>Analyzing Specification...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-cyan-200" />
                    <span>Find Standards</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {/* Quick Clickable Example Queries */}
            <div className="pt-3 border-t border-slate-800/80">
              <p className="text-xs font-medium text-slate-400 mb-2">Click an example to test:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_QUERIES.map((ex, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQuery(ex.text);
                      handleRecommend(ex.text);
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 hover:border-slate-600 transition text-left"
                  >
                    <span>{ex.icon}</span>
                    <span className="font-semibold text-slate-200">{ex.category}:</span>
                    <span className="text-slate-400 truncate max-w-[200px]">{ex.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Error State */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 flex items-start gap-3 text-rose-300">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 text-sm">
              <p className="font-semibold text-rose-200">Recommendation Failed</p>
              <p className="mt-0.5 text-xs text-rose-300/90">{error}</p>
            </div>
            <button
              onClick={() => handleRecommend()}
              className="text-xs font-medium px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State Skeleton */}
        {loading && (
          <div className="space-y-4 animate-pulse">
            <div className="h-5 w-48 bg-slate-800 rounded"></div>
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="h-6 w-32 bg-slate-800 rounded"></div>
                  <div className="h-6 w-20 bg-slate-800 rounded-full"></div>
                </div>
                <div className="h-4 w-3/4 bg-slate-800 rounded"></div>
                <div className="h-2 w-full bg-slate-800 rounded-full"></div>
                <div className="flex gap-2">
                  <div className="h-5 w-16 bg-slate-800 rounded-full"></div>
                  <div className="h-5 w-24 bg-slate-800 rounded-full"></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Section */}
        {!loading && hasSearched && results.length > 0 && (
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Layers className="w-5 h-5 text-cyan-400" />
                <span>Recommended Indian Standards ({results.length})</span>
              </h2>
              <span className="text-xs text-slate-400">Ranked by relevance</span>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {results.map((item, index) => {
                const catClass =
                  CATEGORY_COLORS[item.category] ||
                  'bg-slate-800 text-slate-300 border-slate-700';

                return (
                  <div
                    key={index}
                    className="group bg-slate-900/90 border border-slate-800/80 hover:border-slate-700 rounded-2xl p-5 sm:p-6 transition shadow-md hover:shadow-xl relative overflow-hidden"
                  >
                    {/* Rank indicator badge */}
                    <div className="absolute top-0 right-0 w-12 h-12 overflow-hidden pointer-events-none">
                      <div className="absolute transform rotate-45 bg-slate-800 text-slate-400 text-[10px] font-bold py-0.5 right-[-35px] top-[14px] w-[110px] text-center">
                        #{index + 1}
                      </div>
                    </div>

                    <div className="flex flex-col gap-4">
                      {/* Top Header: Code, Category, Copy button */}
                      <div className="flex flex-wrap items-center justify-between gap-2 pr-8">
                        <div className="flex flex-wrap items-center gap-2.5">
                          <span className="text-lg sm:text-xl font-mono font-bold tracking-tight text-cyan-400">
                            {item.is_code}
                          </span>
                          <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full border ${catClass}`}>
                            {item.category}
                          </span>
                        </div>

                        <button
                          onClick={() => copyToClipboard(item.is_code)}
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                          title="Copy IS Code to clipboard"
                        >
                          {copiedCode === item.is_code ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-emerald-400 font-semibold">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5 text-slate-400" />
                              <span>Copy Code</span>
                            </>
                          )}
                        </button>
                      </div>

                      {/* Title */}
                      <h3 className="text-base sm:text-lg font-semibold text-slate-100 group-hover:text-cyan-300 transition">
                        {item.title}
                      </h3>

                      {/* Relevance Score Bar */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-slate-400 font-medium">Relevance Score</span>
                          <span className="font-bold text-cyan-400">{item.score}% Match</span>
                        </div>
                        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ease-out ${
                              item.score >= 85
                                ? 'bg-gradient-to-r from-emerald-500 to-cyan-400'
                                : item.score >= 65
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500'
                                : 'bg-gradient-to-r from-blue-500 to-indigo-500'
                            }`}
                            style={{ width: `${Math.max(5, item.score)}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Reason / Explanation Card */}
                      <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-xs sm:text-sm text-slate-300 flex items-start gap-2.5">
                        <Sparkles className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold text-slate-200">Recommendation Rationale: </span>
                          <span>{item.reason}</span>
                        </div>
                      </div>

                      {/* Matched Keywords */}
                      {item.matched_keywords && item.matched_keywords.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          <span className="text-xs text-slate-400 mr-1">Matched Keywords:</span>
                          {item.matched_keywords.map((kw, kidx) => (
                            <span
                              key={kidx}
                              className="px-2 py-0.5 text-xs rounded-md bg-slate-800 text-slate-300 border border-slate-700/60 font-mono"
                            >
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Empty State after search */}
        {!loading && hasSearched && results.length === 0 && !error && (
          <div className="text-center py-12 px-4 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-3">
            <BookOpen className="w-10 h-10 text-slate-500 mx-auto" />
            <h3 className="text-base font-semibold text-slate-200">No matching standards found</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              We couldn't find an exact Indian Standard match for this query. Try adding specific material names (e.g. Portland cement, TMT rebars, uPVC pipes) or click an example above.
            </p>
          </div>
        )}

        {/* Initial Empty State */}
        {!hasSearched && (
          <section className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 text-center space-y-2">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto">
                <Search className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Natural Text Processing</h4>
              <p className="text-xs text-slate-400">
                Understands trade terminology, grades (e.g. Fe 500D, 43 Grade), dimensions, and domain synonyms.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 text-center space-y-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200">BIS Compliance Ready</h4>
              <p className="text-xs text-slate-400">
                Maps directly to authentic Bureau of Indian Standards specifications across 9 critical procurement domains.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 text-center space-y-2">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto">
                <Sparkles className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Lightweight & Fast</h4>
              <p className="text-xs text-slate-400">
                Optimized TF-IDF algorithm responds in milliseconds while consuming under 100MB RAM.
              </p>
            </div>
          </section>
        )}
      </main>

      {/* Catalog Modal */}
      {showCatalog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-lg text-white">Indian Standards Catalog</h3>
                <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700">
                  {catalogTotal} Total
                </span>
              </div>
              <button
                onClick={() => setShowCatalog(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Filters */}
            <div className="p-4 border-b border-slate-800 bg-slate-950/40 flex flex-col sm:flex-row gap-3">
              <form onSubmit={handleCatalogSearchSubmit} className="flex-1 flex gap-2">
                <input
                  type="text"
                  placeholder="Search code or keywords (e.g., cement, IS 1786)..."
                  value={catalogSearch}
                  onChange={(e) => setCatalogSearch(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition"
                >
                  Search
                </button>
              </form>

              <select
                value={catalogCategory}
                onChange={(e) => {
                  setCatalogCategory(e.target.value);
                  setCatalogPage(1);
                }}
                className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                <option value="All">All Categories</option>
                <option value="Cement">Cement</option>
                <option value="Steel">Steel</option>
                <option value="Electrical">Electrical</option>
                <option value="Food">Food</option>
                <option value="Textiles">Textiles</option>
                <option value="Pipes">Pipes</option>
                <option value="Paints">Paints</option>
                <option value="Packaging">Packaging</option>
                <option value="Safety Equipment">Safety Equipment</option>
              </select>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {catalogLoading ? (
                <div className="text-center py-12 text-slate-400 flex items-center justify-center gap-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-cyan-400" />
                  <span>Loading standards...</span>
                </div>
              ) : catalogStandards.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-sm">
                  No standards found matching your criteria.
                </div>
              ) : (
                catalogStandards.map((std, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl hover:border-slate-700 transition space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-cyan-400 text-sm">{std.is_code}</span>
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                          {std.category}
                        </span>
                      </div>
                      <button
                        onClick={() => {
                          setQuery(std.title);
                          setShowCatalog(false);
                          handleRecommend(std.title);
                        }}
                        className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                      >
                        <span>Test Query</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <p className="text-xs font-semibold text-slate-200">{std.title}</p>
                    <p className="text-xs text-slate-400 line-clamp-2">{std.scope}</p>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer Pagination */}
            <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>Page {catalogPage} of {Math.max(1, Math.ceil(catalogTotal / 8))}</span>
              <div className="flex items-center gap-2">
                <button
                  disabled={catalogPage <= 1 || catalogLoading}
                  onClick={() => setCatalogPage((p) => Math.max(1, p - 1))}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 transition"
                >
                  Previous
                </button>
                <button
                  disabled={catalogPage >= Math.ceil(catalogTotal / 8) || catalogLoading}
                  onClick={() => setCatalogPage((p) => p + 1)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 transition"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-slate-900/40 py-6 mt-auto">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span>StandardsFinder © {new Date().getFullYear()}</span>
            <span>•</span>
            <span>Smart India Hackathon SIH26108</span>
          </div>
          <div>
            <span>Bureau of Indian Standards (BIS) Recommendation AI</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
