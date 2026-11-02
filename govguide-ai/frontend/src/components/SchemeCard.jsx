import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  HelpCircle, 
  ArrowUpRight, 
  Sparkles,
  Award
} from 'lucide-react';

export default function SchemeCard({ scheme, eligibilityResult, onCheckEligibility }) {
  const getCategoryColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'agriculture': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'housing': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'healthcare': return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'education': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'social welfare': return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'employment': return 'bg-cyan-50 text-cyan-700 border-cyan-200';
      default: return 'bg-indigo-50 text-indigo-700 border-indigo-200';
    }
  };

  const getStatusBadge = () => {
    if (!eligibilityResult) return null;

    switch (eligibilityResult.status) {
      case 'eligible':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Eligible ({Math.round(eligibilityResult.confidence * 100)}%)</span>
          </span>
        );
      case 'conditionally_eligible':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>Conditionally Eligible</span>
          </span>
        );
      case 'ineligible':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Ineligible</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Check Status</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 hover:border-indigo-300 hover:shadow-lg transition-all duration-200 flex flex-col justify-between overflow-hidden group">
      <div className="p-5">
        {/* Category & Status */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getCategoryColor(scheme.category)}`}>
            {scheme.category || 'General'}
          </span>
          {getStatusBadge()}
        </div>

        {/* Scheme Name */}
        <Link to={`/schemes/${scheme.id}`} className="block group-hover:text-indigo-600 transition-colors">
          <h3 className="font-bold text-slate-900 text-lg line-clamp-2 mb-2 leading-snug">
            {scheme.name}
          </h3>
        </Link>

        {/* Description */}
        <p className="text-slate-600 text-xs sm:text-sm line-clamp-3 mb-4 leading-relaxed">
          {scheme.description}
        </p>

        {/* Benefits Pill */}
        {scheme.benefits && (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/60 rounded-lg p-2.5 mb-4">
            <div className="flex items-start space-x-2">
              <Award className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-amber-800">Financial / In-Kind Benefit</p>
                <p className="text-xs font-medium text-amber-950 line-clamp-2">{scheme.benefits}</p>
              </div>
            </div>
          </div>
        )}

        {/* Applicability Meta */}
        <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500 pt-1">
          <span className="flex items-center space-x-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>{scheme.state_applicability || 'All India'}</span>
          </span>
          {scheme.deadline && (
            <span className="text-slate-400">
              • Deadline: <strong className="text-slate-700">{scheme.deadline}</strong>
            </span>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="bg-slate-50 px-5 py-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <Link
          to={`/schemes/${scheme.id}`}
          className="text-xs font-semibold text-slate-700 hover:text-indigo-600 flex items-center space-x-1"
        >
          <span>View Guidelines</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>

        <div className="flex items-center space-x-2">
          {onCheckEligibility && (
            <button
              onClick={() => onCheckEligibility(scheme)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs transition-colors"
            >
              Check My Eligibility
            </button>
          )}
          {scheme.official_url && (
            <a
              href={scheme.official_url}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60"
              title="Official Portal"
            >
              <ArrowUpRight className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
