import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Users, 
  RefreshCw, 
  Award,
  ArrowRight,
  Filter
} from 'lucide-react';
import api from '../api/client';
import SchemeCard from '../components/SchemeCard';
import EligibilityModal from '../components/EligibilityModal';
import { useAuthStore } from '../store/authStore';

export default function EligibilityCheckPage() {
  const { user, token } = useAuthStore();

  const [formData, setFormData] = useState({
    age: user?.age || 28,
    annual_income: user?.annual_income || 180000,
    category: user?.category || 'OBC',
    gender: user?.gender || 'male',
    occupation: user?.occupation || 'farmer',
    state: user?.state || 'Maharashtra',
    residence: user?.residence || 'rural',
    land_holding: user?.land_holding !== undefined ? user.land_holding : true,
    disability: user?.disability || false,
    disability_percentage: user?.disability_percentage || 0,
    bank_account: user?.bank_account !== false,
  });

  const [schemes, setSchemes] = useState([]);
  const [evaluating, setEvaluating] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    // If logged in and profile updates, prefill
    if (user) {
      setFormData((prev) => ({
        ...prev,
        age: user.age ?? prev.age,
        annual_income: user.annual_income ?? prev.annual_income,
        category: user.category ?? prev.category,
        gender: user.gender ?? prev.gender,
        occupation: user.occupation ?? prev.occupation,
        state: user.state ?? prev.state,
        residence: user.residence ?? prev.residence,
        land_holding: user.land_holding ?? prev.land_holding,
        disability: user.disability ?? prev.disability,
      }));
    }
  }, [user]);

  const handleScan = async (e) => {
    if (e) e.preventDefault();
    setEvaluating(true);
    try {
      // 1. Fetch all schemes
      const schemesRes = await api.get('/schemes/');
      const allSchemes = schemesRes.data;

      // 2. Evaluate each scheme against user profile
      const evalPromises = allSchemes.map((s) =>
        api
          .post('/schemes/check-eligibility', {
            scheme_id: s.id,
            user_profile: {
              ...formData,
              annual_income: Number(formData.annual_income),
              age: Number(formData.age),
            },
          })
          .then((res) => ({ scheme: s, eval: res.data }))
          .catch(() => ({ scheme: s, eval: { status: 'unknown', confidence: 0 } }))
      );

      const evaluated = await Promise.all(evalPromises);

      const eligibleList = evaluated.filter((item) => item.eval.status === 'eligible');
      const conditionalList = evaluated.filter((item) => item.eval.status === 'conditionally_eligible');
      const ineligibleList = evaluated.filter((item) => item.eval.status === 'ineligible');

      setResults({
        eligible: eligibleList,
        conditional: conditionalList,
        ineligible: ineligibleList,
        totalChecked: allSchemes.length,
      });
    } catch (err) {
      console.error(err);
      alert('Error running eligibility scanner');
    } finally {
      setEvaluating(false);
    }
  };

  // Run automatically on first mount
  useEffect(() => {
    handleScan();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white/10 text-xs font-semibold text-amber-300">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Rule Matching Engine</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">Citizen Welfare Eligibility Scanner</h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Specify your socio-economic indicators below. Our deterministic rule engine tests all statutory schemes and reveals the ones you qualify for.
          </p>
        </div>
      </div>

      {/* Input Parameters Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-800 mb-4 flex items-center space-x-2">
          <Filter className="w-4 h-4 text-indigo-600" />
          <span>Your Demographic Profile</span>
        </h2>

        <form onSubmit={handleScan} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Age (Years)</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Annual Income (₹)</label>
              <input
                type="number"
                value={formData.annual_income}
                onChange={(e) => setFormData({ ...formData, annual_income: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Category / Caste</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="transgender">Transgender</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Occupation</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                placeholder="e.g. farmer, artisan, student"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">State of Residence</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="e.g. Uttar Pradesh, Maharashtra"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Residence Area</label>
              <select
                value={formData.residence}
                onChange={(e) => setFormData({ ...formData, residence: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
              >
                <option value="rural">Rural (Village)</option>
                <option value="urban">Urban (City / Town)</option>
              </select>
            </div>

            <div className="flex items-center space-x-4 pt-4">
              <label className="flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.land_holding}
                  onChange={(e) => setFormData({ ...formData, land_holding: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span>Landowner</span>
              </label>

              <label className="flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.disability}
                  onChange={(e) => setFormData({ ...formData, disability: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span>PwD (Disability)</span>
              </label>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={evaluating}
              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md transition-all flex items-center space-x-2"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{evaluating ? 'Scanning Catalog...' : 'Scan All Schemes'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {evaluating ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-500 text-sm font-medium">Evaluating rules across central and state welfare databases...</p>
        </div>
      ) : results ? (
        <div className="space-y-10">
          {/* Summary Pills */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center space-x-3">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 shrink-0" />
              <div>
                <div className="text-2xl font-bold">{results.eligible.length}</div>
                <div className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Fully Eligible Schemes</div>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-center space-x-3">
              <AlertCircle className="w-8 h-8 text-amber-600 shrink-0" />
              <div>
                <div className="text-2xl font-bold">{results.conditional.length}</div>
                <div className="text-xs font-semibold uppercase tracking-wider text-amber-700">Conditionally Eligible</div>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-slate-800 flex items-center space-x-3">
              <Users className="w-8 h-8 text-slate-500 shrink-0" />
              <div>
                <div className="text-2xl font-bold">{results.totalChecked}</div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Schemes Screened</div>
              </div>
            </div>
          </div>

          {/* 1. Fully Eligible Schemes */}
          {results.eligible.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <h2 className="text-xl font-bold text-slate-900">
                  Schemes You Qualify For ({results.eligible.length})
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.eligible.map(({ scheme, eval: evalResult }) => (
                  <SchemeCard
                    key={scheme.id}
                    scheme={scheme}
                    eligibilityResult={evalResult}
                    onCheckEligibility={(s) => {
                      setSelectedScheme(s);
                      setModalOpen(true);
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 2. Conditionally Eligible Schemes */}
          {results.conditional.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-amber-600" />
                <h2 className="text-xl font-bold text-slate-900">
                  Conditionally Eligible Schemes ({results.conditional.length})
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.conditional.map(({ scheme, eval: evalResult }) => (
                  <SchemeCard
                    key={scheme.id}
                    scheme={scheme}
                    eligibilityResult={evalResult}
                    onCheckEligibility={(s) => {
                      setSelectedScheme(s);
                      setModalOpen(true);
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}

      {/* Modal */}
      <EligibilityModal
        scheme={selectedScheme}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
