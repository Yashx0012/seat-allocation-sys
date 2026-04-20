import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getToken } from '../utils/tokenStorage';
import { useAuth } from '../contexts/AuthContext';
import { 
  Upload, Eye, Loader2, AlertCircle, 
  RefreshCw, Target, Users,
  Clock, X, ArrowLeftRight,
  Download, Building2, ChevronDown, ChevronRight,
  FileEdit, ArrowRight, Save
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SplitText from '../components/SplitText';
import MajorRoomConfigurator from '../components/MajorRoomConfigurator';
import MajorMasterPlanMetadataForm from '../components/MajorMasterPlanMetadataForm';

const emptyAttendanceMetadata = {
  exam_name: '',
  department: '',
  course_name: '',
  course_code: '',
  examDate: '',
  notes: '',
  invigilator1: '',
  invigilator2: '',
  invigilator3: ''
};

const mapMetadataToFormData = (metadata = {}) => ({
  exam_name: metadata.exam_name || '',
  department: metadata.department || '',
  course_name: metadata.course_name || '',
  course_code: metadata.course_code || '',
  examDate: metadata.exam_date || metadata.examDate || '',
  notes: metadata.notes || '',
  invigilator1: metadata.invigilator_1 || metadata.invigilator1 || '',
  invigilator2: metadata.invigilator_2 || metadata.invigilator2 || '',
  invigilator3: metadata.invigilator_3 || metadata.invigilator3 || ''
});

const MajorExamCreatePlan = ({ showToast }) => {
  const navigate = useNavigate();
  const { setExamType } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const initialFetchDone = useRef(false);
  const fileInputRef = useRef(null);

  // Multi-step upload flow
  const [uploadResult, setUploadResult] = useState(null); // { planId, branches, preview, ... }
  const [showBranchPreview, setShowBranchPreview] = useState(false);
  const [previewBranch, setPreviewBranch] = useState(null); // which branch to preview in modal
  const [showRoomConfig, setShowRoomConfig] = useState(false);
  const [roomConfigLoading, setRoomConfigLoading] = useState(false);

  // Plan viewer
  const [viewingPlan, setViewingPlan] = useState(null);
  const [planRooms, setPlanRooms] = useState([]);
  const [expandedRoom, setExpandedRoom] = useState(null);
  const [attendanceMetadata, setAttendanceMetadata] = useState(emptyAttendanceMetadata);
  const [attendanceMetaSaving, setAttendanceMetaSaving] = useState(false);

  // Master metadata / download
  const [showMasterMetadataForm, setShowMasterMetadataForm] = useState(false);
  const [masterDownloadPlanId, setMasterDownloadPlanId] = useState(null);
  const [masterMetadataInitialData, setMasterMetadataInitialData] = useState(emptyAttendanceMetadata);
  const [masterMetadataLoading, setMasterMetadataLoading] = useState(false);

  // ===== DATA FETCHING =====
  const fetchRecentPlans = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = getToken();
      const res = await fetch('/api/major-exam/recent', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to load');
      setPlans(data.plans || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!initialFetchDone.current) {
      initialFetchDone.current = true;
      fetchRecentPlans();
    }
  }, [fetchRecentPlans]);

  useEffect(() => {
    setExamType('major');
  }, [setExamType]);

  // ===== FILE UPLOAD =====
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) await uploadFile(file);
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      await uploadFile(file);
      e.target.value = '';
    }
  };

  const uploadFile = async (file) => {
    const validTypes = [
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv'
    ];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
      setError('Please upload a valid Excel (.xlsx, .xls) or CSV file');
      if (showToast) showToast('Invalid file type', 'error');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = getToken();
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/api/major-exam/upload', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Upload failed');

      // Show branch preview step
      setUploadResult({
        planId: data.plan_id,
        totalStudents: data.total_students,
        branchNames: data.branch_names || [],
        branchCounts: data.branch_counts || {},
        preview: data.preview || {}
      });
      setShowBranchPreview(true);
      if (showToast) showToast(`Parsed ${data.total_students} students across ${data.branch_names?.length || 0} branch(es)`, 'success');
    } catch (err) {
      setError(err.message);
      if (showToast) showToast(err.message, 'error');
    } finally {
      setUploading(false);
    }
  };

  // ===== ROOM CONFIGURATION =====
  const handleRoomConfigSubmit = async (roomsConfig) => {
    if (!uploadResult?.planId) return;
    setRoomConfigLoading(true);
    
    try {
      const token = getToken();
      const res = await fetch(`/api/major-exam/configure-rooms/${uploadResult.planId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ rooms: roomsConfig })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Room configuration failed');

      setShowRoomConfig(false);
      setShowBranchPreview(false);
      setUploadResult(null);
      if (showToast) showToast(`Plan finalized! ${data.total_allocated} students across ${data.rooms?.length} rooms`, 'success');
      await fetchRecentPlans();
    } catch (err) {
      if (showToast) showToast(err.message, 'error');
    } finally {
      setRoomConfigLoading(false);
    }
  };

  const cancelUpload = () => {
    setShowBranchPreview(false);
    setUploadResult(null);
    if (showToast) showToast('Upload cancelled', 'info');
  };

  // ===== PLAN VIEWER =====
  const handleViewPlan = async (plan) => {
    setViewingPlan(plan);
    setExpandedRoom(null);
    setAttendanceMetadata(emptyAttendanceMetadata);
    setMasterMetadataInitialData(emptyAttendanceMetadata);
    
    try {
      const token = getToken();
      const res = await fetch(`/api/major-exam/rooms/${plan.plan_id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const data = await res.json();
      if (data.success) {
        setPlanRooms(data.rooms || []);
        const attendanceForm = mapMetadataToFormData(data.attendance_metadata || {});
        const masterForm = mapMetadataToFormData({
          ...(data.attendance_metadata || {}),
          ...(data.master_metadata || {})
        });
        setAttendanceMetadata(attendanceForm);
        setMasterMetadataInitialData(masterForm);
      }
    } catch (err) {
      console.error('Error loading rooms:', err);
    }
  };

  // ===== DOWNLOADS =====
  const handleDownload = async (planId, format, roomName = null, branch = null) => {
    if (format === 'master-plan') {
      setMasterDownloadPlanId(planId);
      setShowMasterMetadataForm(true);
      return;
    }

    try {
      const token = getToken();
      let endpoint = '';
      let filename = `MAJOR_EXAM_${planId}`;

      if (format === 'pdf') {
        endpoint = `/api/major-exam/download/pdf/${planId}`;
        if (roomName) endpoint += `?room=${encodeURIComponent(roomName)}`;
        if (roomName && branch) endpoint += `&branch=${encodeURIComponent(branch)}`;
        filename += roomName ? `_${roomName.replace(/\s/g, '_')}` : '';
        filename += branch ? `_${branch}` : '';
        filename += '_ATTENDANCE.pdf';
      } else if (format === 'excel') {
        endpoint = `/api/major-exam/download/excel/${planId}`;
        filename += '.xlsx';
      } else return;

      const res = await fetch(endpoint, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) {
        let message = 'Download failed';
        try {
          const data = await res.json();
          message = data.error || data.message || message;
        } catch {
          // Ignore parse errors and use fallback message
        }
        throw new Error(message);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
      if (showToast) showToast(`Downloaded ${format}`, 'success');
    } catch (err) {
      if (showToast) showToast(err.message, 'error');
    }
  };

  const handleAttendanceMetadataChange = (event) => {
    const { name, value } = event.target;
    setAttendanceMetadata((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const validateAttendanceMetadata = () => {
    return (
      attendanceMetadata.exam_name.trim() &&
      attendanceMetadata.department.trim() &&
      attendanceMetadata.course_name.trim() &&
      attendanceMetadata.course_code.trim() &&
      attendanceMetadata.examDate
    );
  };

  const handleSaveAttendanceMetadata = async () => {
    if (!viewingPlan?.plan_id) return;
    if (!validateAttendanceMetadata()) {
      if (showToast) showToast('Fill required attendance metadata fields before saving', 'error');
      return;
    }

    try {
      setAttendanceMetaSaving(true);
      const token = getToken();

      const res = await fetch(`/api/major-exam/metadata/${viewingPlan.plan_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(attendanceMetadata)
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to save attendance metadata');
      }

      setMasterMetadataInitialData((prev) => ({
        ...prev,
        ...attendanceMetadata
      }));
      if (showToast) showToast('Attendance metadata saved', 'success');
    } catch (err) {
      if (showToast) showToast(err.message, 'error');
    } finally {
      setAttendanceMetaSaving(false);
    }
  };

  const handleMasterMetadataSubmit = async (formData) => {
    if (!masterDownloadPlanId) return;
    try {
      setMasterMetadataLoading(true);
      const token = getToken();

      const saveRes = await fetch(`/api/major-exam/master-metadata/${masterDownloadPlanId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(formData)
      });
      const saveData = await saveRes.json();
      if (!saveRes.ok || !saveData.success) {
        throw new Error(saveData.error || 'Failed to save master metadata');
      }

      setShowMasterMetadataForm(false);
      setMasterMetadataInitialData((prev) => ({
        ...prev,
        ...formData
      }));

      const downloadRes = await fetch(`/api/major-exam/download/master-plan/${masterDownloadPlanId}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!downloadRes.ok) {
        let message = 'Master plan download failed';
        try {
          const data = await downloadRes.json();
          message = data.error || data.message || message;
        } catch {
          // Ignore parse errors and use fallback message
        }
        throw new Error(message);
      }

      const blob = await downloadRes.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `MAJOR_EXAM_${masterDownloadPlanId}_MASTER_PLAN.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
      if (showToast) showToast('Master plan downloaded', 'success');
      setMasterDownloadPlanId(null);
    } catch (err) {
      if (showToast) showToast(err.message, 'error');
    } finally {
      setMasterMetadataLoading(false);
    }
  };

  // ===== HELPERS =====
  const formatDate = (d) => {
    if (!d) return '';
    try {
      return new Date(d).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return ''; }
  };

  const actions = [
    {
      title: 'Template Editor',
      description: 'Configure PDF headers & signatures',
      icon: FileEdit,
      bgColor: 'bg-orange-600',
      hoverBorder: 'hover:border-orange-500',
      onClick: () => navigate('/major-exam/template-editor')
    }
  ];

  // ===== RENDER =====
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-gray-200 dark:border-gray-800">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Major Exam Mode</span>
            </div>
            <SplitText
              text="Major Exam Management"
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              splitType="chars"
              delay={30}
            />
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Upload student data, configure rooms, and generate attendance sheets
            </p>
          </div>

          <div className="flex gap-4 items-center">
            <div className="text-right">
              <div className="text-xs text-gray-500 mb-1">Plans</div>
              <div className="text-3xl font-black text-orange-600 dark:text-orange-400">{plans.length}</div>
            </div>
            <button
              onClick={() => navigate('/create-plan')}
              className="ml-4 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-bold transition-all duration-200 flex items-center gap-2 whitespace-nowrap shadow-lg"
              title="Choose Exam Type"
            >
              <span className="hidden sm:inline">Choose Type</span>
              <ArrowLeftRight size={16} />
            </button>
          </div>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 gap-6">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              className={`relative overflow-hidden p-8 border-2 border-gray-200 dark:border-gray-800 ${action.hoverBorder} transition-all duration-300 group rounded-2xl bg-white/90 dark:bg-[#0a0a0a] text-left`}
              style={{ opacity: 0, animation: `fadeInUp 0.5s ease-out ${index * 0.1}s forwards` }}
            >
              <div className={`absolute inset-0 ${action.bgColor} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              <div className="absolute top-0 right-0 p-4 opacity-5 transform rotate-12 group-hover:scale-110 transition-transform duration-500">
                <action.icon className="w-24 h-24 text-gray-900 dark:text-gray-100" />
              </div>
              <div className="relative z-10 flex flex-col items-start gap-4">
                <div className={`${action.bgColor} p-4 rounded-xl shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
                  <action.icon className="text-white" size={28} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">{action.title}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-500">{action.description}</p>
                </div>
                <ArrowRight className="text-gray-500 dark:text-gray-600 group-hover:text-orange-500 group-hover:translate-x-1 transition-all duration-300" size={18} />
              </div>
            </button>
          ))}
        </div>

        {/* Upload Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative p-12 rounded-2xl border-2 border-dashed transition-all duration-300 ${
            dragActive
              ? 'border-orange-500 bg-orange-50/80 dark:bg-orange-900/10 shadow-lg dark:shadow-orange-900/20'
              : 'border-gray-300 dark:border-gray-700 bg-white/90 dark:bg-[#0a0a0a] hover:border-orange-600 hover:shadow-md'
          }`}
        >
          <label className="flex flex-col items-center justify-center cursor-pointer">
            <motion.div animate={{ scale: dragActive ? 1.1 : 1 }} className="mb-6">
              <div className="p-4 bg-orange-900/20 rounded-full">
                {uploading ? (
                  <Loader2 className="w-10 h-10 text-orange-400 animate-spin" />
                ) : (
                  <Upload className={`w-10 h-10 ${dragActive ? 'text-orange-400' : 'text-orange-500'}`} />
                )}
              </div>
            </motion.div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Upload Student Data</h3>
            <p className="text-center text-gray-600 dark:text-gray-400 mb-4">
              {dragActive ? 'Drop your file here' : 'Drag and drop your Excel file, or click to browse'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-600 mb-4">Each sheet in the Excel = one branch. Sheet name = branch name</p>
            <div className="flex gap-3">
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-xs text-gray-600 dark:text-gray-400">.xlsx</span>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-xs text-gray-600 dark:text-gray-400">.xls</span>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>
        </motion.div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-xl flex items-center gap-3 text-red-700 dark:text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
            <button onClick={() => setError(null)} className="ml-auto"><X size={16} /></button>
          </div>
        )}

        {/* Recent Plans */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Clock className="w-5 h-5 text-orange-400" />
              Recent Plans
            </h2>
            <button onClick={fetchRecentPlans} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 text-orange-400 animate-spin" />
            </div>
          ) : plans.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-600">
              <Target className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No plans yet. Upload an Excel file to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {plans.map((plan, idx) => (
                <motion.div
                  key={plan.plan_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-5 bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded-xl hover:border-orange-500/60 dark:hover:border-orange-700/50 transition-all duration-200 group cursor-pointer"
                  onClick={() => handleViewPlan(plan)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-sm font-mono text-orange-400 font-bold">{plan.plan_id}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-600 mt-0.5">{formatDate(plan.created_at)}</p>
                    </div>
                    <span className={`px-2 py-1 rounded-lg text-xs font-bold ${
                      plan.status === 'FINALIZED'
                        ? 'bg-green-100 text-green-700 border border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800/50'
                        : 'bg-yellow-100 text-yellow-700 border border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800/50'
                    }`}>
                      {plan.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-3">
                    <div className="text-center p-2 bg-gray-100 dark:bg-gray-900/50 rounded-lg">
                      <p className="text-lg font-bold text-orange-300">{plan.total_students || 0}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-600">Students</p>
                    </div>
                    <div className="text-center p-2 bg-gray-100 dark:bg-gray-900/50 rounded-lg">
                      <p className="text-lg font-bold text-green-300">{plan.allocated_count || 0}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-600">Allocated</p>
                    </div>
                    <div className="text-center p-2 bg-gray-100 dark:bg-gray-900/50 rounded-lg">
                      <p className="text-lg font-bold text-amber-300">{plan.room_count || 0}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-600">Rooms</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleViewPlan(plan); }}
                      className="w-full py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-1"
                    >
                      <Eye size={12} /> View Plan
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ===== BRANCH PREVIEW MODAL ===== */}
      <AnimatePresence>
        {showBranchPreview && uploadResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/45 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={cancelUpload}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-auto"
            >
              <div className="p-6 border-b border-gray-200 dark:border-gray-800">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Data Preview</h2>
                <p className="text-gray-600 dark:text-gray-500 text-sm">
                  Plan ID: <span className="text-orange-400 font-mono">{uploadResult.planId}</span>
                  &nbsp;•&nbsp; {uploadResult.totalStudents} students across {uploadResult.branchNames.length} branch(es)
                </p>
              </div>

              <div className="p-6 space-y-4">
                {/* Branch Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {uploadResult.branchNames.map(branch => (
                    <div key={branch} className="p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-xl hover:border-orange-500/60 dark:hover:border-orange-700/50 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-bold text-orange-400">{branch}</h3>
                        <button
                          onClick={() => setPreviewBranch(branch)}
                          className="p-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
                          title="Preview first 10 students"
                        >
                          <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </button>
                      </div>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white">{uploadResult.branchCounts[branch]}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-600">students</p>
                    </div>
                  ))}
                </div>

                {/* Branch preview table */}
                {previewBranch && uploadResult.preview[previewBranch] && (
                  <div className="border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden">
                    <div className="bg-orange-100 dark:bg-orange-900/20 px-4 py-3 border-b border-orange-300 dark:border-orange-800/50 flex items-center justify-between">
                      <h4 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <Users className="w-4 h-4 text-orange-400" />
                        {previewBranch} — First 10 Students
                      </h4>
                      <button onClick={() => setPreviewBranch(null)} className="text-gray-500 hover:text-gray-800 dark:hover:text-white">
                        <X size={16} />
                      </button>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-100 dark:bg-gray-900">
                          <tr>
                            {Object.keys(uploadResult.preview[previewBranch][0] || {}).map(key => (
                              <th key={key} className="px-4 py-3 text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider">{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {uploadResult.preview[previewBranch].map((student, idx) => (
                            <tr key={idx} className="border-t border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900/50">
                              {Object.values(student).map((val, i) => (
                                <td key={i} className="px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300">{String(val)}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {uploadResult.branchCounts[previewBranch] > 10 && (
                      <div className="px-4 py-2 bg-gray-100 dark:bg-gray-900/50 border-t border-gray-200 dark:border-gray-800 text-center">
                        <p className="text-xs text-gray-500 dark:text-gray-600">
                          Showing 10 of {uploadResult.branchCounts[previewBranch]} students
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                  <button
                    onClick={cancelUpload}
                    className="flex-1 py-3 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
                  >
                    <X size={18} /> Cancel
                  </button>
                  <button
                    onClick={() => setShowRoomConfig(true)}
                    className="flex-1 py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2"
                  >
                    <Building2 size={18} /> Configure Rooms
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ===== PLAN VIEWER MODAL ===== */}
      <AnimatePresence>
        {viewingPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/45 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setViewingPlan(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl max-w-6xl w-full max-h-[85vh] overflow-auto"
            >
              <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">{viewingPlan.plan_id}</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-500">{formatDate(viewingPlan.created_at)}</p>
                </div>
                <button onClick={() => setViewingPlan(null)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"><X className="w-5 h-5 text-gray-500 dark:text-gray-400" /></button>
              </div>

              <div className="p-6 space-y-4">
                {/* Stats row */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl text-center">
                    <p className="text-2xl font-bold text-orange-400">{viewingPlan.total_students || 0}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-600">Students</p>
                  </div>
                  <div className="p-3 bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl text-center">
                    <p className="text-2xl font-bold text-green-400">{viewingPlan.allocated_count || 0}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-600">Allocated</p>
                  </div>
                  <div className="p-3 bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl text-center">
                    <p className="text-2xl font-bold text-amber-400">{viewingPlan.room_count || 0}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-600">Rooms</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className="lg:col-span-2 space-y-2">
                    <h3 className="text-sm font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Room Allocations</h3>
                    {planRooms.length === 0 && (
                      <div className="p-4 bg-gray-100 dark:bg-gray-900/60 border border-gray-200 dark:border-gray-800 rounded-xl text-sm text-gray-600 dark:text-gray-500">
                        No rooms available for this plan.
                      </div>
                    )}
                    {planRooms.map((room, idx) => (
                      <div key={idx} className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden">
                        <button
                          onClick={() => setExpandedRoom(expandedRoom === idx ? null : idx)}
                          className="w-full p-4 flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-900/80 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <Building2 className="w-5 h-5 text-orange-400" />
                            <div className="text-left">
                              <p className="font-bold text-gray-900 dark:text-white">{room.room_name}</p>
                              <p className="text-xs text-gray-600 dark:text-gray-500">{room.total_students} students • {Object.keys(room.branches).join(', ')}</p>
                            </div>
                          </div>
                          {expandedRoom === idx ? <ChevronDown className="w-4 h-4 text-gray-500 dark:text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500 dark:text-gray-500" />}
                        </button>

                        {expandedRoom === idx && (
                          <div className="px-4 pb-4 space-y-2 border-t border-gray-200 dark:border-gray-800 pt-3">
                            <button
                              onClick={() => handleDownload(viewingPlan.plan_id, 'pdf', room.room_name)}
                              className="w-full py-2.5 bg-orange-100 dark:bg-orange-900/20 hover:bg-orange-200 dark:hover:bg-orange-900/40 border border-orange-300 dark:border-orange-800/50 text-orange-700 dark:text-orange-400 rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2"
                            >
                              <Download size={14} /> Download Full Room Attendance
                            </button>

                            {Object.entries(room.branches).map(([branch, info]) => (
                              <div key={branch} className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-900 rounded-lg">
                                <div>
                                  <p className="text-sm font-bold text-gray-800 dark:text-gray-200">{branch}</p>
                                  <p className="text-xs text-gray-600 dark:text-gray-500">{info.count} students • {info.from_roll} → {info.to_roll}</p>
                                </div>
                                <button
                                  onClick={() => handleDownload(viewingPlan.plan_id, 'pdf', room.room_name, branch)}
                                  className="px-3 py-1.5 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-xs font-medium transition-colors flex items-center gap-1"
                                >
                                  <Download size={12} /> PDF
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="lg:col-span-1">
                    <div className="bg-gray-50 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-800 rounded-xl p-4 space-y-3 lg:sticky lg:top-4">
                      <div>
                        <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Attendance Metadata</h3>
                        <p className="text-xs text-gray-600 dark:text-gray-500 mt-1">Used for attendance PDF header details.</p>
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Exam Name *</label>
                        <input
                          name="exam_name"
                          value={attendanceMetadata.exam_name}
                          onChange={handleAttendanceMetadataChange}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Exam Date *</label>
                        <input
                          type="date"
                          name="examDate"
                          value={attendanceMetadata.examDate}
                          onChange={handleAttendanceMetadataChange}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Department *</label>
                        <input
                          name="department"
                          value={attendanceMetadata.department}
                          onChange={handleAttendanceMetadataChange}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Course Name *</label>
                        <input
                          name="course_name"
                          value={attendanceMetadata.course_name}
                          onChange={handleAttendanceMetadataChange}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Course Code *</label>
                        <input
                          name="course_code"
                          value={attendanceMetadata.course_code}
                          onChange={handleAttendanceMetadataChange}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                        />
                      </div>

                      <div className="grid grid-cols-1 gap-2">
                        <div className="space-y-1">
                          <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Chief Invigilator</label>
                          <input
                            name="invigilator1"
                            value={attendanceMetadata.invigilator1}
                            onChange={handleAttendanceMetadataChange}
                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                        <div className="space-y-1">
                          <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Invigilator 2</label>
                          <input
                            name="invigilator2"
                            value={attendanceMetadata.invigilator2}
                            onChange={handleAttendanceMetadataChange}
                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                        <div className="space-y-1">
                          <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Invigilator 3</label>
                          <input
                            name="invigilator3"
                            value={attendanceMetadata.invigilator3}
                            onChange={handleAttendanceMetadataChange}
                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-gray-600 dark:text-gray-500 uppercase tracking-wide">Notes</label>
                        <textarea
                          name="notes"
                          value={attendanceMetadata.notes}
                          onChange={handleAttendanceMetadataChange}
                          rows={2}
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 text-sm resize-none"
                        />
                      </div>

                      <button
                        onClick={handleSaveAttendanceMetadata}
                        disabled={attendanceMetaSaving}
                        className="w-full py-2.5 bg-orange-100 dark:bg-orange-900/30 hover:bg-orange-200 dark:hover:bg-orange-900/50 border border-orange-300 dark:border-orange-700/50 text-orange-700 dark:text-orange-300 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-2 disabled:opacity-70"
                      >
                        {attendanceMetaSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                        Save Metadata
                      </button>
                    </div>
                  </div>
                </div>

                {/* Bulk actions */}
                <div className="flex gap-3 pt-3 border-t border-gray-200 dark:border-gray-800">
                  <button
                    onClick={() => handleDownload(viewingPlan.plan_id, 'master-plan')}
                    className="flex-1 py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 text-sm"
                  >
                    <Download size={16} /> Master Plan PDF
                  </button>
                  <button
                    onClick={() => handleDownload(viewingPlan.plan_id, 'excel')}
                    className="flex-1 py-3 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 text-sm"
                  >
                    <Download size={16} /> Excel Export
                  </button>
                </div>

              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Room Configurator */}
      <MajorRoomConfigurator
        isOpen={showRoomConfig}
        onClose={() => setShowRoomConfig(false)}
        onSubmit={handleRoomConfigSubmit}
        branches={uploadResult?.branchCounts ? 
          Object.fromEntries(
            Object.entries(uploadResult.branchCounts).map(([k, v]) => [k, { count: v }])
          ) : {}
        }
        loading={roomConfigLoading}
      />

      <MajorMasterPlanMetadataForm
        isOpen={showMasterMetadataForm}
        onClose={() => {
          setShowMasterMetadataForm(false);
          setMasterDownloadPlanId(null);
        }}
        onSubmit={handleMasterMetadataSubmit}
        initialData={masterMetadataInitialData}
        loading={masterMetadataLoading}
      />

      {/* Animation keyframes */}
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default MajorExamCreatePlan;
