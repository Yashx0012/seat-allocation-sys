import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UserCheck, Printer, Eye, X, Loader2, 
  BookOpen, Hash, Calendar, Clock, ChevronRight, FileDown 
} from 'lucide-react';

const AttendancePage = ({ showToast }) => {
  const { planId } = useParams(); 
  const navigate = useNavigate();

  const [batchGroups, setBatchGroups] = useState({});
  const [roomName, setRoomName] = useState("");
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
  }, [planId]);

  const fetchBatchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/plan-batches/${planId}`);
      if (!response.ok) throw new Error("Could not load plan data. Ensure you generated a plan first.");
      
      const data = await response.json();
      // Ensure we set an empty object if batches is null/undefined to prevent mapping errors
      setBatchGroups(data?.batches || {});
      setRoomName(data?.room_name || "N/A");
      
      if (showToast) showToast("Attendance data loaded", "success");
    } catch (err) {
      if (showToast) showToast(err.message, "error");
      setTimeout(() => navigate('/allocation'), 2000);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadSingle = async (batchLabel) => {
    if (!metadata.course_name || !metadata.course_code) {
      if (showToast) showToast("Please enter Course Name and Code", "warning");
      return;
    }

    setActionLoading(batchLabel);
    try {
      const response = await fetch('/api/export-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: planId,
          batch_name: batchLabel,
          metadata: { ...metadata, room_no: roomName }
        }),
      });

      if (!response.ok) throw new Error("Failed to generate PDF");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Attendance_${batchLabel}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
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
            <p className="text-gray-500 mt-1 font-medium">Room: <span className="text-orange-500 font-bold">{roomName}</span></p>
          </div>
          <button 
            onClick={() => navigate('/allocation')}
            className="text-sm font-bold text-gray-500 hover:text-orange-500 transition-colors"
          >
            ← Back to Allocation
          </button>
        </div>

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
              <label className="text-[10px] font-bold uppercase text-gray-400 ml-1">Course Name</label>
              <input 
                placeholder="Course Name"
                className="w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 dark:text-white focus:border-orange-500 outline-none transition-all"
                value={metadata.course_name}
                onChange={e => setMetadata({...metadata, course_name: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase text-gray-400 ml-1">Course Code</label>
              <input 
                placeholder="Course Code"
                className="w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 dark:text-white focus:border-orange-500 outline-none transition-all"
                value={metadata.course_code}
                onChange={e => setMetadata({...metadata, course_code: e.target.value})}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
             <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
               <Calendar size={18} className="text-orange-500"/>
               <input type="date" value={metadata.date} onChange={e => setMetadata({...metadata, date: e.target.value})} className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"/>
             </div>
             <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
               <Clock size={18} className="text-orange-500"/>
               <input value={metadata.time} onChange={e => setMetadata({...metadata, time: e.target.value})} className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"/>
             </div>
             <div className="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 p-3 rounded-xl border-2 border-gray-100 dark:border-gray-700">
               <Hash size={18} className="text-orange-500"/>
               <input value={metadata.year} onChange={e => setMetadata({...metadata, year: e.target.value})} className="bg-transparent dark:text-white outline-none text-sm font-bold w-full"/>
             </div>
          </div>
        </div>

        {/* Batch List */}
        <div className="space-y-4">
          <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.2em] ml-1">Step 2: Export by Batch</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(batchGroups).map(([label, data]) => (
              <motion.div 
                key={label}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-3xl border-2 border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-xl transition-all"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      {/* FIXED: Added Optional Chaining here */}
                      <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-full text-[10px] font-black uppercase tracking-wider">
                        {data?.info?.degree || "N/A"}
                      </span>
                      <h3 className="text-xl font-black dark:text-white mt-2">{label}</h3>
                    </div>
                    <button onClick={() => handlePreview(label)} className="p-2 text-gray-400 hover:text-orange-500 transition-colors">
                      <Eye size={20} />
                    </button>
                  </div>
                  
                  <div className="space-y-1 mb-6">
                    {/* FIXED: Added Optional Chaining here */}
                    <p className="text-xs text-gray-500 font-medium italic">{data?.info?.branch || "General"}</p>
                    <p className="text-sm font-bold dark:text-gray-300">{data?.students?.length || 0} Students</p>
                  </div>

                  <button 
                    onClick={() => handleDownloadSingle(label)}
                    disabled={actionLoading === label}
                    className="w-full py-4 bg-gray-900 dark:bg-orange-500 text-white rounded-2xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-2 hover:bg-orange-500 dark:hover:bg-orange-600 transition-all disabled:opacity-50"
                  >
                    {actionLoading === label ? <Loader2 className="animate-spin" size={16}/> : <FileDown size={16}/>}
                    Download PDF
                  </button>
                </div>
              </motion.div>
            ))}
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
                <h3 className="font-black dark:text-white uppercase">{previewData.label} Student List</h3>
                <button onClick={() => setPreviewData(null)} className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-all">
                  <X size={20} className="dark:text-white"/>
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-[10px] font-black text-gray-400 uppercase border-b dark:border-gray-700">
                      <th className="pb-3 px-2">Roll No</th>
                      <th className="pb-3">Student Name</th>
                      <th className="pb-3 text-right">Set</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y dark:divide-gray-700">
                    {(previewData.students || []).map((s, i) => (
                      <tr key={i} className="text-sm dark:text-gray-300">
                        <td className="py-3 px-2 font-mono font-bold text-orange-500">{s.roll_number}</td>
                        <td className="py-3 font-medium">{s.student_name}</td>
                        <td className="py-3 text-right font-black text-gray-400">{s.paper_set}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <style>{`.custom-scrollbar::-webkit-scrollbar{width:6px}.custom-scrollbar::-webkit-scrollbar-thumb{background:#f97316;border-radius:10px}`}</style>
    </div>
  );
};

export default AttendancePage;