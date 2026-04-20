import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Monitor, CheckCircle2, Loader2, AlertCircle, Download, FileSpreadsheet, FileText } from 'lucide-react';
import SplitText from '../components/SplitText';
import { getToken } from '../utils/tokenStorage';
import StyledButton from '../components/Template/StyledButton';

const MajorMoreOptionsPage = ({ showToast }) => {
  const { planId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('excel-export');

  const [planInfo, setPlanInfo] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(true);
  const [planError, setPlanError] = useState(null);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [downloadingJson, setDownloadingJson] = useState(false);

  useEffect(() => {
    if (!planId) return;
    const load = async () => {
      setLoadingPlan(true);
      setPlanError(null);
      try {
        const token = getToken();
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const res = await fetch(`/api/major-exam/plan/${planId}`, { headers });
        
        if (res.status === 404) {
          setPlanInfo({
            total_students: 'N/A',
            room_count: 'N/A',
            status: 'FINALIZED',
            created_at: new Date().toLocaleDateString()
          });
        } else if (!res.ok) {
          throw new Error('Could not load plan details');
        } else {
          const data = await res.json();
          setPlanInfo(data.plan || {
            total_students: 'N/A',
            room_count: 'N/A',
            status: 'FINALIZED'
          });
        }
      } catch (err) {
        setPlanError('Could not load plan details (non-critical)');
        setPlanInfo({ total_students: 'N/A', room_count: 'N/A', status: 'FINALIZED' });
      } finally {
        setLoadingPlan(false);
      }
    };
    load();
  }, [planId]);

  const handleExcelExport = async () => {
    setDownloadingExcel(true);
    try {
      const token = getToken();
      const headers = {
        'Authorization': token ? `Bearer ${token}` : ''
      };
      
      const response = await fetch(`/api/major-exam/download/excel/${planId}`, { headers });
      if (!response.ok) {
        let message = 'Failed to export to Excel';
        try {
          const data = await response.json();
          message = data.error || data.message || message;
        } catch {
          // Keep fallback message when response body is not JSON
        }
        throw new Error(message);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `MAJOR_EXAM_${planId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast('✅ Excel file exported successfully', 'success');
    } catch (err) {
      if (showToast) showToast('❌ Failed to export Excel: ' + err.message, 'error');
    } finally {
      setDownloadingExcel(false);
    }
  };

  const handleJsonExport = async () => {
    setDownloadingJson(true);
    try {
      const token = getToken();
      const headers = {
        'Authorization': token ? `Bearer ${token}` : ''
      };

      const response = await fetch(`/api/major-exam/download/json/${planId}`, { headers });
      if (!response.ok) {
        let message = 'Failed to export JSON';
        try {
          const data = await response.json();
          message = data.error || data.message || message;
        } catch {
          // Keep fallback message when response body is not JSON
        }
        throw new Error(message);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `MAJOR_EXAM_${planId}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast('✅ Processed plan JSON downloaded', 'success');
    } catch (err) {
      if (showToast) showToast('❌ Failed to download JSON: ' + err.message, 'error');
    } finally {
      setDownloadingJson(false);
    }
  };

  if (!planId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">No plan selected</p>
          <button
            onClick={() => navigate('/major-exam/create-plan')}
            className="text-orange-500 hover:text-orange-600 font-medium"
          >
            Back to Create Plan
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-gray-200 dark:border-gray-800">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Major Exam Tools</span>
            </div>
            <SplitText
              text="Plan Management"
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              splitType="chars"
              delay={30}
            />
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Download master plan & export student data
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/major-exam/create-plan')}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl text-sm font-bold transition-colors flex items-center gap-2"
            >
              <ArrowLeft size={16} />
              Back
            </button>
            <div className="text-right">
              <div className="text-xs text-gray-500 mb-1">Plan ID</div>
              <div className="text-lg font-black text-orange-600 dark:text-orange-400 font-mono">
                {planId}
              </div>
            </div>
          </div>
        </div>

        {/* Plan Info Stats */}
        {loadingPlan ? (
          <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-800">
            <Loader2 className="w-5 h-5 animate-spin text-orange-500" />
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Loading plan details…</p>
          </div>
        ) : planError ? (
          <div className="flex items-center gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl border-2 border-yellow-200 dark:border-yellow-800">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300 font-medium">{planError}</p>
          </div>
        ) : planInfo && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800 text-center">
              <Users className="w-5 h-5 text-purple-500 mx-auto mb-1" />
              <div className="text-2xl font-black text-purple-600 dark:text-purple-400">{planInfo.total_students}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 font-bold">Students</div>
            </div>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800 text-center">
              <Monitor className="w-5 h-5 text-blue-500 mx-auto mb-1" />
              <div className="text-2xl font-black text-blue-600 dark:text-blue-400">{planInfo.room_count}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 font-bold">Rooms</div>
            </div>
            <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border border-emerald-200 dark:border-emerald-800 text-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto mb-1" />
              <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">{planInfo.status}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 font-bold">Status</div>
            </div>
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800 text-center">
              <FileText className="w-5 h-5 text-amber-500 mx-auto mb-1" />
              <div className="text-2xl font-black text-amber-600 dark:text-amber-400">{planInfo.created_at || '—'}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 font-bold">Created</div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="space-y-6">

          {/* Tab Navigation */}
          <div className="flex gap-2 p-4 bg-gray-100 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
            <button
              onClick={() => setActiveTab('excel-export')}
              className={`flex-1 py-3 px-4 rounded-lg font-bold transition-all ${
                activeTab === 'excel-export'
                  ? 'bg-emerald-500 text-white shadow-lg'
                  : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              <FileSpreadsheet size={18} className="inline mr-2" />
              Excel Export
            </button>
          </div>

          {/* Content */}
          {activeTab === 'excel-export' && (
            <div className="glass-card p-8 border border-gray-200 dark:border-gray-800 rounded-2xl space-y-6">
              <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-800">
                <div className="p-3 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
                  <FileSpreadsheet className="text-emerald-600 dark:text-emerald-400" size={24} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Export to Excel</h2>
              </div>

              <p className="text-gray-600 dark:text-gray-400">
                Export all student data from this plan to an Excel spreadsheet. Includes names, enrollment numbers, allocations, and other relevant information.
              </p>

              <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
                <p className="text-sm text-emerald-700 dark:text-emerald-300">
                  💾 The exported file can be used for reports, analysis, and data processing in your office systems.
                </p>
              </div>

              <StyledButton
                onClick={handleExcelExport}
                disabled={downloadingExcel}
                className="w-full py-4 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700"
              >
                <Download size={18} className={downloadingExcel ? 'animate-spin' : ''} />
                {downloadingExcel ? 'Exporting...' : 'Download Excel File'}
              </StyledButton>

              <StyledButton
                onClick={handleJsonExport}
                disabled={downloadingJson}
                className="w-full py-4 bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800"
              >
                <Download size={18} className={downloadingJson ? 'animate-spin' : ''} />
                {downloadingJson ? 'Downloading JSON...' : 'Download Processed JSON'}
              </StyledButton>
            </div>
          )}

        </div>

      </div>

      <style jsx>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.65);
          backdrop-filter: blur(14px) saturate(140%);
          -webkit-backdrop-filter: blur(14px) saturate(140%);
        }
        :global(.dark) .glass-card {
          background: rgba(17, 24, 39, 0.55);
          backdrop-filter: blur(14px) saturate(130%);
        }
      `}</style>
    </div>
  );
};

export default MajorMoreOptionsPage;
