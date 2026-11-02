import React, { useState, useEffect } from 'react';
import { 
  FileSearch, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Sparkles, 
  ArrowRight,
  RefreshCw,
  Copy,
  ShieldCheck,
  Zap
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function OcrPage() {
  const { user, token, updateProfile } = useAuthStore();
  const [selectedFile, setSelectedFile] = useState(null);
  const [docType, setDocType] = useState('aadhaar');
  const [uploading, setUploading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState(null);
  const [syncSuccess, setSyncSuccess] = useState(false);

  // Sample OCR document texts for instant testing
  const sampleDocuments = [
    {
      id: 'aadhaar',
      name: 'Aadhaar Card (Sample)',
      text: `Government of India\nUnique Identification Authority of India\nEnrollment No: 1234/56789/01234\nTo: Rajesh Kumar\nDOB: 15/08/1990\nGender: Male\nAddress: S/O Ramesh Kumar, Village Rampur, District Varanasi, UP - 221001\n9876 5432 1098\nमेरा आधार, मेरी पहचान`,
    },
    {
      id: 'income_certificate',
      name: 'Income Certificate (Sample)',
      text: `GOVERNMENT OF UTTAR PRADESH\nREVENUE DEPARTMENT\nINCOME CERTIFICATE\nCertificate No: UP/INC/2024/987654\nThis is to certify that Sri Rajesh Kumar S/o Ramesh Kumar resident of Rampur, Varanasi has an annual family income of Rs. 1,40,000 (Rupees One Lakh Forty Thousand Only) from all sources.\nDate of Issue: 12/01/2024\nValid for Year: 2024-2025\nTehsildar Varanasi`,
    },
    {
      id: 'community_certificate',
      name: 'Community / Caste Certificate (Sample)',
      text: `GOVERNMENT OF MAHARASHTRA\nSUB-DIVISIONAL OFFICE\nCOMMUNITY, CASTE AND TRIBE CERTIFICATE\nCertificate No: MH/CST/2023/45612\nThis is to certify that Shri Rajesh Kumar son of Ramesh Kumar of village Rampur belongs to Kurmi Caste which is recognized as Other Backward Class (OBC) under Government Resolution.\nCompetent Authority / Sub Divisional Officer`,
    },
    {
      id: 'ration_card',
      name: 'Ration Card (Sample)',
      text: `FOOD AND CIVIL SUPPLIES DEPARTMENT\nNATIONAL FOOD SECURITY CARD (RATION CARD)\nRation Card No: 092019485721\nCard Type: BPL / PHH (Priority Household)\nHead of Family: Rajesh Kumar\nGas Connection: No\nFair Price Shop No: 1045\nNo. of Family Members: 4`,
    },
  ];

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Please choose a file or use one of the one-click sample documents below.');
      return;
    }

    setUploading(true);
    setError(null);
    setSyncSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('doc_type', docType);

      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setExtractedData(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'OCR extraction failed. You can also try testing with the instant sample cards.');
    } finally {
      setUploading(false);
    }
  };

  const handleTestSample = async (sample) => {
    setUploading(true);
    setError(null);
    setSyncSuccess(false);

    // Create a mock text file blob from sample
    try {
      const blob = new Blob([sample.text], { type: 'text/plain' });
      const file = new File([blob], `${sample.id}_sample.txt`, { type: 'text/plain' });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', sample.id);

      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setDocType(sample.id);
      setExtractedData(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to process sample');
    } finally {
      setUploading(false);
    }
  };

  const handleSyncToProfile = async () => {
    if (!token) {
      alert('Please sign in to save extracted attributes to your profile.');
      return;
    }

    const fields = extractedData?.extracted_fields || {};
    const updates = {};

    if (fields.name) updates.full_name = fields.name;
    if (fields.annual_income) updates.annual_income = Number(fields.annual_income);
    if (fields.category) updates.category = fields.category;
    if (fields.gender) updates.gender = fields.gender.toLowerCase();
    if (fields.state) updates.state = fields.state;

    const res = await updateProfile(updates);
    if (res.success) {
      setSyncSuccess(true);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-indigo-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-800/80 text-xs font-semibold text-emerald-200 border border-emerald-600">
            <Zap className="w-3.5 h-3.5 text-amber-300" />
            <span>Tesseract & Regex Document OCR Lab</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">Citizen Document Verification & OCR</h1>
          <p className="text-emerald-100/90 text-sm leading-relaxed">
            Upload Aadhaar, Income certificates, Caste certificates, or Ration cards. Our OCR and pattern extraction pipeline extracts key eligibility identifiers and synchronizes them with your profile.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload Form (Left Column) */}
        <div className="lg:col-span-6 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-bold text-slate-800 flex items-center space-x-2">
              <Upload className="w-5 h-5 text-indigo-600" />
              <span>Upload Certificate or Document</span>
            </h2>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Document Type</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-medium text-slate-800"
                >
                  <option value="aadhaar">Aadhaar Card</option>
                  <option value="income_certificate">Income Certificate (आय प्रमाण पत्र)</option>
                  <option value="community_certificate">Caste / Community Certificate (जाति प्रमाण पत्र)</option>
                  <option value="ration_card">Ration Card (राशन कार्ड)</option>
                  <option value="marksheet">Academic Marksheet (10th / 12th)</option>
                  <option value="bank_passbook">Bank Passbook (खाता विवरण)</option>
                </select>
              </div>

              {/* Drag/Drop Box */}
              <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:border-indigo-500 transition-colors bg-slate-50/50">
                <input
                  type="file"
                  id="doc-upload"
                  accept="image/*,.pdf,.txt"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="hidden"
                />
                <label htmlFor="doc-upload" className="cursor-pointer block space-y-2">
                  <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto">
                    <FileSearch className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-sm font-semibold text-indigo-600 hover:text-indigo-700">
                      Click to choose image or PDF
                    </span>
                    <span className="text-xs text-slate-500 block mt-1">PNG, JPG, PDF up to 10MB</span>
                  </div>
                </label>

                {selectedFile && (
                  <div className="mt-4 p-2 bg-indigo-50 rounded-lg text-xs font-semibold text-indigo-700 flex items-center justify-between">
                    <span className="truncate max-w-[200px]">{selectedFile.name}</span>
                    <span className="text-[11px] text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                )}
              </div>

              {error && (
                <div className="p-3 bg-rose-50 text-rose-700 text-xs rounded-xl border border-rose-200">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={uploading}
                className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md transition-all flex items-center justify-center space-x-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>{uploading ? 'Extracting Fields with OCR...' : 'Run OCR & Extract Fields'}</span>
              </button>
            </form>
          </div>

          {/* Instant 1-Click Samples Box */}
          <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6 space-y-3">
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-amber-500" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                Don't have a document handy? Try Instant Samples
              </h3>
            </div>
            <p className="text-xs text-slate-500">
              Click any sample below to immediately test the document parsing pipeline and regular expression extractors:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              {sampleDocuments.map((s) => (
                <button
                  key={s.id}
                  onClick={() => handleTestSample(s)}
                  disabled={uploading}
                  className="p-3 text-left bg-white rounded-xl border border-slate-200 hover:border-indigo-400 hover:shadow-xs transition-all text-xs font-semibold text-slate-700 flex items-center justify-between"
                >
                  <span className="truncate">{s.name}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* OCR Extracted Results (Right Column) */}
        <div className="lg:col-span-6 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm min-h-[400px] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <span>OCR Extraction Results</span>
                </h3>
                {extractedData && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                    Confidence: {Math.round((extractedData.confidence || 0.95) * 100)}%
                  </span>
                )}
              </div>

              {!extractedData && !uploading && (
                <div className="text-center py-20 text-slate-400 space-y-2">
                  <FileText className="w-12 h-12 text-slate-300 mx-auto" />
                  <p className="text-sm font-medium">No document uploaded yet</p>
                  <p className="text-xs text-slate-400 max-w-xs mx-auto">
                    Upload an Aadhaar, income certificate, or click one of the instant samples on the left.
                  </p>
                </div>
              )}

              {uploading && (
                <div className="text-center py-20 space-y-3">
                  <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="text-sm font-medium text-slate-600">Performing optical recognition & field parsing...</p>
                </div>
              )}

              {extractedData && !uploading && (
                <div className="space-y-4">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                    <span className="font-semibold text-slate-500 uppercase tracking-wider block text-[10px]">
                      Document Type
                    </span>
                    <span className="font-bold text-slate-800 text-sm capitalize">
                      {extractedData.document_type?.replace(/_/g, ' ')}
                    </span>
                  </div>

                  {/* Extracted Fields Table */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Extracted Attributes</h4>
                    <div className="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden divide-y divide-slate-200 text-xs">
                      {Object.entries(extractedData.extracted_fields || {}).map(([key, val]) => (
                        <div key={key} className="flex justify-between items-center px-4 py-2.5">
                          <span className="text-slate-600 font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Raw OCR Text Snippet */}
                  {extractedData.raw_text && (
                    <div className="space-y-1">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Raw OCR Output</h4>
                      <pre className="text-[11px] bg-slate-900 text-emerald-400 p-3 rounded-xl overflow-x-auto max-h-36 font-mono leading-relaxed">
                        {extractedData.raw_text}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bottom Sync Button */}
            {extractedData && (
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                {syncSuccess ? (
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 flex items-center space-x-1">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Synchronized to Your Profile!</span>
                  </span>
                ) : (
                  <button
                    onClick={handleSyncToProfile}
                    className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors flex items-center justify-center space-x-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Sync Extracted Data into My Profile</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
