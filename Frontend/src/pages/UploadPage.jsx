import React, { useState } from 'react';
import { Upload, Loader2, AlertCircle, CheckCircle, FileSpreadsheet, Database, Sparkles, ArrowRight } from 'lucide-react';

const UploadPage = ({ showToast }) => {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState('2');
  const [batchName, setBatchName] = useState('');
  const [nameColumn, setNameColumn] = useState('');
  const [enrollmentColumn, setEnrollmentColumn] = useState('');
  
  const [uploadResult, setUploadResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [commitLoading, setCommitLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setUploadResult(null);
    
    if (selectedFile) {
      if (showToast) showToast(`📁 File selected: ${selectedFile.name}`, "success");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      if (showToast) showToast('Please select a file first', "error");
      return;
    }

    if (!batchName.trim()) {
      if (showToast) showToast('Please enter a batch name', "error");
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode);
      formData.append('batch_name', batchName.trim());
      
      if (nameColumn.trim()) formData.append('nameColumn', nameColumn.trim());
      if (enrollmentColumn.trim()) formData.append('enrollmentColumn', enrollmentColumn.trim());

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Upload failed');

      setUploadResult(data);
      if (showToast) showToast(`✅ Preview ready! ${data.rows_extracted} students found`, "success");
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
      if (showToast) showToast(`Upload failed: ${err.message}`, "error");
    } finally {
      setUploading(false);
    }
  };

  const handleCommit = async () => {
    if (!uploadResult) return;

    setCommitLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/commit-upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ batch_id: uploadResult.batch_id })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Commit failed');

      if (showToast) showToast(`✅ Committed! ${data.inserted} students added to database`, "success");
      
      setFile(null);
      setUploadResult(null);
      setBatchName('');
      setError(null);
      
    } catch (err) {
      console.error('Commit error:', err);
      if (showToast) showToast(`Commit failed: ${err.message}`, "error");
    } finally {
      setCommitLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-t-0 border-r-0 border-l-0 border-[#c0c0c0] dark:border-[#8a8a8a] bg-transparent shadow-none dark:shadow-none">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Data Import</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent">
              Upload Student Data
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Import CSV or XLSX files to add students to the system
            </p>
          </div>
        </div>

        {/* Main Card */}
        <div className="glass-card rounded-3xl p-8 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_32px_rgba(192,192,192,0.25)] dark:shadow-[0_0_32px_rgba(138,138,138,0.28)]">
          
          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl flex gap-3 animate-fadeIn">
              <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0" size={20} />
              <p className="text-red-700 dark:text-red-300 font-semibold">{error}</p>
            </div>
          )}

          {/* Upload Form */}
          <div className="space-y-6">
            {/* File Input */}
            <div className="p-6 border-2 border-dashed border-orange-300 dark:border-orange-700 rounded-xl bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/10 dark:to-amber-900/10 hover:border-orange-500 dark:hover:border-orange-500 transition-all duration-300 group">
              <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                <Upload size={16} className="text-orange-500" />
                Select File
              </label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-700 dark:text-gray-300
                  file:mr-4 file:py-3 file:px-6
                  file:rounded-lg file:border-0
                  file:text-sm file:font-bold
                  file:bg-gradient-to-r file:from-orange-500 file:to-amber-500 file:text-white
                  hover:file:from-orange-600 hover:file:to-amber-600
                  file:shadow-md hover:file:shadow-lg
                  cursor-pointer transition-all file:transition-all"
              />
              <p className="mt-3 text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                <FileSpreadsheet size={14} className="text-orange-500" /> 
                Supported formats: CSV, XLSX, XLS (Max 50MB)
              </p>
            </div>

            {/* Mode Selection */}
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                <Sparkles size={16} className="text-orange-500" />
                Extraction Mode
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => setMode('1')}
                  className={`p-6 rounded-xl border-2 transition-all duration-200 text-left relative overflow-hidden group ${
                    mode === '1'
                      ? 'border-orange-500 dark:border-orange-400 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 bg-white dark:bg-gray-800'
                  }`}
                >
                  <div className="font-black text-xl text-gray-900 dark:text-white">Mode 1</div>
                  <div className="text-sm mt-2 text-gray-600 dark:text-gray-400">Enrollment Only</div>
                  {mode === '1' && (
                    <div className="absolute top-3 right-3">
                      <div className="relative w-3 h-3">
                        <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                        <div className="relative w-3 h-3 bg-orange-500 rounded-full"></div>
                      </div>
                    </div>
                  )}
                </button>
                <button
                  onClick={() => setMode('2')}
                  className={`p-6 rounded-xl border-2 transition-all duration-200 text-left relative overflow-hidden group ${
                    mode === '2'
                      ? 'border-orange-500 dark:border-orange-400 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 bg-white dark:bg-gray-800'
                  }`}
                >
                  <div className="font-black text-xl text-gray-900 dark:text-white">Mode 2</div>
                  <div className="text-sm mt-2 text-gray-600 dark:text-gray-400">Name + Enrollment</div>
                  {mode === '2' && (
                    <div className="absolute top-3 right-3">
                      <div className="relative w-3 h-3">
                        <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                        <div className="relative w-3 h-3 bg-orange-500 rounded-full"></div>
                      </div>
                    </div>
                  )}
                </button>
              </div>
            </div>

            {/* Batch Name */}
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                <Database size={16} className="text-orange-500" />
                Batch Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={batchName}
                onChange={(e) => setBatchName(e.target.value)}
                placeholder="e.g., CSE-2024, ECE-Batch-A"
                className="w-full px-4 py-3.5 border-2 border-gray-200 dark:border-gray-700 rounded-xl 
                  bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                  focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 dark:focus:border-orange-400
                  placeholder-gray-400 dark:placeholder-gray-600 transition-all duration-300 font-semibold"
              />
            </div>

            {/* Custom Column Names */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                  Name Column (Optional)
                </label>
                <input
                  type="text"
                  value={nameColumn}
                  onChange={(e) => setNameColumn(e.target.value)}
                  placeholder="Auto-detect if empty"
                  className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl
                    bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                    focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 dark:focus:border-orange-400
                    placeholder-gray-400 dark:placeholder-gray-600 transition-all duration-300"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                  Enrollment Column (Optional)
                </label>
                <input
                  type="text"
                  value={enrollmentColumn}
                  onChange={(e) => setEnrollmentColumn(e.target.value)}
                  placeholder="Auto-detect if empty"
                  className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl
                    bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                    focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 dark:focus:border-orange-400
                    placeholder-gray-400 dark:placeholder-gray-600 transition-all duration-300"
                />
              </div>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || !batchName.trim() || uploading}
              className="group w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 
                disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-700 disabled:cursor-not-allowed 
                text-white font-bold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-[1.02]
                flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Uploading & Processing...
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Upload & Preview
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>

          {/* Preview Section */}
          {uploadResult && (
            <div className="mt-8 glass-card rounded-2xl border-2 border-[#c0c0c0] dark:border-[#8a8a8a] overflow-hidden shadow-[0_0_28px_rgba(192,192,192,0.24)] dark:shadow-[0_0_28px_rgba(138,138,138,0.26)] animate-fadeInUp">
              <div className="bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/30 dark:to-green-900/30 p-6 border-b-2 border-emerald-200 dark:border-emerald-800">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-lg bg-emerald-500">
                    <CheckCircle className="text-white" size={24} />
                  </div>
                  <h2 className="text-2xl font-black text-emerald-900 dark:text-emerald-100">Upload Preview</h2>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white/90 dark:bg-gray-800/90 p-4 rounded-xl shadow-md border border-emerald-200 dark:border-emerald-800">
                    <div className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Students Found</div>
                    <div className="text-3xl font-black text-orange-600 dark:text-orange-400">{uploadResult.rows_extracted}</div>
                  </div>
                  <div className="bg-white/90 dark:bg-gray-800/90 p-4 rounded-xl shadow-md border border-emerald-200 dark:border-emerald-800">
                    <div className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Mode</div>
                    <div className="text-2xl font-black text-gray-800 dark:text-white">Mode {uploadResult.mode}</div>
                  </div>
                  <div className="bg-white/90 dark:bg-gray-800/90 p-4 rounded-xl shadow-md col-span-2 border border-emerald-200 dark:border-emerald-800">
                    <div className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Batch Info</div>
                    <div className="text-lg font-black text-gray-800 dark:text-white truncate flex items-center gap-2" title={uploadResult.batch_name}>
                      {uploadResult.batch_name}
                      <span className="text-xs font-mono opacity-60">#{uploadResult.batch_id.slice(0, 6)}</span>
                    </div>
                  </div>
                </div>

                {/* Warnings */}
                {uploadResult.warnings && uploadResult.warnings.length > 0 && (
                  <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/30 border-2 border-yellow-200 dark:border-yellow-800 rounded-xl flex gap-3">
                    <AlertCircle className="text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" size={20} />
                    <div>
                      <p className="font-bold text-yellow-800 dark:text-yellow-200 text-sm mb-2">Warnings ({uploadResult.warnings.length})</p>
                      <ul className="text-xs text-yellow-700 dark:text-yellow-300 space-y-1">
                        {uploadResult.warnings.slice(0, 3).map((w, i) => (
                          <li key={i} className="flex items-start gap-1">
                            <span className="text-yellow-500">•</span>
                            <span>{w}</span>
                          </li>
                        ))}
                        {uploadResult.warnings.length > 3 && <li className="text-yellow-600 dark:text-yellow-400 font-semibold">...and {uploadResult.warnings.length - 3} more</li>}
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Sample Data Table */}
              {uploadResult.sample && uploadResult.sample.length > 0 && (
                <div className="p-6">
                  <h4 className="font-black text-gray-800 dark:text-gray-200 mb-4 text-sm uppercase tracking-wider flex items-center gap-2">
                    <Database size={16} className="text-orange-500" />
                    Sample Data Preview
                  </h4>
                  <div className="overflow-x-auto border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]">
                    <table className="w-full text-sm">
                      <thead className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                        <tr>
                          <th className="px-4 py-3 text-left font-bold uppercase tracking-wide">Enrollment</th>
                          {uploadResult.mode === '2' && <th className="px-4 py-3 text-left font-bold uppercase tracking-wide">Name</th>}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {uploadResult.sample.slice(0, 5).map((row, i) => (
                          <tr key={i} className="hover:bg-orange-50 dark:hover:bg-orange-900/10 transition-colors">
                            <td className="px-4 py-3 font-mono font-semibold text-gray-600 dark:text-gray-400">
                              {typeof row === 'string' ? row : row.enrollmentNo || 'N/A'}
                            </td>
                            {uploadResult.mode === '2' && (
                              <td className="px-4 py-3 text-gray-800 dark:text-gray-200 font-medium">
                                {typeof row === 'object' && row.name ? row.name : '-'}
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3 justify-end mt-6">
                    <button
                      onClick={() => {
                        setUploadResult(null);
                        setFile(null);
                      }}
                      className="px-6 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl 
                        text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 
                        font-bold transition-all focus:outline-none focus:ring-2 focus:ring-gray-300"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCommit}
                      disabled={commitLoading}
                      className="group px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 
                        text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all 
                        disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 hover:scale-105"
                    >
                      {commitLoading ? (
                        <>
                          <Loader2 size={18} className="animate-spin" />
                          Committing...
                        </>
                      ) : (
                        <>
                          <CheckCircle size={18} />
                          Confirm & Save to Database
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-fadeInUp {
          animation: fadeInUp 0.5s ease-out;
        }
      `}</style>
    </div>
  );
};

export default UploadPage;