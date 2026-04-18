import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getToken } from '../utils/tokenStorage';
import { 
  Upload, Eye, Loader2, AlertCircle, 
  FileText, BarChart3, RefreshCw, FileJson, Target, Users,
  FileCheck, Zap, Clock, Check, X, BookMarked, ArrowRightLeft
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SplitText from '../components/SplitText';
import MajorAttendanceForm from '../components/MajorAttendanceForm';

const MajorExamCreatePlan = ({ showToast }) => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [viewingPlan, setViewingPlan] = useState(null);
  const [planDetails, setPlanDetails] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showMetadataForm, setShowMetadataForm] = useState(false);
  const [pendingDownloadPlanId, setPendingDownloadPlanId] = useState(null);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const initialFetchDone = useRef(false);
  const fileInputRef = useRef(null);

  const fetchRecentMajorPlans = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = getToken();
      const response = await fetch('/api/major-exam/recent', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to load plans');
      }

      setPlans(data.plans || []);
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Only fetch once on mount
    if (!initialFetchDone.current) {
      initialFetchDone.current = true;
      fetchRecentMajorPlans();
    }
  }, [fetchRecentMajorPlans]);

  // Handle drag events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  // Handle file drop
  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    // Validate file type
    const validTypes = ['application/vnd.ms-excel', 
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                       'text/csv'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid Excel or CSV file');
      if (showToast) showToast('Invalid file type. Use .xlsx or .csv', 'error');
      return;
    }

    setUploading(true);
    setError(null);
    
    try {
      const token = getToken();
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/major-exam/upload', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      // Show preview before finalizing
      setPreviewData({
        planId: data.plan_id,
        totalStudents: data.total_students || 0,
        allocatedCount: data.allocated_count || 0,
        roomCount: data.room_count || 0,
        students: data.students || []
      });
      setShowPreview(true);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
      if (showToast) showToast(err.message, 'error');
      setUploading(false);
    }
  };

  const confirmUpload = async () => {
    if (showToast) showToast(`Successfully created plan: ${previewData.planId}`, 'success');
    setShowPreview(false);
    setPreviewData(null);
    setUploading(false);
    await fetchRecentMajorPlans();
  };

  const cancelUpload = () => {
    setShowPreview(false);
    setPreviewData(null);
    setUploading(false);
    if (showToast) showToast('Upload cancelled', 'info');
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      await uploadFile(file);
      e.target.value = '';
    }
  };

  const handleViewPlan = async (plan) => {
    setPlanDetails(plan);
    setViewingPlan(plan.plan_id);
  };

  const handleDownload = async (planId, format) => {
    try {
      // For master-plan, show the metadata form first
      if (format === 'master-plan') {
        setPendingDownloadPlanId(planId);
        setShowMetadataForm(true);
        return;
      }

      const token = getToken();
      
      let endpoint = '';
      let filename = `MAJOR_EXAM_${planId}`;
      
      switch(format) {
        case 'pdf':
          endpoint = `/api/major-exam/download/pdf/${planId}`;
          filename += '_ATTENDANCE.pdf';
          break;
        case 'excel':
          endpoint = `/api/major-exam/download/excel/${planId}`;
          filename += '.xlsx';
          break;
        default:
          return;
      }

      const response = await fetch(endpoint, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast(`Downloaded ${format}`, 'success');
    } catch (err) {
      console.error('Download error:', err);
      if (showToast) showToast(err.message, 'error');
    }
  };

  const handleMetadataSubmit = async (formData) => {
    if (!pendingDownloadPlanId) return;

    try {
      setMetadataLoading(true);
      const token = getToken();

      // Save metadata to backend (C4: All 9 fields)
      const metadataResponse = await fetch(`/api/major-exam/metadata/${pendingDownloadPlanId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          examDate: formData.examDate,
          exam_name: formData.exam_name,
          department: formData.department,
          course_name: formData.course_name,
          course_code: formData.course_code,
          notes: formData.notes,
          invigilator1: formData.invigilator1,
          invigilator2: formData.invigilator2,
          invigilator3: formData.invigilator3
        })
      });

      if (!metadataResponse.ok) {
        throw new Error('Failed to save metadata');
      }

      // Close form
      setShowMetadataForm(false);

      // Now download the PDF with updated metadata
      const downloadResponse = await fetch(`/api/major-exam/download/master-plan/${pendingDownloadPlanId}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      if (!downloadResponse.ok) throw new Error('Download failed');

      const blob = await downloadResponse.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `MAJOR_EXAM_${pendingDownloadPlanId}_MASTER_PLAN.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast('Master plan downloaded successfully', 'success');
      
      setPendingDownloadPlanId(null);
    } catch (err) {
      console.error('Metadata/Download error:', err);
      if (showToast) showToast(err.message || 'Failed to process request', 'error');
    } finally {
      setMetadataLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-amber-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 pt-8 pb-20">
      <div className="max-w-7xl mx-auto px-4">
        
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }} 
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 dark:from-orange-400 dark:to-amber-400 bg-clip-text text-transparent">
                <SplitText text="Major Exam Management" />
              </h1>
            </div>
            <button
              onClick={() => navigate('/create-plan')}
              className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-bold transition-all duration-200 flex items-center gap-2 whitespace-nowrap shadow-lg"
              title="Switch to Minor Exams"
            >
              <BookMarked size={18} />
              <span className="hidden sm:inline">Minor Exams</span>
              <ArrowRightLeft size={16} />
            </button>
          </div>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl">
            Upload and manage student data for major examination allocations. Generate professional attendance sheets and seating plans.
          </p>
        </motion.div>

        {/* Upload Card - Professional Design */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative mb-12 p-12 rounded-2xl border-2 border-dashed transition-all duration-300 ${
            dragActive
              ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20 shadow-lg'
              : 'border-orange-300 dark:border-orange-700 bg-white/80 dark:bg-slate-800/50 hover:border-orange-400 hover:shadow-md'
          } backdrop-blur-sm`}
        >
          <label className="flex flex-col items-center justify-center cursor-pointer">
            <motion.div
              animate={{ scale: dragActive ? 1.1 : 1 }}
              className="mb-6"
            >
              <div className="p-4 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 rounded-full">
                <Upload className={`w-10 h-10 transition-colors ${
                  dragActive 
                    ? 'text-orange-600 dark:text-orange-400' 
                    : 'text-orange-500 dark:text-orange-300'
                }`} />
              </div>
            </motion.div>

            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              Upload Student Data
            </h3>
            <p className="text-center text-slate-600 dark:text-slate-300 mb-4">
              {dragActive 
                ? 'Drop your file here to upload' 
                : 'Drag and drop your Excel or CSV file, or click to browse'}
            </p>

            <div className="grid grid-cols-2 gap-4 mb-6 w-full max-w-md">
              <div className="flex items-start gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <FileCheck className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-semibold text-green-900 dark:text-green-300">Flexible Format</p>
                  <p className="text-xs text-green-700 dark:text-green-400">.xlsx, .xls, .csv supported</p>
                </div>
              </div>

              <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <Users className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-semibold text-blue-900 dark:text-blue-300">Smart Detection</p>
                  <p className="text-xs text-blue-700 dark:text-blue-400">Auto-detects column names</p>
                </div>
              </div>

              <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                <Zap className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-semibold text-amber-900 dark:text-amber-300">Instant Processing</p>
                  <p className="text-xs text-amber-700 dark:text-amber-400">Plan created immediately</p>
                </div>
              </div>

              <div className="flex items-start gap-2 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                <Clock className="w-5 h-5 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-semibold text-orange-900 dark:text-orange-300">Required Data</p>
                  <p className="text-xs text-orange-700 dark:text-orange-400">Name, Enrollment, Code, Password</p>
                </div>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileSelect}
              disabled={uploading}
              className="hidden"
            />

            <div className="w-full">
              <button 
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-3 px-6 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-lg disabled:opacity-50"
              >
                {uploading ? 'Processing...' : 'Click to Choose File or Drag & Drop'}
              </button>
            </div>
          </label>

          {uploading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 bg-white/80 dark:bg-slate-800/80 rounded-2xl flex items-center justify-center backdrop-blur-sm"
            >
              <div className="text-center">
                <Loader2 className="w-10 h-10 animate-spin text-orange-600 dark:text-orange-400 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Processing your file...
                </p>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-8 p-4 bg-red-50 dark:bg-red-900/30 border-l-4 border-red-500 rounded-lg flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
              <span className="text-red-700 dark:text-red-300">{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recent Plans Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              Recent Exam Plans
            </h2>
            <motion.button
              whileHover={{ rotate: 90 }}
              onClick={fetchRecentMajorPlans}
              disabled={loading}
              className="p-3 hover:bg-orange-100 dark:hover:bg-orange-900/30 rounded-lg transition-colors disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw className={`w-6 h-6 text-orange-600 dark:text-orange-400 ${loading ? 'animate-spin' : ''}`} />
            </motion.button>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <Loader2 className="w-12 h-12 animate-spin text-orange-600 dark:text-orange-400 mx-auto mb-4" />
              <p className="text-slate-600 dark:text-slate-300 font-medium">Loading your exam plans...</p>
            </div>
          ) : plans.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-16 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600"
            >
              <FileText className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-lg font-medium text-slate-600 dark:text-slate-300 mb-2">No exam plans yet</p>
              <p className="text-slate-500 dark:text-slate-400">Upload a file above to create your first major exam plan</p>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {plans.map((plan, idx) => (
                <motion.div
                  key={plan.plan_id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="group relative p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700 hover:border-orange-400 dark:hover:border-orange-500 hover:shadow-lg transition-all duration-300 overflow-hidden"
                >
                  {/* Gradient Background Effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-orange-500/0 via-amber-500/0 to-orange-500/0 group-hover:from-orange-500/5 group-hover:via-amber-500/5 group-hover:to-orange-500/5 transition-all duration-300 pointer-events-none" />

                  <div className="relative z-10">
                    {/* Plan Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3 flex-1">
                        <div className="p-3 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/40 dark:to-amber-900/40 rounded-lg">
                          <FileJson className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-900 dark:text-white truncate max-w-xs text-lg">
                            {plan.plan_id}
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Created on {new Date(plan.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-3 mb-6 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
                      <div className="text-center">
                        <Users className="w-5 h-5 text-orange-600 dark:text-orange-400 mx-auto mb-2" />
                        <p className="text-xs text-slate-600 dark:text-slate-400">Students</p>
                        <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                          {plan.total_students || 0}
                        </p>
                      </div>
                      <div className="text-center border-l border-r border-slate-200 dark:border-slate-700">
                        <FileCheck className="w-5 h-5 text-green-600 dark:text-green-400 mx-auto mb-2" />
                        <p className="text-xs text-slate-600 dark:text-slate-400">Allocated</p>
                        <p className="text-lg font-bold text-green-600 dark:text-green-400">
                          {plan.allocated_count || 0}
                        </p>
                      </div>
                      <div className="text-center">
                        <Target className="w-5 h-5 text-orange-600 dark:text-orange-400 mx-auto mb-2" />
                        <p className="text-xs text-slate-600 dark:text-slate-400">Rooms</p>
                        <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                          {plan.room_count || 0}
                        </p>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 mb-4">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleViewPlan(plan)}
                        className="flex-1 py-2 px-3 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-300 hover:bg-orange-100 dark:hover:bg-orange-900/50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">View Details</span>
                      </motion.button>
                    </div>

                    {/* Download Options */}
                    <div className="space-y-2 pt-4 border-t border-slate-200 dark:border-slate-700">
                      <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide">Download Options:</p>
                      <div className="grid grid-cols-3 gap-2">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleDownload(plan.plan_id, 'pdf')}
                          className="py-2 px-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-xs"
                          title="Attendance Sheet PDF"
                        >
                          <FileText className="w-4 h-4" />
                          <span>PDF</span>
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleDownload(plan.plan_id, 'excel')}
                          className="py-2 px-2 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40 rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-xs"
                          title="Excel Data Export"
                        >
                          <BarChart3 className="w-4 h-4" />
                          <span>Excel</span>
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleDownload(plan.plan_id, 'master-plan')}
                          className="py-2 px-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-xs"
                          title="Master Seating Plan"
                        >
                          <FileJson className="w-4 h-4" />
                          <span>Master</span>
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Preview & Confirmation Modal */}
      <AnimatePresence>
        {showPreview && previewData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-auto p-8 border-2 border-orange-200 dark:border-orange-800"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-3xl font-bold text-slate-900 dark:text-white">
                  Preview & Confirm Upload
                </h3>
                <button
                  onClick={cancelUpload}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                </button>
              </div>

              {previewData && (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border-2 border-orange-200 dark:border-orange-800">
                      <div className="flex items-center gap-2 mb-2">
                        <Users className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        <p className="text-sm text-orange-600 dark:text-orange-400 font-medium">Total Students</p>
                      </div>
                      <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">{previewData.totalStudents}</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800">
                      <div className="flex items-center gap-2 mb-2">
                        <FileCheck className="w-5 h-5 text-green-600 dark:text-green-400" />
                        <p className="text-sm text-green-600 dark:text-green-400 font-medium">Allocated</p>
                      </div>
                      <p className="text-3xl font-bold text-green-700 dark:text-green-300">{previewData.allocatedCount}</p>
                    </div>
                    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border-2 border-amber-200 dark:border-amber-800">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                        <p className="text-sm text-amber-600 dark:text-amber-400 font-medium">Rooms</p>
                      </div>
                      <p className="text-3xl font-bold text-amber-700 dark:text-amber-300">{previewData.roomCount}</p>
                    </div>
                  </div>

                  {/* First 10 Students Preview */}
                  {previewData.students && previewData.students.length > 0 && (
                    <div className="border-2 border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                      <div className="bg-orange-50 dark:bg-orange-900/20 px-4 py-3 border-b-2 border-orange-200 dark:border-orange-800">
                        <h4 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                          <Users className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                          First 10 Students Preview
                        </h4>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead className="bg-slate-100 dark:bg-slate-700">
                            <tr>
                              {Object.keys(previewData.students[0] || {}).map((key) => (
                                <th key={key} className="px-4 py-3 text-left text-sm font-semibold text-slate-900 dark:text-white">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {previewData.students.slice(0, 10).map((student, idx) => (
                              <tr key={idx} className="border-t border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700">
                                {Object.values(student).map((value, i) => (
                                  <td key={i} className="px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                                    {String(value).substring(0, 50)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {previewData.students.length > 10 && (
                        <div className="bg-slate-50 dark:bg-slate-900/50 px-4 py-3 text-center border-t border-slate-200 dark:border-slate-700">
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            Showing 10 of {previewData.students.length} students ({previewData.students.length - 10} more...)
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-6 border-t border-slate-200 dark:border-slate-700">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={cancelUpload}
                      className="flex-1 py-3 px-6 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                    >
                      <X className="w-5 h-5" />
                      Cancel
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={confirmUpload}
                      className="flex-1 py-3 px-6 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-lg flex items-center justify-center gap-2"
                    >
                      <Check className="w-5 h-5" />
                      Confirm & Save
                    </motion.button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Plan Details Modal */}
      <AnimatePresence>
        {viewingPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setViewingPlan(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-auto p-8 border-2 border-orange-200 dark:border-orange-800"
            >
              <h3 className="text-2xl font-bold mb-6 text-slate-900 dark:text-white">
                {planDetails?.plan_id}
              </h3>
              
              {planDetails && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border-2 border-orange-200 dark:border-orange-800">
                      <p className="text-sm text-orange-600 dark:text-orange-400 font-medium">Total Students</p>
                      <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">{planDetails.total_students || 0}</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800">
                      <p className="text-sm text-green-600 dark:text-green-400 font-medium">Allocated</p>
                      <p className="text-3xl font-bold text-green-700 dark:text-green-300">{planDetails.allocated_count || 0}</p>
                    </div>
                    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border-2 border-amber-200 dark:border-amber-800">
                      <p className="text-sm text-amber-600 dark:text-amber-400 font-medium">Rooms</p>
                      <p className="text-3xl font-bold text-amber-700 dark:text-amber-300">{planDetails.room_count || 0}</p>
                    </div>
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                      <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">Status</p>
                      <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">Active</p>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-200 dark:border-slate-700 flex gap-3">
                    <button
                      onClick={() => navigate(`/major-exam/more-options/${viewingPlan}`)}
                      className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold rounded-lg transition-all duration-200"
                      title="More Options"
                    >
                      More Options
                    </button>
                    <button
                      onClick={() => setViewingPlan(null)}
                      className="flex-1 py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-semibold rounded-lg transition-all duration-200"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Metadata Form Modal */}
      <MajorAttendanceForm
        isOpen={showMetadataForm}
        onClose={() => {
          setShowMetadataForm(false);
          setPendingDownloadPlanId(null);
        }}
        onSubmit={handleMetadataSubmit}
        loading={metadataLoading}
      />
    </div>
  );
};

export default MajorExamCreatePlan;
