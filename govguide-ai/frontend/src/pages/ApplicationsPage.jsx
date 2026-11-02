import React, { useState, useEffect } from 'react';
import { 
  FileSpreadsheet, 
  Plus, 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Building, 
  ExternalLink,
  ChevronRight,
  Edit2
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function ApplicationsPage() {
  const { token } = useAuthStore();
  const [applications, setApplications] = useState([]);
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  // New Application Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [newApp, setNewApp] = useState({
    scheme_id: '',
    status: 'drafting',
    application_ref: '',
    notes: '',
  });

  const fetchApplications = async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const [appsRes, schemesRes] = await Promise.all([
        api.get('/applications/'),
        api.get('/schemes/'),
      ]);
      setApplications(appsRes.data);
      setSchemes(schemesRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [token]);

  const handleCreateApplication = async (e) => {
    e.preventDefault();
    if (!newApp.scheme_id) {
      alert('Please select a scheme.');
      return;
    }

    try {
      await api.post('/applications/', {
        scheme_id: newApp.scheme_id,
        status: newApp.status,
        application_ref: newApp.application_ref,
        notes: newApp.notes,
      });
      setModalOpen(false);
      setNewApp({ scheme_id: '', status: 'drafting', application_ref: '', notes: '' });
      fetchApplications();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add application');
    }
  };

  const handleUpdateStatus = async (appId, newStatus) => {
    try {
      await api.put(`/applications/${appId}`, { status: newStatus });
      fetchApplications();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Approved</span>
          </span>
        );
      case 'submitted':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-300">
            <Clock className="w-3.5 h-3.5" />
            <span>Submitted</span>
          </span>
        );
      case 'under_review':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Under Review</span>
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
            <XCircle className="w-3.5 h-3.5" />
            <span>Rejected</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-800 border border-slate-300">
            <Edit2 className="w-3.5 h-3.5" />
            <span>Drafting / Preparing</span>
          </span>
        );
    }
  };

  const filteredApps = applications.filter((app) => {
    if (statusFilter === 'all') return true;
    return app.status?.toLowerCase() === statusFilter.toLowerCase();
  });

  if (!token) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center space-y-4">
        <FileSpreadsheet className="w-12 h-12 text-slate-400 mx-auto" />
        <h2 className="text-2xl font-bold text-slate-800">Application Tracking Dashboard</h2>
        <p className="text-sm text-slate-500 max-w-md mx-auto">
          Sign in to your citizen account to track submission status, keep application reference numbers, and receive deadline reminders.
        </p>
        <a
          href="/login"
          className="inline-block px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-semibold text-sm shadow-md"
        >
          Sign In Now
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Citizen Application Tracker</h1>
          <p className="text-sm text-slate-500 mt-1">
            Monitor all your government welfare applications, reference IDs, and milestones in one unified dashboard.
          </p>
        </div>

        <button
          onClick={() => setModalOpen(true)}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl shadow-xs transition-all flex items-center justify-center space-x-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Track New Application</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 text-xs font-semibold">
        {['all', 'drafting', 'submitted', 'under_review', 'approved', 'rejected'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-3.5 py-2 rounded-xl capitalize transition-all ${
              statusFilter === status
                ? 'bg-slate-900 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {status.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Applications List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400">Loading your applications...</div>
      ) : filteredApps.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-2xl border border-slate-200 p-8 space-y-3">
          <FileSpreadsheet className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-lg font-bold text-slate-800">No applications tracked under this filter</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You can check eligibility for any scheme and click "Track Application" or add one manually.
          </p>
          <button
            onClick={() => setModalOpen(true)}
            className="px-4 py-2 bg-indigo-50 text-indigo-700 font-semibold text-xs rounded-lg hover:bg-indigo-100"
          >
            Add an Application
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredApps.map((app) => (
            <div
              key={app.id}
              className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs hover:border-indigo-300 transition-all space-y-4"
            >
              <div className="flex justify-between items-start gap-2">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600">
                    Scheme ID: {app.scheme_id}
                  </span>
                  <h3 className="font-bold text-slate-900 text-base mt-0.5">
                    {app.scheme_name || app.scheme_id}
                  </h3>
                </div>
                {getStatusBadge(app.status)}
              </div>

              {/* Meta */}
              <div className="space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200/60">
                {app.application_ref && (
                  <div className="flex justify-between">
                    <span className="text-slate-500">Ack / Reference ID:</span>
                    <span className="font-mono font-bold text-slate-900">{app.application_ref}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-500">Tracked Since:</span>
                  <span className="font-medium text-slate-700">
                    {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'Recent'}
                  </span>
                </div>
                {app.notes && (
                  <div className="pt-1 text-slate-700 italic border-t border-slate-200/60">
                    "{app.notes}"
                  </div>
                )}
              </div>

              {/* Status Update Actions */}
              <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
                <span className="text-xs font-semibold text-slate-500">Change Status:</span>
                <select
                  value={app.status || 'drafting'}
                  onChange={(e) => handleUpdateStatus(app.id, e.target.value)}
                  className="text-xs font-semibold px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="drafting">Drafting</option>
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Application Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Track a Scheme Application</h3>

            <form onSubmit={handleCreateApplication} className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Scheme</label>
                <select
                  value={newApp.scheme_id}
                  onChange={(e) => setNewApp({ ...newApp, scheme_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  required
                >
                  <option value="">-- Choose Scheme --</option>
                  {schemes.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Current Status</label>
                <select
                  value={newApp.status}
                  onChange={(e) => setNewApp({ ...newApp, status: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                >
                  <option value="drafting">Drafting (Gathering Documents)</option>
                  <option value="submitted">Submitted to Official Portal</option>
                  <option value="under_review">Under Review / Verification</option>
                  <option value="approved">Approved / Sanctioned</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Application / Reference Number</label>
                <input
                  type="text"
                  value={newApp.application_ref}
                  onChange={(e) => setNewApp({ ...newApp, application_ref: e.target.value })}
                  placeholder="e.g. DL/2026/AWAS/83921"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Notes / Reminders</label>
                <textarea
                  rows="2"
                  value={newApp.notes}
                  onChange={(e) => setNewApp({ ...newApp, notes: e.target.value })}
                  placeholder="e.g. Document physical verification scheduled for 15th"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs"
                >
                  Save Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
