import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from "framer-motion";
import { 
  Users, Layout, MapPin, Download, Play, Monitor, 
  Loader2, AlertCircle, RefreshCw, CheckCircle2,
  Trash2, Flame, UserCheck, Undo2, BarChart3,
  ArrowRight, AlertTriangle, Info, X
} from 'lucide-react';

const Card = ({ className, children, ref }) => <div ref={ref} className={`glass-card ${className}`}>{children}</div>;

const Button = ({ className = "", children, onClick, disabled, title, variant }) => {
  const base = "inline-flex items-center justify-center rounded-xl font-bold transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none hover:scale-105";
  const safeClassName = className || "";
  const hasCustomBg = safeClassName.includes('bg-');
  const bg = variant === "destructive" 
    ? "bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50 border-2 border-red-200 dark:border-red-800" 
    : variant === "outline" 
    ? "border border-gray-300 dark:border-gray-700 bg-transparent text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
    : hasCustomBg ? "" : "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-white";
  return (
    <button type="button" onClick={onClick} disabled={disabled} title={title} className={`${base} ${bg} ${safeClassName}`}>
      {children}
    </button>
  );
};

const Input = (props) => (
  <input 
    {...props} 
    className={`flex h-10 w-full rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 dark:focus:ring-orange-400 focus:border-orange-500 dark:text-white ${props.className || ''}`} 
  />
);

