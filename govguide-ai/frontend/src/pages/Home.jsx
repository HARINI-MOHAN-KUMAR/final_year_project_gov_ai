import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, 
  Sparkles, 
  ShieldCheck, 
  FileCheck2, 
  MessageSquare, 
  ArrowRight, 
  CheckCircle2, 
  TrendingUp, 
  Users, 
  Award,
  Layers,
  ChevronRight
} from 'lucide-react';
import api from '../api/client';
import SchemeCard from '../components/SchemeCard';
import EligibilityModal from '../components/EligibilityModal';
import { useAuthStore } from '../store/authStore';
import { translations } from '../i18n/translations';

export default function Home() {
  const navigate = useNavigate();
  const { language } = useAuthStore();
  const t = translations[language] || translations.en;

  const [schemes, setSchemes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [schemesRes, catRes] = await Promise.all([
          api.get('/schemes/'),
          api.get('/schemes/categories'),
        ]);
        setSchemes(schemesRes.data.slice(0, 6)); // Top 6 for homepage
        setCategories(catRes.data.categories || []);
      } catch (err) {
        console.error('Failed to load homepage data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/schemes?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleOpenEligibility = (scheme) => {
    setSelectedScheme(scheme);
    setModalOpen(true);
  };

  const categoryIcons = {
    Agriculture: '🌾',
    Housing: '🏠',
    Healthcare: '🏥',
    Education: '🎓',
    'Social Welfare': '🤝',
    Employment: '💼',
    'Women & Child': '👩‍👧',
  };

  return (
    <div className="space-y-16 pb-16">
      {/* ── Hero Section ──────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-b from-indigo-900 via-indigo-950 to-slate-900 text-white pt-16 pb-24 px-4 sm:px-6 lg:px-8">
        {/* Subtle decorative glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-r from-amber-500/10 via-indigo-500/20 to-emerald-500/10 blur-3xl pointer-events-none"></div>

        <div className="relative max-w-5xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-semibold text-amber-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>AI-Driven Citizen Decision Support Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
            Discover Government Schemes <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-amber-300 via-orange-300 to-emerald-300 bg-clip-text text-transparent">
              Tailored Specifically For You
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-300 font-normal leading-relaxed">
            {t.hero_subtitle} Instant rule validation, automated OCR certificate parsing, and multilingual chatbot assistance.
          </p>

          {/* Quick Search Box */}
          <form
            onSubmit={handleSearchSubmit}
            className="max-w-2xl mx-auto bg-white p-2 rounded-2xl shadow-2xl flex flex-col sm:flex-row gap-2 border border-white/20"
          >
            <div className="flex-1 flex items-center px-3 space-x-2">
              <Search className="w-5 h-5 text-slate-400 shrink-0" />
              <input
                type="text"
                placeholder={t.search_placeholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-slate-800 text-sm focus:outline-hidden placeholder:text-slate-400 bg-transparent py-2"
              />
            </div>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-6 py-3 rounded-xl shadow-md transition-all flex items-center justify-center space-x-2 shrink-0"
            >
              <span>Search</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto pt-6 text-left">
            <div className="bg-white/5 backdrop-blur-xs border border-white/10 p-4 rounded-xl">
              <div className="text-2xl font-bold text-amber-300">50+</div>
              <div className="text-xs text-slate-300 font-medium">Major Central & State Schemes</div>
            </div>
            <div className="bg-white/5 backdrop-blur-xs border border-white/10 p-4 rounded-xl">
              <div className="text-2xl font-bold text-emerald-300">100%</div>
              <div className="text-xs text-slate-300 font-medium">Automated Rule Engine</div>
            </div>
            <div className="bg-white/5 backdrop-blur-xs border border-white/10 p-4 rounded-xl">
              <div className="text-2xl font-bold text-indigo-300">6 Docs</div>
              <div className="text-xs text-slate-300 font-medium">OCR Parsers (Aadhaar, Income, etc.)</div>
            </div>
            <div className="bg-white/5 backdrop-blur-xs border border-white/10 p-4 rounded-xl">
              <div className="text-2xl font-bold text-purple-300">4+ Langs</div>
              <div className="text-xs text-slate-300 font-medium">Multilingual Advisory Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Category Quick Access ────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Explore by Welfare Sector</h2>
            <p className="text-sm text-slate-500 mt-1">Browse government welfare programs by area of impact</p>
          </div>
          <Link
            to="/schemes"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-semibold flex items-center space-x-1"
          >
            <span>View All</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {categories.map((cat) => (
            <Link
              key={cat}
              to={`/schemes?category=${encodeURIComponent(cat)}`}
              className="p-4 rounded-xl bg-white border border-slate-200/80 hover:border-indigo-400 hover:shadow-md transition-all text-center flex flex-col items-center justify-center space-y-2 group"
            >
              <span className="text-3xl group-hover:scale-110 transition-transform">
                {categoryIcons[cat] || '🏛️'}
              </span>
              <span className="font-semibold text-xs text-slate-800 group-hover:text-indigo-600 line-clamp-1">
                {cat}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* ── Feature Highlights ────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 text-white rounded-3xl p-8 sm:p-12 shadow-xl relative overflow-hidden">
          <div className="relative z-10 max-w-3xl space-y-6">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-400/20 text-amber-300 border border-amber-400/30">
              Why GovGuide AI?
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Bridging the Gap Between Citizens and Government Entitlements
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Millions of citizens miss out on subsidies, housing, medical aid, and scholarships simply due to complex guidelines, language barriers, and documentation hurdles. GovGuide AI automates this end-to-end.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4">
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base">Rule-Based Matching</h4>
                <p className="text-xs text-slate-400">
                  Calculates exact eligibility across age, income slabs, caste category, land holding, and state quotas.
                </p>
              </div>

              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <FileCheck2 className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base">OCR Document Reader</h4>
                <p className="text-xs text-slate-400">
                  Upload Aadhaar or Income certificates to extract and verify details automatically.
                </p>
              </div>

              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-amber-600/30 border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base">Multilingual AI Chat</h4>
                <p className="text-xs text-slate-400">
                  Ask scheme questions in your local language and receive plain-language explanations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Featured Schemes Grid ────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Prominent Welfare Schemes</h2>
            <p className="text-sm text-slate-500 mt-1">High-impact welfare schemes across India</p>
          </div>
          <Link
            to="/schemes"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-semibold flex items-center space-x-1"
          >
            <span>View All Schemes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading schemes...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schemes.map((scheme) => (
              <SchemeCard
                key={scheme.id}
                scheme={scheme}
                onCheckEligibility={handleOpenEligibility}
              />
            ))}
          </div>
        )}
      </section>

      {/* Eligibility Modal */}
      <EligibilityModal
        scheme={selectedScheme}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
