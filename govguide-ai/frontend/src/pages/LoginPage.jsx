import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogIn, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/profile';
  const { login, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Clear any stale error when component mounts
  useEffect(() => {
    clearError();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await login(email, password);
    if (res.success) {
      navigate(from, { replace: true });
    }
  };

  const handleQuickDemo = (demoEmail, demoPass) => {
    clearError();
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="max-w-md mx-auto px-4 py-12 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mx-auto shadow-md">
          <LogIn className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Citizen Sign In</h1>
        <p className="text-xs text-slate-500">
          Access personalized scheme recommendations, document OCR history, and application tracking.
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-5">
        <form onSubmit={handleSubmit} className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); }}
              required
              placeholder="name@example.com"
              autoComplete="email"
              className={`w-full px-3 py-2.5 rounded-xl border text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors ${
                error ? 'border-rose-400 bg-rose-50/30' : 'border-slate-300'
              }`}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => { setPassword(e.target.value); clearError(); }}
                required
                placeholder="Your password"
                autoComplete="current-password"
                className={`w-full px-3 py-2.5 pr-10 rounded-xl border text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors ${
                  error ? 'border-rose-400 bg-rose-50/30' : 'border-slate-300'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 text-rose-700 text-xs rounded-xl border border-rose-200 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Login failed</p>
                <p>{error}</p>
                <p className="mt-1 text-rose-500">Please check your email and password, then try again.</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-semibold text-sm rounded-xl shadow-md transition-all flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Signing In...</span>
              </>
            ) : (
              <span>Sign In to Portal</span>
            )}
          </button>
        </form>

        {/* Demo Fast Login Buttons */}
        <div className="pt-4 border-t border-slate-100 space-y-2">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 text-center">
            Quick Fill Demo Accounts
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('citizen@example.com', 'password123')}
              className="p-2 rounded-lg bg-slate-50 hover:bg-indigo-50 border border-slate-200 text-xs font-semibold text-slate-700 text-center transition-colors"
            >
              👤 Demo Citizen
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('admin@example.com', 'admin123')}
              className="p-2 rounded-lg bg-slate-50 hover:bg-indigo-50 border border-slate-200 text-xs font-semibold text-slate-700 text-center transition-colors"
            >
              🛡️ Demo Admin
            </button>
          </div>
          <p className="text-[10px] text-slate-400 text-center">
            Click a demo button above, then press Sign In
          </p>
        </div>

        <div className="text-center text-xs text-slate-500 pt-1">
          Don't have an account yet?{' '}
          <Link to="/register" className="font-semibold text-indigo-600 hover:text-indigo-700">
            Create an Account
          </Link>
        </div>
      </div>
    </div>
  );
}
