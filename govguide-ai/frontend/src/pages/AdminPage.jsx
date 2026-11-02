import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Users, 
  FileSpreadsheet, 
  ShieldAlert, 
  ExternalLink, 
  Sparkles, 
  CheckCircle,
  Clock,
  Search
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function AdminPage() {
  const { user } = useAuthStore();
  const [schemes, setSchemes] = useState([]);
  const [stats, setStats] = useState({
    totalSchemes: 0,
    totalCategories: 0,
    activeEngine: 'Rule-Based + RAG Fallback',
    dbStatus: 'Connected (SQLite)',
  });
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAdminData = async () => {
      try {
        const [schemesRes, catRes] = await Promise.all([
          api.get('/schemes/'),
          api.get('/schemes/categories'),
        ]);
        setSchemes(schemesRes.data);
        setStats({
          totalSchemes: schemesRes.data.length,
          totalCategories: catRes.data.categories?.length || 0,
          activeEngine: 'Rule-Based + TF-IDF RAG',
          dbStatus: 'Operational',
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadAdminData();
  }, []);

  const filteredSchemes = schemes.filter((s) =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 text-indigo-700">
              Administrative Control
            </span>
            <span className="text-xs text-slate-400">GovGuide AI Engine Monitor</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">System Administration</h1>
        </div>

        <a
          href="/api/docs"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl shadow-xs flex items-center space-x-1.5 shrink-0"
        >
          <span>Open FastAPI Swagger Docs</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Schemes Catalogued</div>
          <div className="text-3xl font-extrabold text-slate-900">{stats.totalSchemes}</div>
          <div className="text-xs text-emerald-600 font-medium">Synced from schemes.json</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Welfare Sectors</div>
          <div className="text-3xl font-extrabold text-indigo-600">{stats.totalCategories}</div>
          <div className="text-xs text-slate-500 font-medium">Agriculture, Housing, Education, etc.</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">AI / ML Engine Status</div>
          <div className="text-sm font-extrabold text-slate-900 truncate">{stats.activeEngine}</div>
          <div className="text-xs text-emerald-600 font-medium">Confidence scoring ready</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Database Engine</div>
          <div className="text-3xl font-extrabold text-slate-900">SQLite</div>
          <div className="text-xs text-slate-500 font-medium">{stats.dbStatus}</div>
        </div>
      </div>

      {/* Scheme Management Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm overflow-hidden space-y-4 p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Catalogued Government Schemes</h2>
            <p className="text-xs text-slate-500">Live registry of schemes queried by the recommendation engine</p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter schemes..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Scheme Name</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Applicability</th>
                <th className="px-4 py-3">Income Cap</th>
                <th className="px-4 py-3">Official Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredSchemes.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-indigo-700">{s.id}</td>
                  <td className="px-4 py-3 font-semibold text-slate-900 max-w-xs truncate">{s.name}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-md font-medium bg-slate-100 text-slate-700">
                      {s.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{s.state_applicability || 'All India'}</td>
                  <td className="px-4 py-3 font-medium text-slate-700">
                    {s.eligibility_rules?.income_limit
                      ? `₹${s.eligibility_rules.income_limit.toLocaleString('en-IN')}`
                      : 'None'}
                  </td>
                  <td className="px-4 py-3">
                    {s.official_url ? (
                      <a
                        href={s.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
                      >
                        <span>Portal</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
