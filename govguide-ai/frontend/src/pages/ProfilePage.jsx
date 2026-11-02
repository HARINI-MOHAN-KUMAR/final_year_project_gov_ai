import React, { useState, useEffect } from 'react';
import { 
  User, 
  ShieldCheck, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  Percent, 
  MapPin, 
  Briefcase, 
  GraduationCap, 
  DollarSign 
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function ProfilePage() {
  const { user, token, updateProfile, fetchProfile } = useAuthStore();
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    age: '',
    gender: 'male',
    annual_income: '',
    education: 'graduate',
    occupation: 'farmer',
    category: 'General',
    state: 'Uttar Pradesh',
    disability: false,
    disability_percentage: 0,
    marital_status: 'single',
    residence: 'rural',
    land_holding: false,
    bank_account: true,
    preferred_language: 'en',
  });

  const [completeness, setCompleteness] = useState({ score: 0, missing_fields: [] });
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        phone: user.phone || '',
        age: user.age !== null && user.age !== undefined ? user.age : '',
        gender: user.gender || 'male',
        annual_income: user.annual_income !== null && user.annual_income !== undefined ? user.annual_income : '',
        education: user.education || 'graduate',
        occupation: user.occupation || 'farmer',
        category: user.category || 'General',
        state: user.state || 'Uttar Pradesh',
        disability: Boolean(user.disability),
        disability_percentage: user.disability_percentage || 0,
        marital_status: user.marital_status || 'single',
        residence: user.residence || 'rural',
        land_holding: Boolean(user.land_holding),
        bank_account: user.bank_account !== false,
        preferred_language: user.preferred_language || 'en',
      });
    }

    const loadCompleteness = async () => {
      try {
        const res = await api.get('/profile/completeness');
        setCompleteness({
          score: res.data.completeness_percentage || res.data.percentage || 75,
          missing_fields: res.data.missing_fields || [],
        });
      } catch (err) {
        // Fallback calculation
        let filled = 0;
        const total = 10;
        if (formData.full_name) filled++;
        if (formData.age) filled++;
        if (formData.annual_income) filled++;
        if (formData.category) filled++;
        if (formData.state) filled++;
        if (formData.occupation) filled++;
        if (formData.residence) filled++;
        if (formData.education) filled++;
        setCompleteness({ score: Math.round((filled / total) * 100), missing_fields: [] });
      }
    };
    loadCompleteness();
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      const payload = {
        ...formData,
        age: formData.age ? Number(formData.age) : null,
        annual_income: formData.annual_income ? Number(formData.annual_income) : null,
        disability_percentage: formData.disability ? Number(formData.disability_percentage) : 0,
      };

      const res = await updateProfile(payload);
      if (res.success) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 4000);
      } else {
        setError(res.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!token) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <User className="w-12 h-12 text-slate-400 mx-auto" />
        <h2 className="text-2xl font-bold text-slate-800">Citizen Profile</h2>
        <p className="text-sm text-slate-500">Please sign in to view and manage your citizen demographic attributes.</p>
        <a href="/login" className="inline-block px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-semibold text-sm">
          Sign In
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Profile Header & Completeness Meter */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-700 to-amber-500 text-white font-extrabold text-2xl flex items-center justify-center shadow-md">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {user?.full_name || 'Citizen Profile'}
              </h1>
              <p className="text-xs text-slate-500">{user?.email}</p>
              <div className="mt-1 flex items-center space-x-2">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Active Citizen Account
                </span>
                {user?.is_admin && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                    Administrator
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Completeness Gauge */}
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/80 min-w-[220px]">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-1.5">
              <span>Profile Completeness</span>
              <span className="text-indigo-600 font-extrabold">{completeness.score}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-600 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${completeness.score}%` }}
              ></div>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              A 100% complete profile unlocks accurate eligibility matching.
            </p>
          </div>
        </div>
      </div>

      {/* Profile Form */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Demographic & Economic Attributes</h2>
            <p className="text-xs text-slate-500">
              Used strictly by the local eligibility engine to match statutory criteria.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-sm">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Full Legal Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Phone Number</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="10-digit mobile number"
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Age</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="transgender">Transgender</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Social Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="General">General</option>
                <option value="OBC">OBC (Other Backward Class)</option>
                <option value="SC">SC (Scheduled Caste)</option>
                <option value="ST">ST (Scheduled Tribe)</option>
                <option value="EWS">EWS (Economically Weaker Section)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Annual Family Income (₹)</label>
              <input
                type="number"
                value={formData.annual_income}
                onChange={(e) => setFormData({ ...formData, annual_income: e.target.value })}
                placeholder="e.g. 150000"
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Education Level</label>
              <select
                value={formData.education}
                onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="below_10th">Below 10th</option>
                <option value="10th_pass">10th Matriculate</option>
                <option value="12th_pass">12th Intermediate</option>
                <option value="diploma">Diploma / Polytechnic</option>
                <option value="graduate">Graduate (B.A, B.Sc, B.Tech, etc.)</option>
                <option value="post_graduate">Post Graduate</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Occupation</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                placeholder="farmer, student, artisan, unemployed, self_employed"
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">State of Residence</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="e.g. Uttar Pradesh, Maharashtra"
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Residence Area</label>
              <select
                value={formData.residence}
                onChange={(e) => setFormData({ ...formData, residence: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="rural">Rural (Village)</option>
                <option value="urban">Urban (City / Town)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Marital Status</label>
              <select
                value={formData.marital_status}
                onChange={(e) => setFormData({ ...formData, marital_status: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="single">Single / Unmarried</option>
                <option value="married">Married</option>
                <option value="widow">Widow / Widower</option>
                <option value="divorced">Divorced / Separated</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Preferred Language</label>
              <select
                value={formData.preferred_language}
                onChange={(e) => setFormData({ ...formData, preferred_language: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              >
                <option value="en">English</option>
                <option value="hi">हिंदी (Hindi)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="bn">বাংলা (Bengali)</option>
              </select>
            </div>
          </div>

          <div className="flex flex-wrap gap-6 pt-4 border-t border-slate-100">
            <label className="flex items-center space-x-2 text-xs font-semibold text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.land_holding}
                onChange={(e) => setFormData({ ...formData, land_holding: e.target.checked })}
                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
              />
              <span>Owns Agricultural Land</span>
            </label>

            <label className="flex items-center space-x-2 text-xs font-semibold text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.bank_account}
                onChange={(e) => setFormData({ ...formData, bank_account: e.target.checked })}
                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
              />
              <span>Has Active Bank Account (DBT Linked)</span>
            </label>

            <label className="flex items-center space-x-2 text-xs font-semibold text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.disability}
                onChange={(e) => setFormData({ ...formData, disability: e.target.checked })}
                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
              />
              <span>Person with Benchmark Disability (PwD)</span>
            </label>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 text-rose-700 text-xs rounded-xl border border-rose-200">
              {error}
            </div>
          )}

          {saveSuccess && (
            <div className="p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl border border-emerald-200 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Citizen profile successfully updated and saved to database!</span>
            </div>
          )}

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl shadow-md transition-all flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving Changes...' : 'Save Profile Details'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