const AllocationPage = ({ showToast }) => {
  const navigate = useNavigate();

  // Session & Data
  const [session, setSession] = useState(null);
  const [hasActiveSession, setHasActiveSession] = useState(false);
  const [uploadedBatches, setUploadedBatches] = useState([]);
  const [loadingBatches, setLoadingBatches] = useState(false);

  // Classroom
  const [classrooms, setClassrooms] = useState([]);
  const [selectedRoomId, setSelectedRoomId] = useState("");
  const [rows, setRows] = useState(8);
  const [cols, setCols] = useState(10);
  const [blockWidth, setBlockWidth] = useState(2);
  const [brokenSeats, setBrokenSeats] = useState("");
  
  // Layout options
  const [batchByColumn, setBatchByColumn] = useState(true);
  const [enforceNoAdjacentBatches, setEnforceNoAdjacentBatches] = useState(false);

  // Batch selection for this room
  const [numBatchesToAllocate, setNumBatchesToAllocate] = useState(1);
  const [selectedBatchIds, setSelectedBatchIds] = useState([null]);

  // Seating & UI
  const [loading, setLoading] = useState(false);
  const [webData, setWebData] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [undoing, setUndoing] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [usedRoomIds, setUsedRoomIds] = useState([]);

  const chartRef = useRef();

  // ============================================================================
  // LOAD SESSION & BATCHES
  // ============================================================================
  useEffect(() => {
    const loadSession = async () => {
      try {
        const res = await fetch('/api/sessions/active');
        const data = await res.json();
        
        if (data.success && data.session_data) {
          setSession(data.session_data);
          setHasActiveSession(true);
          loadUploadedBatches(data.session_data.session_id);
          setUsedRoomIds(data.session_data.allocated_rooms?.map(r => r.classroom_id) || []);
        }
        else {
          setHasActiveSession(false);}

      } catch (err) {
        console.error('Failed to load session:', err);
        setHasActiveSession(false);
      }
    };
    
    loadSession();
  }, []);

  const loadUploadedBatches = async (sessionId) => {
    if (!sessionId) return;
    
    setLoadingBatches(true);
    try {
      const res = await fetch(`/api/sessions/${sessionId}/uploads`);
      const data = await res.json();
      
      if (data.success && Array.isArray(data.uploads)) {
        setUploadedBatches(data.uploads);
        console.log('📦 Loaded batches:', data.uploads);
      }
    } catch (err) {
      console.error('Failed to load batches:', err);
      if (showToast) showToast('Failed to load batches', 'error');
    } finally {
      setLoadingBatches(false);
    }
  };

  // Load classrooms
  useEffect(() => {
    fetch('/api/classrooms')
      .then(res => res.json())
      .then(data => setClassrooms(Array.isArray(data) ? data : []))
      .catch(err => {
        console.error(err);
        if (showToast) showToast("Failed to load classrooms", "error");
      });
  }, [showToast]);

  // Stats
  const allocated = session?.allocated_count || 0;
  const totalStudents = session?.total_students || 0;
  const pendingCount = totalStudents - allocated;
  const progressPct = totalStudents > 0 ? Math.round((allocated / totalStudents) * 100) : 0;
  const allocatedRooms = session?.allocated_rooms || [];

  // ============================================================================
  // BATCH SELECTION
  // ============================================================================
  const handleNumBatchesChange = (num) => {
    const newNum = Math.max(1, Math.min(num, uploadedBatches.length));
    setNumBatchesToAllocate(newNum);
    setSelectedBatchIds(prev => {
      const updated = [...prev];
      while (updated.length < newNum) updated.push(null);
      return updated.slice(0, newNum);
    });
  };

  const updateSelectedBatch = (index, batchId) => {
    setSelectedBatchIds(prev => {
      const updated = [...prev];
      updated[index] = batchId;
      return updated;
    });
  };

  // ============================================================================
  // ROOM SELECTION
  // ============================================================================
  const handleRoomChange = (roomId) => {
    if (!roomId) {
      setSelectedRoomId("");
      return;
    }
    
    const roomIdNum = parseInt(roomId, 10);
    if (usedRoomIds.includes(roomIdNum)) {
      if (showToast) showToast("⚠️ This room has already been allocated", "error");
      return;
    }
    
    setSelectedRoomId(roomId);
    const room = classrooms.find(r => r.id === roomIdNum);
    if (room) {
      setRows(room.rows);
      setCols(room.cols);
      setBrokenSeats(room.broken_seats || "");
      setBlockWidth(room.block_width || 1);
      if (showToast) showToast(`✅ Loaded ${room.name}`, "success");
    }
  };

  // ============================================================================
  // PARSE BROKEN SEATS
  // ============================================================================
  const parseBrokenSeats = () => {
    const str = brokenSeats;
    const list = [];
    if (typeof str === 'string' && str.includes('-')) {
      str.split(',')
        .map(s => s.trim())
        .filter(Boolean)
        .forEach(p => {
          const [r, c] = p.split('-');
          const rr = parseInt(r, 10) - 1;
          const cc = parseInt(c, 10) - 1;
          if (!isNaN(rr) && !isNaN(cc) && rr >= 0 && rr < rows && cc >= 0 && cc < cols) {
            list.push([rr, cc]);
          }
        });
    }
    return list;
  };

  // ============================================================================
  // PREPARE PAYLOAD - ONLY SELECTED BATCHES
  // ============================================================================
  const preparePayload = () => {
    const validBatchIds = selectedBatchIds.filter(id => id !== null);
    const selectedBatchesData = uploadedBatches.filter(b => validBatchIds.includes(b.batch_id));

    if (selectedBatchesData.length === 0) {
      throw new Error('No batches selected');
    }

    // Build batch data ONLY for selected batches
    const batchCounts = {};
    const batchLabels = {};
    const batchColors = {};

    selectedBatchesData.forEach((batch, idx) => {
      const batchIndex = idx + 1;
      batchCounts[batchIndex] = batch.student_count || 0;
      batchLabels[batchIndex] = batch.batch_name;
      batchColors[batchIndex] = batch.batch_color || '#3b82f6';
    });

    console.log('📤 Payload - Selected batches:', selectedBatchesData.map(b => b.batch_name));
    console.log('📤 Batch counts:', batchCounts);
    console.log('📤 Batch colors:', batchColors);

    return {
      session_id: session?.session_id,
      plan_id: session?.plan_id,
      rows,
      cols,
      block_width: blockWidth,
      broken_seats: parseBrokenSeats(),
      num_batches: selectedBatchesData.length,
      batch_by_column: batchByColumn,
      enforce_no_adjacent_batches: enforceNoAdjacentBatches,
      use_demo_db: true,
      batch_student_counts: batchCounts,
      batch_labels: batchLabels,
      batch_colors: batchColors
    };
  };

  // ============================================================================
  // GENERATE SEATING
  // ============================================================================
  const generate = async () => {
    if (!session) {
      if (showToast) showToast("Please upload student data first", "error");
      return;
    }
    if (!selectedRoomId) {
      if (showToast) showToast("Please select a classroom", "error");
      return;
    }
    
    const validBatchIds = selectedBatchIds.filter(id => id !== null);
    if (validBatchIds.length === 0) {
      if (showToast) showToast("Please select at least one batch", "error");
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch("/api/generate-seating", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(preparePayload())
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || "Failed to generate seating");
      }
      
      setWebData(data);
      setTimeout(() => chartRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
      if (showToast) showToast("Seating generated successfully", "success");
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // SAVE ROOM
  // ============================================================================
  const handleSaveRoom = async () => {
    if (!webData || !session?.session_id) {
      if (showToast) showToast("Generate seating first", "error");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(
        `/api/sessions/${session.session_id}/allocate-room`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            classroom_id: parseInt(selectedRoomId, 10),
            seating_data: webData
          })
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Allocation failed");

      // Refresh session
      const sessionRes = await fetch('/api/sessions/active');
      const sessionData = await sessionRes.json();
      if (sessionData.success) {
        setSession(sessionData.session_data);
        setUsedRoomIds(sessionData.session_data.allocated_rooms?.map(r => r.classroom_id) || []);
      }

      setWebData(null);
      setSelectedRoomId("");
      setSelectedBatchIds([null]);

      if (showToast) {
        const remaining = data.remaining_count || 0;
        if (remaining === 0) {
          showToast(`✅ All students allocated — ready to finalize!`, "success");
        } else {
          showToast(`✅ Room saved! ${remaining} students remaining`, "success");
        }
      }
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // UNDO
  // ============================================================================
  const handleUndoLastRoom = async () => {
    if (!session?.session_id || allocatedRooms.length === 0) {
      if (showToast) showToast("No rooms to undo", "error");
      return;
    }
    if (!window.confirm("Undo last room allocation?")) return;

    setUndoing(true);
    try {
      const res = await fetch(
        `/api/sessions/${session.session_id}/undo`,
        { method: 'POST' }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      const sessionRes = await fetch('/api/sessions/active');
      const sessionData = await sessionRes.json();
      if (sessionData.success) {
        setSession(sessionData.session_data);
      }

      setWebData(null);
      setSelectedRoomId("");
      if (showToast) showToast(data.message || "Undo successful", "success");
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setUndoing(false);
    }
  };

  // ============================================================================
  // FINALIZE
  // ============================================================================
  const handleFinalizeSession = async () => {
    if (!session?.session_id) {
      if (showToast) showToast("No active session", "error");
      return;
    }
    
    if (pendingCount > 0) {
      if (showToast) showToast(`Cannot finalize: ${pendingCount} students pending`, "error");
      return;
    }
    
    if (!window.confirm("✅ Finalize this session?\n\nThis will mark the session as complete.")) return;

    setLoading(true);
    try {
      const res = await fetch(
        `/api/sessions/${session.session_id}/finalize`, 
        { method: 'POST' }
      );
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || "Finalize failed");

      setWebData(null);
      setSession(null);
      if (showToast) showToast("🎉 Session finalized successfully!", "success");
      setTimeout(() => navigate('/create-plan', { replace: true }), 500);
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // RESET DATABASE
  // ============================================================================
  const handleResetDatabase = async () => {
    if (!window.confirm("⚠️ DANGER: Delete ALL student data?")) return;
    if (!window.confirm("⚠️ FINAL WARNING: Cannot be undone!")) return;

    setResetting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch("/api/reset-data", {
        method: "POST",
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error("Reset failed");
      setSession(null);
      setWebData(null);
      if (showToast) showToast("Database cleared", "success");
      navigate('/upload', { replace: true });
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setResetting(false);
    }
  };

  // ============================================================================
  // FETCH STATS
  // ============================================================================
  const fetchStats = async () => {
    if (!session?.session_id) return;
    try {
      const res = await fetch(`/api/sessions/${session.session_id}/stats`);
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error);
      setStats(data.stats);
      setShowStats(true);
    } catch (e) {
      if (showToast) showToast("Failed to load stats", "error");
    }
  };

  // ============================================================================
  // DOWNLOAD PDF
  // ============================================================================
  const downloadPdf = async () => {
    if (!webData) {
      if (showToast) showToast("Generate seating first", "error");
      return;
    }
    setPdfLoading(true);
    try {
      const payload = preparePayload();
      payload.seating = webData.seating;
      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Server failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `seating_${Date.now()}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      if (showToast) showToast("PDF downloaded", "success");
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setPdfLoading(false);
    }
  };

  // ============================================================================
  // NO SESSION
  // ============================================================================
  if (!session) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-900 rounded-2xl shadow-xl border-2 border-amber-500 p-8">
          <div className="text-center space-y-6">
            <div className="w-20 h-20 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mx-auto">
              <AlertTriangle className="w-10 h-10 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No Active Session</h2>
              <p className="text-gray-600 dark:text-gray-400">Upload student data to begin allocation</p>
            </div>
            <button
              onClick={() => navigate('/upload', { replace: true })}
              className="w-full h-14 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-bold rounded-xl"
            >
              <ArrowRight className="inline mr-2" size={20} />
              Go to Upload
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-[1600px] mx-auto space-y-8">
        
        {/* HEADER */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-gray-200 dark:border-gray-800">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Active Session</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">Allocation Control</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Managing {totalStudents} students</p>
          </div>
          <div className="flex gap-4 items-end">
            <div className="text-right">
              <div className="text-xs text-gray-500 mb-1">Allocated</div>
              <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400">{allocated}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500 mb-1">Pending</div>
              <div className="text-3xl font-black text-orange-600 dark:text-orange-400">{pendingCount}</div>
            </div>
          </div>
        </div>

        {/* PROGRESS CARD */}
        <Card className="p-6 border-2 border-orange-500 dark:border-orange-400">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Session Progress</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">ID: {session.plan_id}</p>
            </div>
            <Button onClick={fetchStats} variant="outline" className="h-9 px-3 text-sm">
              <BarChart3 size={16} className="mr-2" />
              View Stats
            </Button>
          </div>
          <div className="relative h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-4">
            <motion.div 
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-orange-500 to-amber-500 flex items-center justify-end pr-2"
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.5 }}
            >
              <span className="text-white text-xs font-bold">{progressPct}%</span>
            </motion.div>
          </div>
          <div className="flex justify-between text-sm font-mono text-gray-600 dark:text-gray-400 mb-4">
            <span>{allocated} / {totalStudents} allocated</span>
            <span>{pendingCount} remaining</span>
          </div>
          
          {allocatedRooms.length > 0 && (
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs font-bold uppercase text-gray-500 mb-2">Allocated Rooms:</p>
              <div className="flex flex-wrap gap-2">
                {allocatedRooms.map((room, idx) => (
                  <div 
                    key={room?.classroom_id || idx}
                    className="px-3 py-1.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-lg text-xs font-bold border border-emerald-200 dark:border-emerald-700"
                  >
                    {room?.classroom_name || 'Unknown'}: {room?.count || 0} seats
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* STATS MODAL */}
        <AnimatePresence>
          {showStats && stats && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              onClick={() => setShowStats(false)}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                className="bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-2xl w-full max-h-[80vh] overflow-auto border-2 border-gray-200 dark:border-gray-700"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Allocation Statistics</h2>
                  <button onClick={() => setShowStats(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
                    <X size={20} />
                  </button>
                </div>
                
                {Array.isArray(stats?.rooms) && stats.rooms.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-bold mb-3 text-gray-900 dark:text-white">Room Utilization</h3>
                    <div className="space-y-2">
                      {stats.rooms.map((room, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-gray-900 dark:text-white">{room?.name || 'Unknown'}</span>
                            <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                              {room?.allocated || 0}/{room?.capacity || 0} ({Math.round(((room?.allocated || 0)/(room?.capacity || 1))*100)}%)
                            </span>
                          </div>
                          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${((room?.allocated || 0)/(room?.capacity || 1))*100}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {Array.isArray(stats?.batches) && stats.batches.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-3 text-gray-900 dark:text-white">Batch Distribution</h3>
                    <div className="grid grid-cols-2 gap-3">
                      {stats.batches.map((batch, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl text-center">
                          <div className="text-sm font-bold text-gray-600 dark:text-gray-400 mb-1">{batch?.batch_name || 'Unknown'}</div>
                          <div className="text-2xl font-black text-orange-600 dark:text-orange-400">{batch?.count || 0}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl border border-orange-200 dark:border-orange-800">
                  <div className="text-sm font-bold text-orange-900 dark:text-orange-100 mb-1">Overall Completion</div>
                  <div className="text-3xl font-black text-orange-600 dark:text-orange-400">{stats?.completion_rate || 0}%</div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* MAIN GRID */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          {/* LEFT: CONFIGURATION */}
          <Card className="xl:col-span-4 h-full flex flex-col overflow-hidden border-2 border-gray-200 dark:border-gray-800">
            <div className="p-6 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border-b-2 border-gray-200 dark:border-gray-800">
              <h2 className="text-xl font-bold text-orange-900 dark:text-orange-100 flex items-center gap-2">
                <Flame size={24} className="text-orange-500" />
                Configuration
              </h2>
            </div>
            
            <div className="p-6 space-y-6 flex-1 overflow-y-auto custom-scrollbar">
              {/* Classroom Selection */}
              <div>
                <label className="flex items-center gap-2 text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest mb-3">
                  <Monitor size={16} className="text-orange-500" />
                  Select Classroom
                </label>
                <select 
                  value={selectedRoomId} 
                  onChange={e => handleRoomChange(e.target.value)} 
                  className="w-full h-12 px-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl font-bold text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">-- Select a Classroom --</option>
                  {classrooms.map(r => {
                    const isUsed = usedRoomIds.includes(r.id);
                    return (
                      <option key={r.id} value={r.id} disabled={isUsed}>
                        {r.name} {isUsed ? '✓ (Used)' : ''}
                      </option>
                    );
                  })}
                </select>
                {selectedRoomId && (
                  <div className="mt-3 flex gap-2 text-xs font-mono flex-wrap">
                    <span className="bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 px-3 py-1.5 rounded-lg font-bold border border-orange-200 dark:border-orange-800">
                      {rows}×{cols} Grid
                    </span>
                    {brokenSeats && (
                      <span className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-lg font-bold border border-red-200 dark:border-red-800">
                        {brokenSeats.split(',').filter(Boolean).length} Broken
                      </span>
                    )}
                    <span className="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-3 py-1.5 rounded-lg font-bold border border-blue-200 dark:border-blue-800">
                      {(rows * cols) - parseBrokenSeats().length} Seats
                    </span>
                  </div>
                )}
              </div>

              {/* BATCH SELECTION - NEW DESIGN */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="flex items-center gap-2 text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest">
                    <Users size={16} className="text-orange-500" />
                    Batches to Allocate
                  </label>
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Count:</span>
                    <input 
                      type="number" 
                      value={numBatchesToAllocate} 
                      onChange={e => handleNumBatchesChange(Math.max(1, parseInt(e.target.value) || 1))}
                      min="1"
                      max={uploadedBatches.length}
                      className="w-12 h-9 text-center border-2 border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-bold focus:ring-2 focus:ring-orange-500"
                    />
                  </div>
                </div>
                
                {loadingBatches ? (
                  <div className="text-center py-6"><Loader2 className="animate-spin mx-auto" size={20} /></div>
                ) : uploadedBatches.length === 0 ? (
                  <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800 text-xs text-amber-700 dark:text-amber-300">
                    No batches uploaded in this session
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedBatchIds.map((selectedId, idx) => {
                      const selectedBatch = selectedId ? uploadedBatches.find(b => b.batch_id === selectedId) : null;
                      return (
                        <div key={idx} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-750 rounded-xl border-2 border-gray-200 dark:border-gray-700 space-y-3 hover:border-orange-500 dark:hover:border-orange-400 transition-all">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-gray-600 dark:text-gray-400">Batch {idx + 1}:</span>
                            <select
                              value={selectedId || ""}
                              onChange={e => updateSelectedBatch(idx, e.target.value || null)}
                              className="flex-1 h-9 px-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg text-sm font-bold text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500"
                            >
                              <option value="">-- Choose Batch --</option>
                              {uploadedBatches.map(batch => (
                                <option key={batch.batch_id} value={batch.batch_id}>
                                  {batch.batch_name} ({batch.student_count} students)
                                </option>
                              ))}
                            </select>
                            {selectedBatch && (
                              <div 
                                className="w-10 h-9 rounded-lg border-2 border-gray-300 dark:border-gray-600"
                                style={{ backgroundColor: selectedBatch.batch_color }}
                                title={`Color: ${selectedBatch.batch_color}`}
                              />
                            )}
                          </div>
                          {selectedBatch && (
                            <div className="text-xs font-mono text-gray-600 dark:text-gray-400 px-3 py-1.5 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                              Total Students: <span className="font-bold">{selectedBatch.student_count}</span>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* LAYOUT OPTIONS */}
              <div className="flex flex-col gap-3 pt-4 border-t-2 border-gray-200 dark:border-gray-800">
                <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                  <input 
                    type="checkbox" 
                    checked={batchByColumn} 
                    onChange={e => setBatchByColumn(e.target.checked)} 
                    className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"
                  />
                  <Layout size={16} className="text-orange-500" />
                  Fill By Columns
                </label>
                <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                  <input 
                    type="checkbox" 
                    checked={enforceNoAdjacentBatches} 
                    onChange={e => setEnforceNoAdjacentBatches(e.target.checked)} 
                    className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"
                  />
                  <MapPin size={16} className="text-orange-500" />
                  Enforce Batch Gap
                </label>
              </div>

              <div className="pt-4 border-t-2 border-gray-200 dark:border-gray-800">
                <Button onClick={handleResetDatabase} variant="destructive" className="w-full h-11 text-sm font-bold uppercase tracking-wide" disabled={resetting}>
                  {resetting ? <Loader2 className="animate-spin mr-2" size={16}/> : <Trash2 size={16} className="mr-2"/>}
                  {resetting ? 'Resetting...' : 'Reset All Data'}
                </Button>
              </div>
            </div>

            {/* BUTTONS FOOTER */}
            <div className="p-6 border-t-2 border-gray-200 dark:border-gray-800 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750 space-y-3">
              <Button 
                onClick={generate} 
                disabled={loading || pendingCount === 0 || !selectedRoomId || selectedBatchIds.filter(id => id !== null).length === 0}
                className="w-full h-14 bg-gradient-to-r from-orange-500 to-amber-500 text-white hover:from-orange-600 hover:to-amber-600 shadow-lg hover:shadow-xl text-base font-black uppercase tracking-wide"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin mr-2" size={20}/>
                    Generating...
                  </>
                ) : pendingCount === 0 ? (
                  <>
                    <CheckCircle2 className="mr-2" size={20}/>
                    All Students Allocated
                  </>
                ) : (
                  <>
                    <Play className="mr-2" size={20}/>
                    Generate Seating ({pendingCount} pending)
                  </>
                )}
              </Button>

              <div className="flex gap-2">
                {webData && !loading && (
                  <Button 
                    onClick={handleSaveRoom}
                    className="flex-1 h-12 bg-emerald-500 hover:bg-emerald-600 text-white font-bold"
                  >
                    <CheckCircle2 className="mr-2" size={18}/>
                    Save & Continue
                  </Button>
                )}
                
                {hasActiveSession && pendingCount === 0 && !webData && (
                  <Button 
                    onClick={handleFinalizeSession}
                    disabled={loading}
                    className="flex-1 h-12 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white shadow-xl font-black"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="animate-spin mr-2" size={18}/>
                        Finalizing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="mr-2" size={18}/>
                        Finalize Session
                      </>
                    )}
                  </Button>
                )}
                
                {allocatedRooms.length > 0 && (
                  <Button 
                    onClick={handleUndoLastRoom}
                    disabled={undoing || loading}
                    className="h-12 px-4 bg-amber-100 text-amber-700 hover:bg-amber-200 dark:bg-amber-900/30 dark:text-amber-300"
                    title="Undo last room allocation"
                  >
                    {undoing ? <Loader2 className="animate-spin" size={18}/> : <Undo2 size={18}/>}
                  </Button>
                )}
              </div>
              
              {pendingCount === 0 && (
                <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg flex items-center gap-2">
                  <Info size={16} className="text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                  <p className="text-xs text-emerald-700 dark:text-emerald-300 font-bold">
                    All students allocated! Click "Finalize Session" above to complete.
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* RIGHT: VISUALIZATION */}
          <Card className="xl:col-span-8 h-full flex flex-col relative overflow-hidden p-6 border-2 border-gray-200 dark:border-gray-800" ref={chartRef}>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-black text-gray-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
                  <Layout className="text-orange-500" size={24} />
                  Hall Visualization
                </h2>
                {webData && Array.isArray(webData.seating) && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-mono">
                    {webData.seating.flat().filter(s => s && !s.is_unallocated && !s.is_broken).length} seats allocated
                  </p>
                )}
              </div>
              {webData && (
                <div className="flex gap-2 flex-wrap">
                  <Button onClick={() => navigate(`/attendance/${session?.plan_id}`)} className="h-10 px-4 bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300 text-xs font-bold">
                    <UserCheck size={14} className="mr-2"/> Attendance
                  </Button>
                  <Button onClick={downloadPdf} disabled={pdfLoading} className="h-10 px-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white text-xs font-bold">
                    {pdfLoading ? (
                      <>
                        <Loader2 className="animate-spin mr-2" size={14}/>
                        Generating...
                      </>
                    ) : (
                      <>
                        <Download size={14} className="mr-2"/>
                        Export PDF
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={() => setWebData(null)} className="h-10 px-4 text-xs font-bold">
                    <RefreshCw className="w-4 h-4 mr-2" /> Clear
                  </Button>
                </div>
              )}
            </div>

            {!webData ? (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-300 dark:text-gray-600">
                <div className="relative mb-6">
                  <div className="absolute inset-0 bg-orange-500 rounded-full blur-2xl opacity-20"></div>
                  <Layout size={80} className="relative opacity-20"/>
                </div>
                <p className="font-bold uppercase tracking-widest text-sm">Ready to generate</p>
                <p className="text-xs mt-2 text-gray-400">Select classroom and batches, then click Generate</p>
              </div>
            ) : (
              <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-10 overflow-auto custom-scrollbar relative z-10 rounded-xl">
                {Array.isArray(webData.seating) && (
                  <div className="grid gap-3 mx-auto" style={{ gridTemplateColumns: `repeat(${cols}, minmax(120px, 1fr))`, width: 'fit-content' }}>
                    {webData.seating.map((row, rIdx) => 
                      Array.isArray(row) && row.map((seat, cIdx) => {
                        const seatIndex = rIdx * cols + cIdx + 1;
                        const isBroken = seat?.is_broken;
                        const isAllocated = !isBroken && !seat?.is_unallocated;
                        const deskRow = rIdx + 1;
                        const deskCol = cIdx + 1;
                        return (
                          <motion.div
                            key={`${rIdx}-${cIdx}`}
                            initial={{ opacity: 0, scale: 0.85, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            transition={{ delay: (rIdx * cols + cIdx) * 0.003, type: "spring", stiffness: 300, damping: 24 }}
                            className={`relative flex flex-col items-center justify-between p-3 transition-all duration-200 border-2 rounded-xl bg-white dark:bg-gray-900 shadow-sm hover:shadow-md min-h-[120px] group cursor-pointer ${
                              isBroken 
                                ? 'border-red-200 bg-red-50/20 dark:bg-red-900/10' 
                                : isAllocated 
                                  ? 'border-gray-200 dark:border-gray-800 hover:border-orange-400 hover:scale-[1.02]' 
                                  : 'border-dashed border-gray-200 dark:border-gray-800 opacity-40'
                            }`}
                          >
                            {isAllocated && (
                              <div className="absolute top-0 inset-x-0 h-1.5 rounded-t-xl" style={{ backgroundColor: seat.color }} />
                            )}
                            {isAllocated ? (
                              <>
                                <span className="text-[9px] font-extrabold text-gray-400 dark:text-gray-500 uppercase tracking-tighter">
                                  {seat.batch_label || `B-${seat.batch}`}
                                </span>
                                <span className="text-lg font-black text-gray-900 dark:text-white leading-none my-2 group-hover:text-orange-600 transition-colors">
                                  {seat.roll_number}
                                </span>
                                <div className="w-full flex justify-between items-center gap-1.5 pt-2 border-t border-gray-100 dark:border-gray-800 mt-auto">
                                  <div className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                                    <span className="text-[8px] font-mono font-bold text-gray-600 dark:text-gray-400">SET: {seat.paper_set || 'A'}</span>
                                  </div>
                                  <div className="px-1.5 py-0.5 rounded bg-orange-50 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-700">
                                    <span className="text-[8px] font-mono font-bold text-orange-600 dark:text-orange-400">
                                      {deskRow}-{deskCol}
                                    </span>
                                  </div>
                                </div>
                              </>
                            ) : isBroken ? (
                              <div className="flex flex-col items-center justify-center h-full">
                                <AlertCircle className="w-5 h-5 text-red-400 mb-1" />
                                <span className="text-[10px] font-bold text-red-500 uppercase">Broken</span>
                              </div>
                            ) : (
                              <div className="flex items-center justify-center h-full">
                                <span className="text-xs font-mono text-gray-300 dark:text-gray-700">{seatIndex}</span>
                              </div>
                            )}
                          </motion.div>
                        );
                      })
                    )}
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>
      </div>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar{width:8px;height:8px}
        .custom-scrollbar::-webkit-scrollbar-track{background:transparent}
        .custom-scrollbar::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:10px}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#9ca3af}
        .dark .custom-scrollbar::-webkit-scrollbar-thumb{background:#4b5563}
        .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#6b7280}
      `}</style>
    </div>
  );
};

export default AllocationPage;