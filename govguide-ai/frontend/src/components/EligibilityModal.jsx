import React, { useState } from 'react';
import { 
  X, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  FileText, 
  ExternalLink, 
  PlusCircle, 
  ArrowRight,
  ShieldCheck,
  Percent
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function EligibilityModal({ scheme, isOpen, onClose, onApplicationCreated }) {
  const { user, token } = useAuthStore();
  const [formData, setFormData] = useState({
    age: user?.age || 30,
    annual_income: user?.annual_income || 150000,
    category: user?.category || 'General',
    gender: user?.gender || 'male',
    occupation: user?.occupation || 'farmer',
    state: user?.state || 'Uttar Pradesh',
    residence: user?.residence || 'rural',
    disability: user?.disability || false,
    land_holding: user?.land_holding || false,
    bank_account: user?.bank_account !== false,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [trackingSuccess, setTrackingSuccess] = useState(false);

  if (!isOpen || !scheme) return null;

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/schemes/check-eligibility', {
        scheme_id: scheme.id,
        user_profile: {
          ...formData,
          annual_income: Number(formData.annual_income),
          age: Number(formData.age),
        },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to check eligibility');
    } finally {
      setLoading(false);
    }
  };

  const handleTrackApplication = async () => {
    if (!token) {
      alert('Please sign in to track this application in your dashboard.');
      return;
    }
    setTrackingLoading(true);
    try {
      await api.post('/applications/', {
        scheme_id: scheme.id,
        status: result?.status === 'eligible' ? 'drafting' : 'drafting',
        notes: `Checked eligibility on ${new Date().toLocaleDateString()}. Status: ${result?.status || 'Advisory'}`,
      });
      setTrackingSuccess(true);
      if (onApplicationCreated) onApplicationCreated();
    } catch (err) {
      alert(err.response?.data?.detail || 'Could not track application');
    } finally {
      setTrackingLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-900 to-indigo-700 text-white p-5 flex justify-between items-start">
          <div className="space-y-1">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-800/80 text-indigo-200 border border-indigo-600">
              {scheme.category}
            </span>
            <h2 className="text-xl font-bold leading-tight">{scheme.name}</h2>
            <p className="text-xs text-indigo-200">Rule-Based Eligibility Evaluation Engine</p>
          </div>
          <button
            onClick={onClose}
            className="text-indigo-200 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {!result ? (
            <form onSubmit={handleEvaluate} className="space-y-4">
              <p className="text-xs text-slate-500 font-medium">
                Verify or adjust your demographic attributes below to evaluate your eligibility under official scheme criteria:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Age</label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                    min="1"
                    max="120"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Annual Family Income (₹)</label>
                  <input
                    type="number"
                    value={formData.annual_income}
                    onChange={(e) => setFormData({ ...formData, annual_income: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                    min="0"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Social Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    <option value="General">General</option>
                    <option value="OBC">OBC</option>
                    <option value="SC">SC</option>
                    <option value="ST">ST</option>
                    <option value="EWS">EWS</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="transgender">Transgender</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Occupation / Student</label>
                  <input
                    type="text"
                    value={formData.occupation}
                    onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                    placeholder="e.g. farmer, student, artisan, self_employed"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Residence Location</label>
                  <select
                    value={formData.residence}
                    onChange={(e) => setFormData({ ...formData, residence: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    <option value="rural">Rural (Village)</option>
                    <option value="urban">Urban (City / Town)</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-wrap gap-4 pt-2">
                <label className="flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.land_holding}
                    onChange={(e) => setFormData({ ...formData, land_holding: e.target.checked })}
                    className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                  />
                  <span>Owns Agricultural Land</span>
                </label>

                <label className="flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.disability}
                    onChange={(e) => setFormData({ ...formData, disability: e.target.checked })}
                    className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                  />
                  <span>Person with Disability (PwD)</span>
                </label>
              </div>

              {error && (
                <div className="p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md transition-all flex items-center justify-center space-x-2"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>{loading ? 'Evaluating Rules...' : 'Run Eligibility Check'}</span>
              </button>
            </form>
          ) : (
            <div className="space-y-5 animate-in fade-in duration-200">
              {/* Verdict Header */}
              <div
                className={`p-4 rounded-xl border flex items-start space-x-3 ${
                  result.status === 'eligible'
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : result.status === 'conditionally_eligible'
                    ? 'bg-amber-50 border-amber-200 text-amber-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}
              >
                {result.status === 'eligible' ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
                ) : result.status === 'conditionally_eligible' ? (
                  <AlertCircle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
                )}

                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="font-bold text-base capitalize">
                      {result.status.replace('_', ' ')}
                    </h4>
                    <span className="text-xs px-2 py-0.5 rounded-md font-bold bg-white/70">
                      Match: {Math.round((result.confidence || 0.9) * 100)}%
                    </span>
                  </div>
                  <p className="text-xs mt-1 text-slate-700">
                    {result.status === 'eligible'
                      ? 'Congratulations! Based on your criteria, you appear eligible for this scheme.'
                      : result.status === 'conditionally_eligible'
                      ? 'You satisfy primary requirements, but additional verification or documentation may be required.'
                      : 'You do not currently satisfy one or more key criteria for this scheme.'}
                  </p>
                </div>
              </div>

              {/* Reasons / Rules Checked */}
              {result.reasons && result.reasons.length > 0 && (
                <div className="space-y-2">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500">Evaluation Details</h5>
                  <ul className="space-y-1.5 text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200">
                    {result.reasons.map((r, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-indigo-600 font-bold">•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Missing criteria */}
              {result.missing_criteria && result.missing_criteria.length > 0 && (
                <div className="space-y-2">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-rose-600">Unmet Criteria</h5>
                  <ul className="space-y-1 text-xs text-rose-800 bg-rose-50/50 p-3 rounded-lg border border-rose-200">
                    {result.missing_criteria.map((m, i) => (
                      <li key={i} className="flex items-center space-x-1.5">
                        <XCircle className="w-3.5 h-3.5 text-rose-500" />
                        <span>{m}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Required Documents */}
              {scheme.required_documents && scheme.required_documents.length > 0 && (
                <div className="space-y-2">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Documents Needed For Application</span>
                  </h5>
                  <div className="flex flex-wrap gap-1.5">
                    {scheme.required_documents.map((doc, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200"
                      >
                        ✓ {doc.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Next Steps Buttons */}
              <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                <button
                  onClick={() => setResult(null)}
                  className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100"
                >
                  Adjust Parameters
                </button>

                {token && !trackingSuccess ? (
                  <button
                    onClick={handleTrackApplication}
                    disabled={trackingLoading}
                    className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs flex items-center justify-center space-x-1.5"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>{trackingLoading ? 'Saving...' : 'Track Application'}</span>
                  </button>
                ) : trackingSuccess ? (
                  <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 flex items-center space-x-1">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Tracked in Dashboard!</span>
                  </span>
                ) : null}

                {scheme.official_url && (
                  <a
                    href={scheme.official_url}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs flex items-center justify-center space-x-1.5 ml-auto"
                  >
                    <span>Apply on Official Portal</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
