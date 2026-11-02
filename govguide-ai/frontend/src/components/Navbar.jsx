import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Compass, 
  ShieldCheck, 
  FileSearch, 
  MessageSquareText, 
  FileSpreadsheet, 
  Globe, 
  User, 
  LogOut, 
  Menu, 
  X,
  Layers,
  Sparkles
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { translations } from '../i18n/translations';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, token, logout, language, setLanguage } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const t = translations[language] || translations.en;

  const navLinks = [
    { name: t.explore_schemes || 'Schemes', path: '/schemes', icon: Compass },
    { name: t.check_eligibility || 'Check Eligibility', path: '/eligibility', icon: ShieldCheck, highlight: true },
    { name: t.upload_docs || 'Document OCR', path: '/ocr', icon: FileSearch },
    { name: t.ask_ai || 'AI Assistant', path: '/chat', icon: MessageSquareText },
    { name: t.my_applications || 'Track Applications', path: '/applications', icon: FileSpreadsheet, authRequired: true },
    { name: 'Admin', path: '/admin', icon: Layers, adminOnly: true },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
      {/* Top Advisory Bar */}
      <div className="bg-slate-900 text-slate-300 text-xs px-4 py-1.5 flex justify-between items-center tracking-wide">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span><strong>National Citizen Advisory Portal</strong> • Intelligent Scheme Recommendation</span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 bg-slate-800 px-2 py-0.5 rounded text-[11px] text-slate-200">
            <Globe className="w-3 h-3 text-indigo-400" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent border-none text-slate-200 focus:outline-hidden cursor-pointer"
            >
              <option value="en" className="bg-slate-900">English (EN)</option>
              <option value="hi" className="bg-slate-900">हिंदी (Hindi)</option>
              <option value="ta" className="bg-slate-900">தமிழ் (Tamil)</option>
              <option value="bn" className="bg-slate-900">বাংলা (Bengali)</option>
            </select>
          </div>
          <span className="hidden sm:inline text-slate-400">Helpline: 1800-111-555</span>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-700 via-indigo-600 to-amber-500 p-0.5 shadow-md flex items-center justify-center">
              <div className="w-full h-full bg-white rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-indigo-600 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-indigo-900 via-indigo-700 to-amber-600 bg-clip-text text-transparent">
                  GovGuide
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-indigo-100 text-indigo-700 rounded-md tracking-wider">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-medium -mt-1 tracking-tight">Citizen Welfare Assistant</p>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => {
              if (link.authRequired && !token) return null;
              if (link.adminOnly && (!user || !user.is_admin)) return null;

              const Icon = link.icon;
              const isActive = location.pathname === link.path;

              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                      : 'text-slate-600 hover:text-indigo-600 hover:bg-slate-100/70'
                  } ${link.highlight ? 'border border-indigo-200/80 text-indigo-700 bg-indigo-50/50' : ''}`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Action / Auth */}
          <div className="hidden md:flex items-center space-x-3">
            {token ? (
              <div className="flex items-center space-x-3">
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/40 transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shadow-xs">
                    {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <span className="text-sm font-medium text-slate-700 max-w-[120px] truncate">
                    {user?.full_name || 'Profile'}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-2 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-sm font-semibold text-slate-700 hover:text-indigo-600 rounded-lg transition-colors"
                >
                  {t.login}
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm hover:shadow transition-all"
                >
                  {t.register}
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu trigger */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-5 space-y-2 shadow-lg">
          {navLinks.map((link) => {
            if (link.authRequired && !token) return null;
            if (link.adminOnly && (!user || !user.is_admin)) return null;

            const Icon = link.icon;
            const isActive = location.pathname === link.path;

            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-base font-medium ${
                  isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-5 h-5 text-indigo-500" />
                <span>{link.name}</span>
              </Link>
            );
          })}

          <div className="pt-4 border-t border-slate-100">
            {token ? (
              <div className="space-y-2">
                <Link
                  to="/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-700 hover:bg-slate-50 font-medium"
                >
                  <User className="w-5 h-5 text-slate-500" />
                  <span>{user?.full_name || 'My Profile'}</span>
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-rose-600 hover:bg-rose-50 font-medium"
                >
                  <LogOut className="w-5 h-5" />
                  <span>{t.logout}</span>
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2 pt-2">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-center py-2.5 rounded-lg border border-slate-300 text-slate-700 font-semibold"
                >
                  {t.login}
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-center py-2.5 rounded-lg bg-indigo-600 text-white font-semibold"
                >
                  {t.register}
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
