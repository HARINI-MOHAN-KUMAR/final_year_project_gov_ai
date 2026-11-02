import React from 'react';
import { ShieldAlert, ExternalLink, Heart, Globe2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { translations } from '../i18n/translations';

export default function Footer() {
  const { language } = useAuthStore();
  const t = translations[language] || translations.en;

  return (
    <footer className="bg-slate-900 text-slate-400 text-sm mt-auto border-t border-slate-800">
      {/* Important Advisory Disclaimer Banner */}
      <div className="bg-amber-950/40 border-b border-amber-800/30 py-3 px-4">
        <div className="max-w-7xl mx-auto flex items-start sm:items-center space-x-3 text-amber-200/90 text-xs sm:text-sm">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5 sm:mt-0" />
          <p>
            <strong>Official Advisory Notice:</strong> {t.disclaimer} All government schemes are managed and disbursed exclusively by their respective central and state ministries.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & mission */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg text-white">GovGuide AI</span>
              <span className="text-[10px] bg-indigo-900 text-indigo-300 font-bold px-1.5 py-0.5 rounded">v1.0</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Empowering 1.4 billion citizens with instant, AI-guided scheme eligibility, document verification, and multilingual accessibility.
            </p>
          </div>

          {/* Core Portals */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">Gov Portals</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="https://www.india.gov.in" target="_blank" rel="noreferrer" className="hover:text-indigo-400 flex items-center space-x-1">
                  <span>National Portal of India</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://pmkisan.gov.in" target="_blank" rel="noreferrer" className="hover:text-indigo-400 flex items-center space-x-1">
                  <span>PM-KISAN Samman Nidhi</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://pmaymis.gov.in" target="_blank" rel="noreferrer" className="hover:text-indigo-400 flex items-center space-x-1">
                  <span>Pradhan Mantri Awas Yojana</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://scholarships.gov.in" target="_blank" rel="noreferrer" className="hover:text-indigo-400 flex items-center space-x-1">
                  <span>National Scholarship Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>

          {/* Citizen Services */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">GovGuide AI Services</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="/schemes" className="hover:text-indigo-400">Search Scheme Catalog</a></li>
              <li><a href="/eligibility" className="hover:text-indigo-400">Rule-Based Eligibility Checker</a></li>
              <li><a href="/ocr" className="hover:text-indigo-400">Document Parsing & OCR</a></li>
              <li><a href="/chat" className="hover:text-indigo-400">AI Scheme Guidance Chat</a></li>
              <li><a href="/applications" className="hover:text-indigo-400">Application Status Tracking</a></li>
            </ul>
          </div>

          {/* Helplines */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">Emergency Helplines</h4>
            <div className="space-y-1.5 text-xs text-slate-400">
              <p>National Helpline: <span className="text-indigo-300 font-mono">1947 / 1800-111-555</span></p>
              <p>Kisan Call Center: <span className="text-indigo-300 font-mono">1800-180-1551</span></p>
              <p>Women Helpline: <span className="text-indigo-300 font-mono">1091 / 181</span></p>
              <p>Ayushman Bharat: <span className="text-indigo-300 font-mono">14555</span></p>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500">
          <p>© 2026 GovGuide AI • Academic Project for Citizen Welfare</p>
          <p className="flex items-center space-x-1 mt-2 sm:mt-0">
            <span>Built with care for public empowerment</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 inline fill-rose-500" />
          </p>
        </div>
      </div>
    </footer>
  );
}
