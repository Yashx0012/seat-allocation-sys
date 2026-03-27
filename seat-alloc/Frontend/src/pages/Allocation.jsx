import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getToken } from '../utils/tokenStorage';
import { motion, AnimatePresence } from "framer-motion";
import { getPrintFriendlyColor } from '../utils/colorUtils';
import { 
  Users, Layout, MapPin, Download, Play, Monitor, 
  Loader2, AlertCircle, RefreshCw, CheckCircle2,
  Trash2, Flame, UserCheck, Undo2, BarChart3,
  ArrowRight, AlertTriangle, Info, X, ShieldCheck, XCircle, LogOut,
  UserPlus, Palette
} from 'lucide-react';
import OptimizationConfigModal from '../components/OptimizationConfigModal';
import FeatureTooltip from '../components/FeatureTooltip';

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

const ConstraintIndicator = ({ constraints, validation }) => {
  if (!constraints) return null;
  
  return (
    <div className="flex flex-col gap-2 mt-4">
      <div className="grid grid-cols-2 gap-2">
      {constraints.map((c, i) => (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          key={i} 
          className={`p-3 rounded-xl border-2 flex items-start gap-3 ${
            c.satisfied 
              ? 'bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-100 dark:border-emerald-900/30' 
              : 'bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30'
          }`}
        >
          <div className={`mt-0.5 p-1.5 rounded-lg ${c.satisfied ? 'bg-emerald-100 dark:bg-emerald-800/40 text-emerald-600' : 'bg-red-100 dark:bg-red-800/40 text-red-600'}`}>
            {c.satisfied ? <ShieldCheck size={14} /> : <AlertTriangle size={14} />}
          </div>
          <div>
            <div className="text-[10px] font-black uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-0.5">{c.name}</div>
            <div className={`text-xs font-bold ${c.satisfied ? 'text-emerald-700 dark:text-emerald-400' : 'text-red-700 dark:text-red-400'}`}>
              {c.satisfied ? 'Constraint Satisfied' : 'Violation Detected'}
            </div>
          </div>
        </motion.div>
      ))}
      </div>
      
      {validation && !validation.is_valid && validation.errors && validation.errors.length > 0 && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg flex gap-2 items-start mt-2">
          <XCircle className="text-red-500 shrink-0 mt-0.5" size={18} />
          <div>
            <h4 className="text-sm font-black text-red-800 dark:text-red-300 uppercase tracking-tight">Critical Algorithm Warnings</h4>
            <ul className="mt-1 space-y-1">
              {validation.errors.map((err, idx) => (
                <li key={idx} className="text-xs font-bold text-red-700 dark:text-red-400 flex items-center gap-1.5">
                  <div className="w-1 h-1 bg-red-500 rounded-full" />
                  {err}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

const AllocationPage = ({ showToast }) => {
  const navigate = useNavigate();
  const { user } = useAuth();

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
  const [blockStructure, setBlockStructure] = useState(null); // Array of block widths e.g. [3, 2, 3, 2]
  const [brokenSeats, setBrokenSeats] = useState("");
  
  // Layout options
  const [batchByColumn, setBatchByColumn] = useState(true);
  const [randomizeColumn, setRandomizeColumn] = useState(false);
  const [allowAdjacentSeating, setAllowAdjacentSeating] = useState(false);
  const [optimizeRoom, setOptimizeRoom] = useState(false);
  const [isOptModalOpen, setIsOptModalOpen] = useState(false);
  const [batchSuccessors, setBatchSuccessors] = useState({});

  // Batch selection for this room
  const [numBatchesToAllocate, setNumBatchesToAllocate] = useState(1);
  const [selectedBatchIds, setSelectedBatchIds] = useState([null]);

  // Seating & UI
  const [initializing, setInitializing] = useState(true);
  const [loading, setLoading] = useState(false);
  const [webData, setWebData] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [undoing, setUndoing] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [batchAllocations, setBatchAllocations] = useState({});
  const [usedRoomIds, setUsedRoomIds] = useState([]);
  const [selectedRoomName, setSelectedRoomName] = useState("");

  // External Student Modal State
  const [showExternalModal, setShowExternalModal] = useState(false);
  const [selectedEmptySeat, setSelectedEmptySeat] = useState(null);
  const [externalStudent, setExternalStudent] = useState({
    roll_number: '',
    student_name: '',
    batch_label: '',
    batch_color: '#3b82f6'
  });
  const [roomBatches, setRoomBatches] = useState([]);
  const [addingExternal, setAddingExternal] = useState(false);
  const [showNewBatchInput, setShowNewBatchInput] = useState(false);

  const chartRef = useRef();

  // ============================================================================
  // LOAD SESSION & BATCHES
  // ============================================================================
  //============================================================================
  // ✅ FIXED: Single initialization effect
  // ============================================================================
  useEffect(() => {
    const initializePage = async () => {
      setInitializing(true);
      
      try {
        const token = getToken();
        const res = await fetch('/api/sessions/active', {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        const data = await res.json();
        
        if (data.success && data.session_data && data.session_data.status === 'active') {
          setSession(data.session_data);
          setHasActiveSession(true);
          await loadUploadedBatches(data.session_data.session_id);
          await loadBatchAllocations(data.session_data.session_id);
          setUsedRoomIds(data.session_data.allocated_rooms?.map(r => r.classroom_id) || []);
          console.log('✅ Active session loaded:', data.session_data.session_id);
        } else {
          setSession(null);
          setHasActiveSession(false);
          console.log('ℹ️ No active session found');
        }
      } catch (err) {
        console.error('Failed to load session:', err);
        setSession(null);
        setHasActiveSession(false);
      }
      
      // Small delay to prevent flash
      await new Promise(resolve => setTimeout(resolve, 150));
      setInitializing(false);
    };
    
    initializePage();
  }, []);

  const loadUploadedBatches = async (sessionId) => {
    if (!sessionId) return;
    
    setLoadingBatches(true);
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${sessionId}/uploads`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const data = await res.json();
      
      if (data.success && Array.isArray(data.uploads)) {
        setUploadedBatches(data.uploads);
        console.log('📦 Loaded batches:', data.uploads);
      }
    } catch (err) {
      console.error('Failed to load batches:', err);
    } finally {
      setLoadingBatches(false);
    }
  };

  const loadBatchAllocations = async (sessionId) => {
    if (!sessionId) return;
    
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${sessionId}/stats`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const data = await res.json();
      
      if (data.success && Array.isArray(data.stats?.batches)) {
        const allocMap = {};
        data.stats.batches.forEach(batch => {
          allocMap[batch.batch_name] = batch.count || 0;
        });
        setBatchAllocations(allocMap);
        console.log('📊 Loaded batch allocations:', allocMap);
      }
    } catch (err) {
      console.error('Failed to load batch allocations:', err);
    }
  };

  // Load classrooms
  useEffect(() => {
    const token = getToken();
    fetch('/api/classrooms', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
      .then(res => res.json())
      .then(data => setClassrooms(Array.isArray(data) ? data : []))
      .catch(err => {
        console.error(err);
      });
  }, []);

  // Re-fetch when user changes (account switch)
  const userIdentity = user?.email || user?.id;
  useEffect(() => {
    if (userIdentity) {
      setSession(null);
      setHasActiveSession(false);
      setUploadedBatches([]);
      setClassrooms([]);
      setBatchAllocations({});
      setUsedRoomIds([]);
      setWebData(null);
      setInitializing(true);
      // Re-run initialization
      const reinitialize = async () => {
        try {
          const token = getToken();
          const res = await fetch('/api/sessions/active', {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          });
          const data = await res.json();
          if (data.success && data.session_data && data.session_data.status === 'active') {
            setSession(data.session_data);
            setHasActiveSession(true);
            await loadUploadedBatches(data.session_data.session_id);
            await loadBatchAllocations(data.session_data.session_id);
            setUsedRoomIds(data.session_data.allocated_rooms?.map(r => r.classroom_id) || []);
          }
          // Re-load classrooms
          const cRes = await fetch('/api/classrooms', {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          });
          const cData = await cRes.json();
          setClassrooms(Array.isArray(cData) ? cData : []);
        } catch (err) {
          console.error('Re-init failed:', err);
        } finally {
          setInitializing(false);
        }
      };
      reinitialize();
    }
  }, [userIdentity]); // eslint-disable-line react-hooks/exhaustive-deps

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
      setSelectedRoomName(""); // Reset name
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
      setSelectedRoomName(room.name); // <--- CAPTURE NAME HERE
      setRows(room.rows);
      setCols(room.cols);
      setBrokenSeats(room.broken_seats || "");
      setBlockWidth(room.block_width || 1);
      // Capture block_structure for variable block widths
      setBlockStructure(room.block_structure || null);
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
  // PREPARE PAYLOAD - ONLY SELECTED BATCHES (IN USER-SPECIFIED ORDER)
  // ============================================================================
  const preparePayload = () => {
    const validBatchIds = selectedBatchIds.filter(id => id !== null);
    
    // CRITICAL: Map from selectedBatchIds order to maintain user-specified sequence
    // Instead of filtering uploadedBatches (which maintains upload order),
    // we iterate through validBatchIds to preserve the order user selected
    const selectedBatchesData = validBatchIds
      .map(id => uploadedBatches.find(b => b.batch_id === id))
      .filter(Boolean); // Remove any undefined entries

    if (selectedBatchesData.length === 0) {
      throw new Error('No batches selected');
    }

    // Include any Successor batches that aren't explicitly selected
    // This allows chaining to external batches (e.g., Overflow -> Batch X)
    const successorIds = Object.values(batchSuccessors).filter(id => id !== null);
    const extraBatchIds = successorIds.filter(id => !validBatchIds.includes(id));
    
    // Find these extra batches in uploadedBatches
    const extraBatchesData = uploadedBatches.filter(b => extraBatchIds.includes(b.batch_id));
    
    // Merge for payload (but NOT for UI state)
    const allPayloadBatches = [...selectedBatchesData, ...extraBatchesData];

    // Build batch data
    const batchCounts = {};
    const batchLabels = {};
    const batchColors = {};

    // Map Real Batch IDs to 1-based Indices for the algorithm
    const idToIndexMap = {};
    allPayloadBatches.forEach((b, i) => {
       idToIndexMap[b.batch_id] = i + 1;
    });
    
    // Populate counts/labels/colors using the Index
    allPayloadBatches.forEach((batch, idx) => {
      const batchIndex = idx + 1;
      batchCounts[batchIndex] = batch.student_count || 0;
      batchLabels[batchIndex] = batch.batch_name;
      batchColors[batchIndex] = batch.batch_color || '#3b82f6';
    });
    
    // Transform successors to use Indices (Algorithm expects 1..N)
    const payloadSuccessors = {};
    Object.entries(batchSuccessors).forEach(([fromId, toId]) => {
        // Ensure both IDs are valid (exist in our payload list)
        // Note: fromId is a string key, toId is number
        const fId = parseInt(fromId, 10);
        if (toId && idToIndexMap[fId] && idToIndexMap[toId]) {
            payloadSuccessors[idToIndexMap[fId]] = idToIndexMap[toId];
        }
    });

    console.log('📤 Payload - All batches:', allPayloadBatches.map(b => b.batch_name));
    console.log('📤 Mapped Successors:', payloadSuccessors);

    return {
      session_id: session?.session_id,
      plan_id: session?.plan_id,
      room_no: selectedRoomName, 
      rows,
      cols,
      block_width: blockWidth,
      block_structure: blockStructure, // Variable block widths array
      broken_seats: parseBrokenSeats(),
      num_batches: allPayloadBatches.length, // Includes extras
      batch_by_column: batchByColumn,
      randomize_column: randomizeColumn,
      allow_adjacent_same_batch: allowAdjacentSeating,
      optimize_stgy: optimizeRoom,
      batch_successors: payloadSuccessors, // <--- TRANSORMED
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
      const token = getToken();
      const res = await fetch("/api/generate-seating", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
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
      const token = getToken();
      const res = await fetch(
        `/api/sessions/${session.session_id}/allocate-room`,
        {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
          },
          body: JSON.stringify({
            classroom_id: parseInt(selectedRoomId, 10),
            room_no: selectedRoomName || 'UnKnown', // <--- ADD THIS LINE
            seating_data: webData
          })
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Allocation failed");

      // Refresh session
      const sessionRes = await fetch('/api/sessions/active', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const sessionData = await sessionRes.json();
      if (sessionData.success) {
        setSession(sessionData.session_data);
        setUsedRoomIds(sessionData.session_data.allocated_rooms?.map(r => r.classroom_id) || []);
        await loadBatchAllocations(sessionData.session_data.session_id);
      }

      setWebData(null);
      setSelectedRoomId("");
      setSelectedBatchIds([null]);
      setNumBatchesToAllocate(1);

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
      const token = getToken();
      const res = await fetch(
        `/api/sessions/${session.session_id}/undo`,
        { 
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      const sessionRes = await fetch('/api/sessions/active', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
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
    
    // Extract allocated rooms reliably - use multiple fallback keys
    const allocatedRoomList = 
      session?.allocated_rooms?.map((r) => r.classroom_name) ||
      allocatedRooms?.map((r) => r.classroom_name) ||
      [];
    
    if (allocatedRoomList.length === 0) {
      if (showToast) showToast("Warning: No rooms detected, but proceeding with finalize", "warning");
    }
    
    if (!window.confirm("✅ Finalize this session?\n\nThis will mark the session as complete and clean up the cache.")) return;

    setLoading(true);
    try {
      const token = getToken();
      const res = await fetch(
        `/api/sessions/${session.session_id}/finalize`, 
        { 
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
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
  // END SESSION (Expire current session only)
  // ============================================================================
  const handleEndSession = async () => {
    if (!session?.session_id) {
      if (showToast) showToast("No active session to end", "error");
      return;
    }
    if (!window.confirm("End this session? You can start a new one after.")) return;

    setResetting(true);
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${session.session_id}/expire`, {
        method: "POST",
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error("Failed to end session");
      setSession(null);
      setHasActiveSession(false);
      setWebData(null);
      if (showToast) showToast("Session ended successfully", "success");
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
      const token = getToken();
      const res = await fetch(`/api/sessions/${session.session_id}/stats`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
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
      const token = getToken();
      const payload = preparePayload();
      payload.seating = webData.seating;
      // Include metadata from webData which contains block_structure from algorithm
      if (webData.metadata) {
        payload.metadata = webData.metadata;
      }
      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
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
  // EXTERNAL STUDENT FUNCTIONS
  // ============================================================================
  
  const loadRoomBatches = async () => {
    if (!session?.session_id || !selectedRoomName) return;
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${session.session_id}/rooms/${encodeURIComponent(selectedRoomName)}/batches`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const data = await res.json();
      if (data.status === 'success') {
        setRoomBatches(data.batches || []);
      }
    } catch (e) {
      console.error('Failed to load room batches:', e);
    }
  };

  const handleEmptySeatClick = async (seat, rowIdx, colIdx) => {
    // Load room batches for dropdown
    await loadRoomBatches();
    
    setSelectedEmptySeat({
      position: seat?.position || `${String.fromCharCode(65 + rowIdx)}${colIdx + 1}`,
      row: rowIdx,
      col: colIdx
    });
    setExternalStudent({
      roll_number: '',
      student_name: '',
      batch_label: roomBatches.length > 0 ? roomBatches[0].label : '',
      batch_color: roomBatches.length > 0 ? roomBatches[0].color : '#3b82f6'
    });
    setShowNewBatchInput(false);
    setShowExternalModal(true);
  };

  const handleAddExternalStudent = async () => {
    if (!externalStudent.roll_number || !externalStudent.batch_label) {
      if (showToast) showToast("Roll number and batch are required", "error");
      return;
    }
    
    setAddingExternal(true);
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${session.session_id}/rooms/${encodeURIComponent(selectedRoomName)}/add-external-student`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          seat_position: selectedEmptySeat.position,
          seat_row: selectedEmptySeat.row,
          seat_col: selectedEmptySeat.col,
          roll_number: externalStudent.roll_number,
          student_name: externalStudent.student_name,
          batch_label: externalStudent.batch_label,
          batch_color: externalStudent.batch_color
        })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.message || 'Failed to add student');
      }
      
      // Update webData locally with the new student
      if (webData && data.seat) {
        const newSeating = [...webData.seating];
        newSeating[selectedEmptySeat.row][selectedEmptySeat.col] = data.seat;
        setWebData({ ...webData, seating: newSeating });
      }
      
      if (showToast) showToast(`Student ${externalStudent.roll_number} added to seat ${selectedEmptySeat.position}`, "success");
      setShowExternalModal(false);
      setSelectedEmptySeat(null);
      
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    } finally {
      setAddingExternal(false);
    }
  };

  const handleRemoveExternalStudent = async (seat, rowIdx, colIdx) => {
    if (!window.confirm(`Remove ${seat.roll_number} from this seat?`)) return;
    
    try {
      const token = getToken();
      const res = await fetch(`/api/sessions/${session.session_id}/rooms/${encodeURIComponent(selectedRoomName)}/remove-external-student`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          seat_position: seat.position
        })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.message || 'Failed to remove student');
      }
      
      // Update webData locally - mark seat as unallocated
      if (webData) {
        const newSeating = [...webData.seating];
        newSeating[rowIdx][colIdx] = {
          ...newSeating[rowIdx][colIdx],
          roll_number: null,
          student_name: null,
          batch_label: null,
          is_unallocated: true,
          is_external: false,
          color: '#F3F4F6'
        };
        setWebData({ ...webData, seating: newSeating });
      }
      
      if (showToast) showToast("External student removed", "success");
      
    } catch (e) {
      if (showToast) showToast(e.message, "error");
    }
  };

  const batchColorOptions = [
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Orange', value: '#f97316' },
    { name: 'Green', value: '#22c55e' },
    { name: 'Purple', value: '#a855f7' },
    { name: 'Pink', value: '#ec4899' },
    { name: 'Cyan', value: '#06b6d4' },
    { name: 'Yellow', value: '#eab308' },
    { name: 'Red', value: '#ef4444' }
  ];

  // ============================================================================
  // NO SESSION
  // ============================================================================

  // LOADING STATE

  if (initializing) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="relative w-20 h-20 mx-auto">
            {/* Outer ring */}
            <div className="absolute inset-0 border-4 border-orange-200 dark:border-orange-900 rounded-full"></div>
            {/* Spinning ring */}
            <div className="absolute inset-0 border-4 border-transparent border-t-orange-500 rounded-full animate-spin"></div>
            {/* Center icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center shadow-lg">
                <Layout className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
          <div>
            <p className="text-gray-900 dark:text-white font-bold text-lg">Loading Allocation</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Preparing your session...</p>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // ✅ FIXED: No Session - Only show AFTER initialization complete
  // ============================================================================
  if (!hasActiveSession && !initializing) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border-2 border-amber-400 dark:border-amber-600 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 p-6 border-b border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center">
                  <AlertTriangle className="w-7 h-7 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    No Active Session
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Start by uploading student data
                  </p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                To begin allocating seats, you need to:
              </p>
              <ol className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <span className="w-6 h-6 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center text-xs font-bold text-orange-600">1</span>
                  Upload student CSV files
                </li>
                <li className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <span className="w-6 h-6 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center text-xs font-bold text-orange-600">2</span>
                  Start an allocation session
                </li>
                <li className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <span className="w-6 h-6 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center text-xs font-bold text-orange-600">3</span>
                  Generate seating arrangements
                </li>
              </ol>

              <button
                onClick={() => navigate('/upload', { replace: true })}
                className="w-full mt-4 h-12 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg"
              >
                Go to Upload
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const validBatchIds = selectedBatchIds.filter(id => id !== null);
  const selectedBatchesForModal = uploadedBatches
    .filter(b => validBatchIds.includes(b.batch_id))
    .map(b => ({
      id: b.batch_id,
      label: b.batch_name,
      color: b.batch_color || '#3b82f6'
    }));

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

        
        {/* PROGRESS CARD - With null guards */}
          {session && (
            <Card className="p-6 border-2 border-orange-500 dark:border-orange-400">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Session Progress</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">ID: {session?.plan_id || 'N/A'}</p>
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
                  {progressPct > 5 && (
                    <span className="text-white text-xs font-bold">{progressPct}%</span>
                  )}
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
          )}

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
                    {blockStructure && Array.isArray(blockStructure) && blockStructure.length > 0 && (
                      <span className="bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 px-3 py-1.5 rounded-lg font-bold border border-purple-200 dark:border-purple-800">
                        Blocks: {blockStructure.join(':')}
                      </span>
                    )}
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
                              Total Students: <span className="font-bold">{selectedBatch.student_count}</span> | Unallocated: <span className="font-bold text-orange-600 dark:text-orange-400">{selectedBatch.student_count - (batchAllocations[selectedBatch.batch_name] || 0)}</span>
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
                  <FeatureTooltip
                    title="Fill By Columns"
                    description="Allocates students column by column, maintaining the order from your input data. Each column is completely filled before moving to the next one."
                  >
                    <span>Fill By Columns</span>
                  </FeatureTooltip>
                </label>
                <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                  <input 
                    type="checkbox" 
                    checked={randomizeColumn} 
                    onChange={e => setRandomizeColumn(e.target.checked)} 
                    className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"
                  />
                  <RefreshCw size={16} className="text-orange-500" />
                  <FeatureTooltip
                    title="Randomize Within Column"
                    description="Shuffles student positions within each column instead of maintaining sequential order. This reduces exam malpractice while keeping batch organization intact."
                  >
                    <span>Randomize Within Column</span>
                  </FeatureTooltip>
                </label>
                
                {/* Adjacent Seating Option - Only show when single batch selected */}
                {selectedBatchIds.filter(id => id !== null).length === 1 && (
                  <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                    <input 
                      type="checkbox" 
                      checked={allowAdjacentSeating} 
                      onChange={e => setAllowAdjacentSeating(e.target.checked)} 
                      className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"
                    />
                    <Users size={16} className="text-orange-500" />
                    <FeatureTooltip
                      title="Allow Adjacent Seating"
                      description="Allows students from the same batch to sit next to each other. Paper set alternation and other constraints are still enforced. Only available for single-batch allocations."
                    >
                      <span>Allow Adjacent Seating</span>
                    </FeatureTooltip>
                    <span className="text-[10px] uppercase font-black bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded">
                      Single Batch
                    </span>
                  </label>
                )}
                
                <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                  <input 
                    type="checkbox" 
                    checked={optimizeRoom} 
                    onChange={e => setOptimizeRoom(e.target.checked)} 
                    className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"
                  />
                  <div className="flex items-center gap-2">
                    <BarChart3 size={16} className="text-orange-500" />
                    <FeatureTooltip
                      title="Optimize Room"
                      description="Intelligently fills leftover empty seats in a room with students from a different batch. Creates better room utilization and reduces wasted seating capacity."
                    >
                      <span>Optimize Room</span>
                    </FeatureTooltip>
                    <span className="text-[10px] uppercase font-black bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 px-1.5 py-0.5 rounded">
                      New
                    </span>
                  </div>
                </label>
                {/* Config Button (Only show if optimized enabled) */}
                {optimizeRoom && (
                  <button
                    onClick={() => setIsOptModalOpen(true)}
                    className="ml-auto text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    Configure Chain
                  </button>
                )}
              </div>

              <div className="pt-4 border-t-2 border-gray-200 dark:border-gray-800">
                <Button onClick={handleEndSession} variant="destructive" className="w-full h-11 text-sm font-bold uppercase tracking-wide" disabled={resetting}>
                  {resetting ? <Loader2 className="animate-spin mr-2" size={16}/> : <LogOut size={16} className="mr-2"/>}
                  {resetting ? 'Ending...' : 'End Session'}
                </Button>
              </div>

              {/* ALGORITHM STATUS */}
              {webData && webData.constraints_status && (
                <ConstraintIndicator 
                  constraints={webData.constraints_status.constraints} 
                  validation={webData.validation}
                />
              )}
            </div>

            {/* BUTTONS FOOTER */}
            <div className="p-6 border-t-2 border-gray-200 dark:border-gray-800 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750 space-y-3">
              <Button 
                onClick={generate} 
                disabled={loading || pendingCount === 0 || !selectedRoomId || selectedBatchIds.filter(id => id !== null).length === 0}
                className="w-full h-14 bg-gradient-to-r from-orange-500 to-amber-500 text-white hover:from-orange-600 hover:to-amber-600 shadow-lg text-base font-black uppercase tracking-wide"
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
                  <Button 
                        onClick={() => session?.plan_id && navigate(`/attendance/${session.plan_id}?source=allocation`)} 
                        disabled={!session?.plan_id}
                        className="h-10 px-4 bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300 text-xs font-bold"
>
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
              <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-6 md:p-10 overflow-auto custom-scrollbar relative z-10 rounded-xl">
                {Array.isArray(webData.seating) && (() => {
                  // Use block_structure if available, otherwise fall back to block_width
                  const effectiveBlockStructure = webData?.metadata?.block_structure || blockStructure;
                  const bw = webData?.metadata?.block_width || blockWidth;
                  
                  // Calculate aisle positions based on block_structure or uniform block_width
                  const aisleAfterCols = new Set();
                  if (effectiveBlockStructure && Array.isArray(effectiveBlockStructure) && effectiveBlockStructure.length > 0) {
                    // Variable block widths: insert aisle after cumulative sum
                    let cumulative = 0;
                    for (let i = 0; i < effectiveBlockStructure.length - 1; i++) {
                      cumulative += effectiveBlockStructure[i];
                      aisleAfterCols.add(cumulative - 1); // Convert to 0-indexed column where aisle follows
                    }
                  } else {
                    // Uniform block_width: insert aisle every bw columns
                    for (let i = bw - 1; i < cols - 1; i += bw) {
                      aisleAfterCols.add(i);
                    }
                  }
                  
                  const columnStyles = [];
                  for(let i = 0; i < cols; i++) {
                    columnStyles.push('minmax(160px, 1fr)');
                    if (aisleAfterCols.has(i)) {
                      columnStyles.push('40px'); // Aisle gap
                    }
                  }
                  
                  return (
                    <div className="grid gap-3 mx-auto" style={{ gridTemplateColumns: columnStyles.join(' '), width: 'fit-content' }}>
                      {webData.seating.map((row, rIdx) => 
                        Array.isArray(row) && row.map((seat, cIdx) => (
                          <React.Fragment key={`${rIdx}-${cIdx}`}>
                            {(() => {
                              const seatIndex = rIdx * cols + cIdx + 1;
                              const isBroken = seat?.is_broken;
                              const isAllocated = !isBroken && !seat?.is_unallocated;
                              const isExternal = seat?.is_external;
                              const deskRow = rIdx + 1;
                              const deskCol = cIdx + 1;
                              const isEmpty = !isBroken && seat?.is_unallocated;
                              
                              return (
                                <motion.div
                                  initial={{ opacity: 0, scale: 0.85, y: 20 }}
                                  animate={{ opacity: 1, scale: 1, y: 0 }}
                                  transition={{ delay: (rIdx * cols + cIdx) * 0.003, type: "spring", stiffness: 300, damping: 24 }}
                                  onClick={() => {
                                    if (isEmpty) {
                                      handleEmptySeatClick(seat, rIdx, cIdx);
                                    }
                                  }}
                                  className={`relative flex flex-col items-center justify-between p-4 transition-all duration-200 border-2 rounded-xl bg-white dark:bg-gray-900 shadow-sm min-h-[140px] w-full group cursor-pointer ${
                                    isBroken 
                                      ? 'border-red-200 bg-red-50/20 dark:bg-red-900/10' 
                                      : isAllocated 
                                        ? `border-gray-200 dark:border-gray-800 hover:border-orange-400 hover:scale-[1.02] ${isExternal ? 'ring-2 ring-purple-400 ring-offset-2 dark:ring-offset-gray-900' : ''}` 
                                        : 'border-dashed border-gray-300 dark:border-gray-700 hover:border-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 opacity-60 hover:opacity-100'
                                  }`}
                                >
                                  {isAllocated && (
                                    <div className="absolute top-0 inset-x-0 h-1.5 rounded-t-xl" style={{ backgroundColor: seat.color }} />
                                  )}
                                  {/* External student indicator badge */}
                                  {isExternal && (
                                    <div className="absolute -top-2 -right-2 bg-purple-500 text-white text-[8px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-wider shadow-lg">
                                      Manual
                                    </div>
                                  )}
                                  {isAllocated ? (
                                    <>
                                      <div className="flex items-center justify-between w-full">
                                        <span className="text-[11px] font-extrabold text-gray-400 dark:text-gray-500 uppercase tracking-tighter">
                                          {seat.batch_label || `B-${seat.batch}`}
                                        </span>
                                        {/* Remove button for external students */}
                                        {isExternal && (
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleRemoveExternalStudent(seat, rIdx, cIdx);
                                            }}
                                            className="p-1 rounded-full bg-red-100 dark:bg-red-900/30 text-red-500 hover:bg-red-200 dark:hover:bg-red-800/50 transition-colors"
                                            title="Remove external student"
                                          >
                                            <X size={12} />
                                          </button>
                                        )}
                                      </div>
                                      <span className="text-lg font-black text-gray-900 dark:text-white leading-tight my-3 group-hover:text-orange-600 transition-colors text-center whitespace-nowrap w-full px-1">
                                        {seat.roll_number}
                                      </span>
                                      {seat.student_name && (
                                        <span className="text-[10px] text-gray-500 dark:text-gray-400 truncate w-full text-center mb-1">
                                          {seat.student_name}
                                        </span>
                                      )}
                                      <div className="w-full flex justify-between items-center gap-1.5 pt-2 border-t border-gray-100 dark:border-gray-800 mt-auto">
                                        <div className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                                          <span className="text-xs font-mono font-extrabold text-gray-600 dark:text-gray-400 uppercase">SET: {seat.paper_set || 'A'}</span>
                                        </div>
                                        <div className="px-1.5 py-0.5 rounded bg-orange-50 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-700">
                                          <span className="text-[10px] font-mono font-bold text-orange-600 dark:text-orange-400">
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
                                    <div className="flex flex-col items-center justify-center h-full gap-2">
                                      <UserPlus className="w-6 h-6 text-gray-300 dark:text-gray-600 group-hover:text-orange-500 transition-colors" />
                                      <span className="text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase group-hover:text-orange-600">Click to Add</span>
                                      <span className="text-xs font-mono text-gray-300 dark:text-gray-700">{deskRow}-{deskCol}</span>
                                    </div>
                                  )}
                                </motion.div>
                              );
                            })()}
                            {aisleAfterCols.has(cIdx) && <div key={`spacer-${rIdx}-${cIdx}`} className="w-10" />}
                          </React.Fragment>
                        ))
                      )}
                    </div>
                  );
                })()}
              </div>
            )}
          </Card>
        </div>
      </div>
      
      {/* External Student Modal */}
      <AnimatePresence>
        {showExternalModal && selectedEmptySeat && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowExternalModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="glass-card bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl shadow-lg">
                    <UserPlus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-black text-gray-900 dark:text-white uppercase tracking-tight">
                      Add External Student
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                      Seat {selectedEmptySeat.position} in Room {selectedRoomName}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowExternalModal(false)}
                  className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* Form */}
              <div className="space-y-4">
                {/* Roll Number */}
                <div>
                  <label className="block text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Roll Number *
                  </label>
                  <Input
                    value={externalStudent.roll_number}
                    onChange={(e) => setExternalStudent({ ...externalStudent, roll_number: e.target.value.toUpperCase() })}
                    placeholder="e.g., BTCS2401099"
                    className="font-mono"
                  />
                </div>

                {/* Student Name */}
                <div>
                  <label className="block text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Student Name (Optional)
                  </label>
                  <Input
                    value={externalStudent.student_name}
                    onChange={(e) => setExternalStudent({ ...externalStudent, student_name: e.target.value })}
                    placeholder="e.g., John Doe"
                  />
                </div>

                {/* Batch Selection */}
                <div>
                  <label className="block text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Batch *
                  </label>
                  {!showNewBatchInput ? (
                    <div className="space-y-2">
                      <select
                        value={externalStudent.batch_label}
                        onChange={(e) => {
                          if (e.target.value === '__NEW__') {
                            setShowNewBatchInput(true);
                            setExternalStudent({ ...externalStudent, batch_label: '', batch_color: '#3b82f6' });
                          } else {
                            const selected = roomBatches.find(b => b.label === e.target.value);
                            setExternalStudent({ 
                              ...externalStudent, 
                              batch_label: e.target.value,
                              batch_color: selected?.color || '#3b82f6'
                            });
                          }
                        }}
                        className="flex h-10 w-full rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 dark:text-white"
                      >
                        <option value="">Select batch...</option>
                        {roomBatches.map((batch) => (
                          <option key={batch.label} value={batch.label}>
                            {batch.label}
                          </option>
                        ))}
                        <option value="__NEW__">+ Add New Batch</option>
                      </select>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex gap-2">
                        <Input
                          value={externalStudent.batch_label}
                          onChange={(e) => setExternalStudent({ ...externalStudent, batch_label: e.target.value.toUpperCase() })}
                          placeholder="e.g., CSE, ECE, MAC"
                          className="flex-1"
                        />
                        <button
                          onClick={() => {
                            setShowNewBatchInput(false);
                            setExternalStudent({ ...externalStudent, batch_label: roomBatches[0]?.label || '', batch_color: roomBatches[0]?.color || '#3b82f6' });
                          }}
                          className="px-3 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-bold"
                        >
                          Cancel
                        </button>
                      </div>
                      
                      {/* Color Picker */}
                      <div>
                        <label className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                          <Palette size={12} /> Batch Color
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {batchColorOptions.map((color) => (
                            <button
                              key={color.value}
                              onClick={() => setExternalStudent({ ...externalStudent, batch_color: color.value })}
                              className={`w-8 h-8 rounded-lg transition-all ${
                                externalStudent.batch_color === color.value 
                                  ? 'ring-2 ring-offset-2 ring-gray-400 dark:ring-offset-gray-900 scale-110' 
                                  : 'hover:scale-105'
                              }`}
                              style={{ backgroundColor: color.value }}
                              title={color.name}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Paper Set Info */}
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
                  <div className="flex items-start gap-2">
                    <Info className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                    <p className="text-xs text-blue-700 dark:text-blue-300 font-medium">
                      Paper set will be automatically calculated based on adjacent seats to ensure proper alternation.
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => setShowExternalModal(false)}
                  variant="outline"
                  className="flex-1 h-12 text-sm"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAddExternalStudent}
                  disabled={addingExternal || !externalStudent.roll_number || !externalStudent.batch_label}
                  className="flex-1 h-12 bg-gradient-to-r from-purple-500 to-indigo-500 text-white hover:from-purple-600 hover:to-indigo-600 text-sm"
                >
                  {addingExternal ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Student
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar{width:8px;height:8px}
        .custom-scrollbar::-webkit-scrollbar-track{background:transparent}
        .custom-scrollbar::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:10px}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#9ca3af}
        .dark .custom-scrollbar::-webkit-scrollbar-thumb{background:#4b5563}
        .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#6b7280}
      `}</style>
      <OptimizationConfigModal
        isOpen={isOptModalOpen}
        onClose={() => setIsOptModalOpen(false)}
        selectedBatches={selectedBatchesForModal}
        allBatches={uploadedBatches} // <--- Pass all batches
        onSaveSuccessors={(successors) => {
          setBatchSuccessors(successors);
          showToast('success', 'Optimization chain saved!');
        }}
        initialSuccessors={batchSuccessors}
      />
    </div>
  );
};

export default AllocationPage;