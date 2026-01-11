import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UserCheck, Eye, X, Loader2, 
  BookOpen, Hash, Calendar, Clock, FileDown, Building2, ArrowLeft, Users
} from 'lucide-react';

const AttendancePage = ({ showToast }) => {
  const { planId } = useParams(); 
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const roomFromUrl = searchParams.get('room');

  const [batchGroups, setBatchGroups] = useState({});
  const [roomName, setRoomName] = useState(roomFromUrl || "");
  const [allRooms, setAllRooms] = useState([]);
  const [roomsData, setRoomsData] = useState({}); // Store all rooms data for stats
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  
  const [metadata, setMetadata] = useState({
    exam_title: "SESSIONAL EXAMINATION",
    course_name: "",
    course_code: "",
    date: new Date().toISOString().split('T')[0],
    time: "10:00 AM - 12:00 PM",
    year: new Date().getFullYear().toString()
  });

  useEffect(() => {
    if (planId) {
      fetchBatchData();
    }
  }, [planId, roomFromUrl]);

  const fetchBatchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/plan-batches/${planId}`);
      if (!response.ok) throw new Error("Could not load plan data.");
      
      const data = await response.json();

      // Store all rooms data
      const rooms = data?.rooms || {};
      setRoomsData(rooms);

      // Store all available rooms
      const availableRooms = Object.keys(rooms);
      setAllRooms(availableRooms);

      // Determine which room to display
      let targetRoom = roomFromUrl;
      
      if (!targetRoom && data?.metadata?.room_no) {
        targetRoom = data.metadata.room_no;
      }
      
      if (!targetRoom && data?.inputs?.room_no) {
        targetRoom = data.inputs.room_no;
      }

      if (!targetRoom && availableRooms.length > 0) {
        targetRoom = availableRooms[0];
      }

      // Extract batches for target room
      let extractedBatches = {};
      
      if (rooms[targetRoom]) {
        extractedBatches = rooms[targetRoom].batches || {};
      } else if (data?.batches) {
        extractedBatches = data.batches;
      }

      setRoomName(targetRoom || "N/A");
      setBatchGroups(extractedBatches);

      if (showToast) {
        if (Object.keys(extractedBatches).length > 0) {
          showToast(`Loaded data for Room: ${targetRoom}`, "success");
        } else {
          showToast("No batch data found in this plan.", "warning");
        }
      }
    } catch (err) {
      console.error("Fetch error:", err);
      if (showToast) showToast("Error: " + err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const switchRoom = (newRoom) => {
    navigate(`/attendance/${planId}?room=${encodeURIComponent(newRoom)}`);
  };

  // ✅ FIXED: Build complete metadata for API
  // ✅ FIXED: Build metadata with EXACT field names that backend/PDF expects
const buildCompleteMetadata = () => {
  return {
    // ✅ Use 'exam_title' (not 'exam_name') - this is what PDF expects
    exam_title: metadata.exam_title,
    
    // ✅ Use 'course_name' - this is what PDF expects
    course_name: metadata.course_name,
    
    // ✅ Use 'course_code' - this is what PDF expects
    course_code: metadata.course_code,
    
    // ✅ Use 'date' (not 'exam_date') - this is what PDF expects
    date: metadata.date,
    
    // ✅ Use 'time' - this is what PDF expects
    time: metadata.time,
    
    // ✅ Use 'year' - this is what PDF expects
    year: metadata.year,
    
    // Room info
    room_no: roomName,
    room_name: roomName,
    
    // Plan info
    plan_id: planId
  };
};

  const handleDownloadSingle = async (batchLabel) => {
    if (!metadata.course_name || !metadata.course_code) {
      if (showToast) showToast("Please enter Course Name and Code", "warning");
      return;
    }

    setActionLoading(batchLabel);
    try {
      const token = localStorage.getItem('token');
      const completeMetadata = buildCompleteMetadata();
      
      console.log('📤 Sending batch download request:', { batchLabel, metadata: completeMetadata });

      const response = await fetch('/api/export-attendance', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          plan_id: planId,
          batch_name: batchLabel,
          metadata: completeMetadata
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to generate PDF");
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error("Empty PDF received");
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Attendance_${roomName}_${batchLabel}_${metadata.course_code}_${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast(`✅ Attendance for ${batchLabel} downloaded`, "success");
    } catch (err) {
      console.error("Download error:", err);
      if (showToast) showToast(err.message, "error");
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownloadRoom = async () => {
    if (!metadata.course_name || !metadata.course_code) {
      if (showToast) showToast("Please enter Course Name and Code", "warning");
      return;
    }

    setActionLoading('room');
    try {
      const token = localStorage.getItem('token');
      const completeMetadata = buildCompleteMetadata();
      
      console.log('📤 Sending room download request:', { roomName, metadata: completeMetadata });

      const response = await fetch('/api/export-attendance', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          plan_id: planId,
          batch_name: roomName,
          metadata: completeMetadata
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to generate PDF");
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error("Empty PDF received");
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Attendance_${roomName}_Complete_${metadata.course_code}_${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      if (showToast) showToast(`✅ Complete attendance for ${roomName} downloaded`, "success");
    } catch (err) {
      console.error("Download error:", err);
      if (showToast) showToast(err.message, "error");
    } finally {
      setActionLoading(null);
    }
  };

  const handlePreview = (batchLabel) => {
    const batch = batchGroups[batchLabel];
    if (!batch) return;
    
    setPreviewData({
      label: batchLabel,
      students: batch.students || [],
      info: batch.info || {}
    });
  };

  // ✅ FIXED: Calculate total students from actual batch data
  const totalStudents = Object.values(batchGroups).reduce(
    (sum, batch) => sum + (batch?.students?.length || 0), 
    0
  );

  // ✅ FIXED: Calculate room capacity from matrix if available
  const getRoomCapacity = () => {
    const currentRoomData = roomsData[roomName];
    if (!currentRoomData) return 0;
    
    const matrix = currentRoomData.raw_matrix || currentRoomData.matrix;
    if (matrix && matrix.length > 0) {
      return matrix.length * (matrix[0]?.length || 0);
    }
    
    const inputs = currentRoomData.inputs;
    if (inputs) {
      return (inputs.rows || 0) * (inputs.cols || 0);
    }
    
    return 0;
  };

  const roomCapacity = getRoomCapacity();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#050505]">
        <Loader2 className="animate-spin text-orange-500 w-12 h-12 mb-4" />
        <p className="text-gray-500 font-bold uppercase tracking-widest">Reading Cache...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 dark:border-gray-800 pb-8">
          <div>
            <h1 className="text-4xl font-black text-gray-900 dark:text-white uppercase tracking-tighter flex items-center gap-3">
              <UserCheck className="text-orange-500" size={36} />
              Attendance Control
            </h1>
            <div className="flex items-center gap-4 mt-2 flex-wrap">
              <p className="text-gray-500 font-medium">
                Plan: <span className="text-orange-500 font-bold">{planId}</span>
              </p>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <p className="text-gray-500 font-medium">
                Room: <span className="text-emerald-500 font-bold">{roomName}</span>
              </p>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <p className="text-gray-500 font-medium">
                Students: <span className="text-blue-500 font-bold">{totalStudents}</span>
                {roomCapacity > 0 && (
                  <span className="text-gray-400"> / {roomCapacity} capacity</span>
                )}
              </p>
            </div>
          </div>
          <button 
            onClick={() => navigate('/create-plan')}
            className="text-sm font-bold text-gray-500 hover:text-orange-500 transition-colors flex items-center gap-2"
          >
            <ArrowLeft size={16} />
            Back to Plans
          </button>
        </div>

        {/* Room Selector (if multiple rooms) */}
        {allRooms.length > 1 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-gray-100 dark:border-gray-700">
            <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <Building2 size={16}/> Select Room
            </h2>
            <div className="flex flex-wrap gap-3">
              {allRooms.map((room) => {
                // ✅ FIXED: Calculate actual student count per room
                const roomBatches = roomsData[room]?.batches || {};
                const roomStudentCount = Object.values(roomBatches).reduce(
                  (sum, batch) => sum + (batch?.students?.length || 0), 0
                );
                
                return (
                  <button
                    key={room}
                    onClick={() => switchRoom(room)}
                    className={`px-4 py-2 rounded-xl font-bold text-sm transition-all flex items-center gap-2 ${
                      room === roomName
                        ? 'bg-orange-500 text-white shadow-lg'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-orange-100 dark:hover:bg-orange-900/30'
                    }`}
                  >
                    {room}
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      room === roomName
                        ? 'bg-white/20 text-white'
                        : 'bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400'
                    }`}>
                      {roomStudentCount}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Metadata Form */}
        <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 border-2 border-gray-100 dark:border-gray-700 shadow-xl">
          <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
            <BookOpen size={16}/> Step 1: Enter Exam Details
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase text-gray-400 ml-1">Exam Title</label>
              <input 
                className="w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 dark:text-white focus:border-orange-500 outline-none transition-all"
                value={metadata.exam_title}
                onChange={e => setMetadata({...metadata, exam_title: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase text-gray-400 ml-1">Course Name / Department *</label>
              <input 
                placeholder="e.g., Computer Science"
                className="w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 dark:text-white focus:border-orange-500 outline-none transition-all"
                value={metadata.course_name}
                onChange={e => setMetadata({...metadata, course_name: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase text-gray-400 ml-1">Course Code *</label>
              <input 
                placeholder="e.g., CS-101"
                className="w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 dark:text-white focus:border-orange-500 outline-none transition-all"
                value={metadata.course_code}
                onChange={e => setMetadata({...metadata, course_code: e.target.value})}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
              <Calendar size={18} className="text-orange-500"/>
              <input 
                type="date" 
                value={metadata.date} 
                onChange={e => setMetadata({...metadata, date: e.target.value})} 
                className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"
              />
            </div>
            <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
              <Clock size={18} className="text-orange-500"/>
              <input 
                value={metadata.time} 
                onChange={e => setMetadata({...metadata, time: e.target.value})} 
                className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"
                placeholder="10:00 AM - 12:00 PM"
              />
            </div>
            <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
              <Hash size={18} className="text-orange-500"/>
              <input 
                value={metadata.year} 
                onChange={e => setMetadata({...metadata, year: e.target.value})} 
                className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"
                placeholder="2025"
              />
            </div>
          </div>
        </div>

        {/* Download All Button */}
        {Object.keys(batchGroups).length > 0 && (
          <button
            onClick={handleDownloadRoom}
            disabled={actionLoading === 'room' || !metadata.course_name || !metadata.course_code}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white rounded-2xl font-black uppercase tracking-widest text-sm flex items-center justify-center gap-3 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {actionLoading === 'room' ? (
              <Loader2 className="animate-spin" size={20}/>
            ) : (
              <FileDown size={20}/>
            )}
            Download Complete Attendance for {roomName} ({totalStudents} students)
          </button>
        )}

        {/* Batch List */}
        <div className="space-y-4">
          <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.2em] ml-1">Step 2: Export by Batch</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(batchGroups).length > 0 ? (
              Object.entries(batchGroups).map(([label, data]) => {
                // ✅ FIXED: Get actual student count from data
                const studentCount = data?.students?.length || 0;
                
                return (
                  <motion.div 
                    key={label}
                    whileHover={{ y: -5 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl border-2 border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-xl transition-all"
                  >
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-full text-[10px] font-black uppercase tracking-wider">
                            {data?.info?.degree || "N/A"}
                          </span>
                          <h3 className="text-xl font-black dark:text-white mt-2">{label}</h3>
                        </div>
                        <button 
                          onClick={() => handlePreview(label)} 
                          className="p-2 text-gray-400 hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                          title="Preview students"
                        >
                          <Eye size={20} />
                        </button>
                      </div>
                      
                      <div className="space-y-1 mb-6">
                        <p className="text-xs text-gray-500 font-medium italic">
                          {data?.info?.branch || "General"}
                        </p>
                        {/* ✅ FIXED: Display actual student count */}
                        <div className="flex items-center gap-2">
                          <Users size={14} className="text-blue-500" />
                          <p className="text-sm font-bold dark:text-gray-300">
                            {studentCount} Students
                          </p>
                        </div>
                      </div>

                      <button 
                        onClick={() => handleDownloadSingle(label)}
                        disabled={actionLoading === label || !metadata.course_name || !metadata.course_code}
                        className="w-full py-4 bg-gray-900 dark:bg-orange-500 text-white rounded-2xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-2 hover:bg-orange-500 dark:hover:bg-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {actionLoading === label ? (
                          <Loader2 className="animate-spin" size={16}/>
                        ) : (
                          <FileDown size={16}/>
                        )}
                        Download PDF
                      </button>
                    </div>
                  </motion.div>
                );
              })
            ) : (
              <div className="col-span-full py-12 text-center bg-gray-100 dark:bg-gray-900 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-800">
                <p className="text-gray-400 font-bold uppercase tracking-widest">No batches found for this room</p>
                <p className="text-gray-400 text-sm mt-2">Try selecting a different room above</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {previewData && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-md">
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-3xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col shadow-2xl"
            >
              <div className="p-6 border-b dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900">
                <div>
                  <h3 className="font-black dark:text-white uppercase">{previewData.label}</h3>
                  <p className="text-sm text-gray-500">{previewData.students.length} students</p>
                </div>
                <button 
                  onClick={() => setPreviewData(null)} 
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-all"
                >
                  <X size={20} className="dark:text-white"/>
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-[10px] font-black text-gray-400 uppercase border-b dark:border-gray-700">
                      <th className="pb-3 px-2">#</th>
                      <th className="pb-3">Enrollment</th>
                      <th className="pb-3">Student Name</th>
                      <th className="pb-3 text-right">Set</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y dark:divide-gray-700">
                    {(previewData.students || []).map((s, i) => (
                      <tr key={i} className="text-sm dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-2 text-gray-400">{i + 1}</td>
                        <td className="py-3 font-mono font-bold text-orange-500">
                          {s.roll_number || s.enrollment || s.enrollment_no || 'N/A'}
                        </td>
                        <td className="py-3 font-medium">
                          {s.student_name || s.name || 'N/A'}
                        </td>
                        <td className="py-3 text-right font-black text-gray-400">
                          {s.paper_set || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #f97316; border-radius: 10px; }
      `}</style>
    </div>
  );
};

export default AttendancePage;