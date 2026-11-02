import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Award, 
  Calendar, 
  MapPin, 
  FileText, 
  ExternalLink, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle,
  Building,
  Tag
} from 'lucide-react';
import api from '../api/client';
import EligibilityModal from '../components/EligibilityModal';

export default function SchemeDetailPage() {
  const { id } = useParams();
  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    const fetchScheme = async () => {
      try {
        const res = await api.get(`/schemes/${id}`);
        setScheme(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchScheme();
  }, [id]);

  if (loading) {
    return <div className="py-24 text-center text-slate-400">Loading scheme guidelines...</div>;
  }

  if (!scheme) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <h2 className="text-2xl font-bold text-slate-800">Scheme Not Found</h2>
        <p className="text-slate-500 text-sm">The requested scheme identifier was not found in the database.</p>
        <Link to="/schemes" className="inline-flex items-center space-x-1 text-sm font-semibold text-indigo-600">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Schemes Catalog</span>
        </Link>
      </div>
    );
  }

  const rules = scheme.eligibility_rules || {};

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <Link
        to="/schemes"
        className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to All Schemes</span>
      </Link>

      {/* Scheme Header Banner */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-md p-6 sm:p-8 space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            {scheme.category}
          </span>
          <span className="flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
            <MapPin className="w-3.5 h-3.5 text-slate-500" />
            <span>{scheme.state_applicability || 'All India'}</span>
          </span>
          {scheme.deadline && (
            <span className="flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
              <Calendar className="w-3.5 h-3.5 text-amber-600" />
              <span>Deadline: {scheme.deadline}</span>
            </span>
          )}
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-snug">
          {scheme.name}
        </h1>

        <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
          {scheme.description}
        </p>

        {/* Benefits Highlight Callout */}
        {scheme.benefits && (
          <div className="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/5 border border-amber-300/60 rounded-2xl p-4 sm:p-5">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-amber-500 text-white rounded-xl shadow-xs shrink-0 mt-0.5">
                <Award className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900">
                  Entitlement & Financial Benefits
                </h4>
                <p className="text-sm font-semibold text-amber-950 leading-relaxed">
                  {scheme.benefits}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Action CTA Bar */}
        <div className="pt-2 flex flex-col sm:flex-row items-center gap-3 border-t border-slate-100">
          <button
            onClick={() => setModalOpen(true)}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md transition-all flex items-center justify-center space-x-2"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Check My Eligibility</span>
          </button>

          {scheme.official_url && (
            <a
              href={scheme.official_url}
              target="_blank"
              rel="noreferrer"
              className="w-full sm:w-auto px-6 py-3 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold text-sm transition-all flex items-center justify-center space-x-2 sm:ml-auto"
            >
              <span>Apply on Official Govt Portal</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>

      {/* Grid: Eligibility Rules & Required Documents */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Eligibility Rules */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <h3 className="font-bold text-slate-900 text-base flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-indigo-600" />
            <span>Official Eligibility Criteria</span>
          </h3>

          <div className="space-y-3 text-sm">
            {rules.income_limit && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Annual Income Ceiling</span>
                <span className="font-semibold text-slate-800">Up to ₹{rules.income_limit.toLocaleString('en-IN')}</span>
              </div>
            )}

            {(rules.age_min || rules.age_max) && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Age Requirement</span>
                <span className="font-semibold text-slate-800">
                  {rules.age_min ? `${rules.age_min} yrs` : 'Any'} - {rules.age_max ? `${rules.age_max} yrs` : 'No max limit'}
                </span>
              </div>
            )}

            {rules.gender && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Gender Applicability</span>
                <span className="font-semibold text-slate-800 capitalize">{rules.gender}</span>
              </div>
            )}

            {rules.categories && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Eligible Categories</span>
                <span className="font-semibold text-slate-800">{rules.categories.join(', ')}</span>
              </div>
            )}

            {rules.occupation && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Target Occupation</span>
                <span className="font-semibold text-slate-800">{rules.occupation.join(', ')}</span>
              </div>
            )}

            {rules.residence && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Residence Area</span>
                <span className="font-semibold text-slate-800 capitalize">{rules.residence}</span>
              </div>
            )}

            {rules.land_holding !== undefined && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Agricultural Land Holding</span>
                <span className="font-semibold text-slate-800">{rules.land_holding ? 'Mandatory' : 'Not required'}</span>
              </div>
            )}

            {rules.disability && (
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Disability (PwD)</span>
                <span className="font-semibold text-slate-800">Required (≥40% disability)</span>
              </div>
            )}

            {rules.excluded_categories && rules.excluded_categories.length > 0 && (
              <div className="py-2">
                <span className="text-xs font-semibold text-rose-600 block mb-1">Excluded Categories:</span>
                <span className="text-xs text-slate-600 bg-rose-50 p-2 rounded-lg block border border-rose-100">
                  {rules.excluded_categories.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Required Documents */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <h3 className="font-bold text-slate-900 text-base flex items-center space-x-2">
            <FileText className="w-5 h-5 text-emerald-600" />
            <span>Required Documents</span>
          </h3>

          <p className="text-xs text-slate-500">
            Keep clear, scanned copies or photographs of the following proofs ready before submitting your application:
          </p>

          <div className="space-y-2.5">
            {(scheme.required_documents || []).map((doc, idx) => (
              <div
                key={idx}
                className="flex items-center space-x-3 p-3 rounded-xl bg-slate-50 border border-slate-200/80"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="text-xs font-semibold text-slate-800 capitalize">
                  {doc.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2">
            <Link
              to="/ocr"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
            >
              <span>Upload and verify documents with OCR right now</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Tags */}
      {scheme.tags && scheme.tags.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <Tag className="w-4 h-4 text-slate-400" />
          {scheme.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs font-medium text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Modal */}
      <EligibilityModal
        scheme={scheme}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
