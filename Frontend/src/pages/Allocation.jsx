import React, { useState, useEffect, useRef } from 'react';
import SplitText from '../components/SplitText';
import { motion, AnimatePresence } from "framer-motion";
import { 
  Users, Layout, MapPin, Download, Play, 
  Settings, Monitor, Palette, Hash, Type, 
  Loader2, AlertCircle, RefreshCw, CheckCircle2,
  Database, ChevronRight, FileDown, Zap, Trash2, Flame, Building
} from 'lucide-react';

// --- INLINE UI COMPONENTS ---
const Card = ({ className, children }) => <div className={`glass-card ${className}`}>{children}</div>;
const Button = ({ className, children, onClick, disabled, title, variant }) => {
    const base = "inline-flex items-center justify-center rounded-xl font-bold transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none hover:scale-105";
    const bg = variant === "destructive" 
      ? "bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50 border-2 border-red-200 dark:border-red-800" 
      : className.includes('bg-') ? "" : "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-white";
    return <button onClick={onClick} disabled={disabled} title={title} className={`${base} ${bg} ${className}`}>{children}</button>
};
const Input = (props) => <input {...props} className={`flex h-10 w-full rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 dark:focus:ring-orange-400 focus:border-orange-500 dark:text-white ${props.className}`} />;

const AllocationPage = ({ showToast }) => {
  const [classrooms, setClassrooms] = useState([]);
  const [selectedRoomId, setSelectedRoomId] = useState("");
  const [rows, setRows] = useState(8);
  const [cols, setCols] = useState(10);
  const [blockWidth, setBlockWidth] = useState(2);
  const [brokenSeats, setBrokenSeats] = useState("");
  const [numBatches, setNumBatches] = useState(2);
  const [batchConfigs, setBatchConfigs] = useState([
    { id: 1, label: 'Batch A', startRoll: '101', color: '#f97316' },
    { id: 2, label: 'Batch B', startRoll: '201', color: '#ef4444' }
  ]);
  const [useDemoDb, setUseDemoDb] = useState(true);
  const [batchByColumn, setBatchByColumn] = useState(true);
  const [enforceNoAdjacentBatches, setEnforceNoAdjacentBatches] = useState(false);
  const [loading, setLoading] = useState(false);
  const [webData, setWebData] = useState(null);
  const [error, setError] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const chartRef = useRef();

  useEffect(() => {
    fetch('http://localhost:5000/api/classrooms')
      .then(res => res.json())
      .then(data => setClassrooms(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const count = parseInt(numBatches) || 1;
    setBatchConfigs(prev => {
      const news = [...prev];
      if (count > prev.length) {
         const newBatches = [];
         for(let i = prev.length; i < count; i++) newBatches.push({ id: i+1, label: `Batch ${String.fromCharCode(65+i)}`, startRoll: `${(i+1)*100+1}`, color: '#'+Math.floor(Math.random()*16777215).toString(16).padStart(6, '0') });
         return [...prev, ...newBatches];
      }
      return prev.slice(0, count);
    });
  }, [numBatches]);

  const handleRoomChange = (roomId) => {
    setSelectedRoomId(roomId);
    if (!roomId) return;
    const room = classrooms.find(r => r.id === parseInt(roomId));
    if (room) {
      setRows(room.rows); setCols(room.cols); setBrokenSeats(room.broken_seats || ""); setBlockWidth(room.block_width || 1);
      if(showToast) showToast(`Loaded ${room.name}`, "success");
    }
  };

  const updateBatch = (i, f, v) => {
    const u = [...batchConfigs]; u[i][f] = v; setBatchConfigs(u);
  };

  const preparePayload = () => {
    const startRolls = {}, batchLabels = {}, batchColors = {};
    batchConfigs.forEach((b, i) => { startRolls[i+1] = b.startRoll; batchLabels[i+1] = b.label; batchColors[i+1] = b.color; });
    return {
      room_id: selectedRoomId, rows, cols, block_width: blockWidth, broken_seats: brokenSeats,
      num_batches: numBatches, batch_by_column: batchByColumn, enforce_no_adjacent_batches: enforceNoAdjacentBatches,
      use_demo_db: useDemoDb, start_rolls: startRolls, batch_labels: batchLabels, batch_colors: batchColors
    };
  };

  const generate = async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch("http://localhost:5000/api/generate-seating", { 
        method: "POST", headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify(preparePayload()) 
      });
      const data = await res.json();
      if(!res.ok) throw new Error(data.error);
      setWebData(data);
      setTimeout(() => chartRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (e) { if(showToast) showToast(e.message, "error"); } 
    finally { setLoading(false); }
  };

  const showConstraints = async () => {
    try {
        const res = await fetch("http://localhost:5000/api/constraints-status", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(preparePayload()) });
        const data = await res.json();
        const body = data.constraints ? data.constraints.map(c => `${c.satisfied ? '✅' : '❌'} ${c.name}`).join("\n") : "No constraints data";
        alert(`Constraints:\n\n${body}`);
    } catch (e) { alert("Error checking constraints"); }
  };

  const handleResetDatabase = async () => {
    if (!window.confirm("⚠️ DANGER: Delete ALL student data?")) return;
    setResetting(true);
    try {
        const token = localStorage.getItem('token');
        const res = await fetch("http://localhost:5000/api/reset-data", { method: "POST", headers: token ? { 'Authorization': `Bearer ${token}` } : {} });
        if (res.ok) { if (showToast) showToast("Database cleared", "success"); setWebData(null); }
    } catch (e) { alert(e.message); } finally { setResetting(false); }
  };

  const downloadPdf = async (type) => {
    if(!webData) { if(showToast) showToast("Generate first", "error"); return; }
    setPdfLoading(true);
    
    if(type==='client') {
       if(!window.html2pdf) { alert("html2pdf missing"); setPdfLoading(false); return; }
       const container = document.createElement("div");
       container.style.cssText = "width:1100px; padding:40px; background:#fff; color:#000; font-family:Arial,sans-serif;";
       const title = document.createElement("h1"); title.innerText = "Seating Plan"; title.style.textAlign = "center";
       container.appendChild(title);
       const info = document.createElement("div"); 
       info.innerText = `Room: ${classrooms.find(r=>r.id===parseInt(selectedRoomId))?.name || 'Manual'} | Date: ${new Date().toLocaleDateString()}`;
       info.style.textAlign = "center"; info.style.marginBottom = "20px";
       container.appendChild(info);
       const grid = document.createElement("div");
       grid.style.cssText = `display:grid; grid-template-columns:repeat(${cols}, 1fr); gap:4px; border:2px solid #000; padding:10px;`;
       webData.seating.flat().forEach(seat => {
          const el = document.createElement("div");
          el.style.cssText = `border:1px solid #ccc; min-height:60px; display:flex; flex-direction:column; align-items:center; justify-content:center; background-color:${seat.color||'#fff'}; -webkit-print-color-adjust:exact;`;
          if (seat.is_broken) { el.style.backgroundColor="#fee2e2"; el.innerHTML = `<b style='color:red'>X</b>`; }
          else if (!seat.is_unallocated) { el.innerHTML = `<div style='font-weight:bold;font-size:12px'>${seat.roll_number}</div><div style='font-size:9px'>Set ${seat.paper_set}</div>`; }
          grid.appendChild(el);
       });
       container.appendChild(grid);
       container.style.position='fixed'; container.style.left='-10000px'; container.style.top='0';
       document.body.appendChild(container);
       const opt = { margin: 10, filename: `seating_${Date.now()}.pdf`, image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2 }, jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' } };
       setTimeout(() => {
           window.html2pdf().set(opt).from(container).save().then(() => { document.body.removeChild(container); setPdfLoading(false); });
       }, 500);
    } else {
       try {
         const payload = { ...preparePayload(), seating: webData.seating, metadata: webData.metadata };
         const res = await fetch('http://localhost:5000/api/generate-pdf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
         if (!res.ok) throw new Error('Server failed');
         const blob = await res.blob();
         const url = window.URL.createObjectURL(blob);
         const a = document.createElement('a'); a.href = url; a.download = 'seating_hq.pdf'; a.click();
         window.URL.revokeObjectURL(url);
       } catch(e) { alert(e.message); } finally { setPdfLoading(false); }
    }
  };

  const renderSeat = (seat, rIdx, cIdx) => (
    <motion.div 
      initial={{ scale: 0, opacity: 0 }} 
      animate={{ scale: 1, opacity: 1 }} 
      transition={{ delay: (rIdx*cols+cIdx)*0.002, type: "spring", stiffness: 300 }} 
      key={`${rIdx}-${cIdx}`} 
      className={`aspect-square rounded-xl border-2 flex flex-col items-center justify-center p-0.5 shadow-md transition-all hover:scale-110 hover:shadow-xl z-10 relative cursor-pointer ${
        seat.is_broken ? 'bg-red-50 dark:bg-red-900/20 border-red-500 dark:border-red-600 text-red-500' :
        seat.is_unallocated ? 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-300' :
        'bg-white dark:bg-gray-700 border-transparent text-white shadow-lg'
      }`}
      style={!seat.is_broken && !seat.is_unallocated ? { 
        backgroundColor: seat.color,
        boxShadow: `0 4px 6px -1px ${seat.color}40`
      } : {}}
      title={!seat.is_unallocated ? `Roll: ${seat.roll_number}` : 'Empty'}
    >
      {!seat.is_broken && !seat.is_unallocated && (
          <>
            <span className="text-[8px] font-bold uppercase opacity-90 tracking-wide">{seat.batch_label || `B${seat.batch}`}</span>
            <span className="text-[11px] md:text-sm font-black mt-1">{seat.roll_number}</span>
          </>
      )}
      {seat.is_broken && <span className="text-base font-black">✕</span>}
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-[1600px] mx-auto space-y-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_4px_26px_rgba(192,192,192,0.22)] dark:shadow-[0_4px_26px_rgba(138,138,138,0.22)]">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Live Allocation</span>
            </div>
            <SplitText
              text={`Allocation Cockpit`}
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              splitType="chars"
              delay={30}
            />
            <p className="text-gray-600 dark:text-gray-400 mt-2">Configure and generate intelligent seat arrangements</p>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
           <Card className="xl:col-span-4 h-full flex flex-col overflow-hidden border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_28px_rgba(192,192,192,0.22)] dark:shadow-[0_0_28px_rgba(138,138,138,0.24)]">
             <div className="p-6 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border-b-2 border-[#c0c0c0] dark:border-[#8a8a8a]">
               <h2 className="text-xl font-bold text-orange-900 dark:text-orange-100 flex items-center gap-2">
                 <Flame size={24} className="text-orange-500"/>
                 Configuration Panel
               </h2>
             </div>
             
             <div className="p-6 space-y-6 flex-1 overflow-y-auto custom-scrollbar">
                <div>
                  <label className="flex items-center gap-2 text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest mb-3">
                    <Monitor size={16} className="text-orange-500" />
                    1. Select Venue
                  </label>
                  <select value={selectedRoomId} onChange={e=>handleRoomChange(e.target.value)} className="w-full h-12 px-4 bg-white dark:bg-gray-800 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl font-bold dark:text-white outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all">
                     <option value="">-- Manual Configuration --</option>
                     {classrooms.map(r=><option key={r.id} value={r.id}>{r.name}</option>)}
                  </select>
                  {selectedRoomId && (
                    <div className="mt-3 flex gap-2 text-xs font-mono">
                      <span className="bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 px-3 py-1.5 rounded-lg font-bold border border-orange-200 dark:border-orange-800">{rows}×{cols} Grid</span>
                      <span className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-lg font-bold border border-red-200 dark:border-red-800">{brokenSeats.split(',').filter(Boolean).length} Broken</span>
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex justify-between items-center mb-3">
                     <label className="flex items-center gap-2 text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest">
                       <Users size={16} className="text-orange-500" />
                       2. Configure Batches
                     </label>
                     <input type="number" value={numBatches} onChange={e=>setNumBatches(Math.max(1, parseInt(e.target.value)||1))} className="w-14 h-9 text-center border-2 border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 dark:text-white font-bold focus:ring-2 focus:ring-orange-500" />
                  </div>
                  <div className="space-y-3">
                     {batchConfigs.map((b, i) => (
                       <div key={b.id} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-750 rounded-xl border-2 border-[#c0c0c0] dark:border-[#8a8a8a] space-y-3 hover:border-orange-500 dark:hover:border-orange-400 transition-all">
                          <div className="flex gap-2">
                            <input value={b.label} onChange={e=>updateBatch(i,'label',e.target.value)} className="flex-1 h-9 px-3 text-xs border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-lg bg-white dark:bg-gray-800 dark:text-white font-bold focus:ring-2 focus:ring-orange-500" placeholder="Batch Label" />
                            <input type="color" value={b.color} onChange={e=>updateBatch(i,'color',e.target.value)} className="w-9 h-9 p-0.5 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-lg cursor-pointer" />
                          </div>
                          <div className="flex items-center gap-2">
                             <Hash size={14} className="text-orange-500"/>
                             <input value={b.startRoll} onChange={e=>updateBatch(i,'startRoll',e.target.value)} className="flex-1 h-9 px-3 text-xs border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-lg bg-white dark:bg-gray-800 dark:text-white font-mono focus:ring-2 focus:ring-orange-500" placeholder="Start Roll Number" />
                          </div>
                       </div>
                     ))}
                  </div>
                </div>

                <div className="flex flex-col gap-3 pt-4 border-t-2 border-[#c0c0c0] dark:border-[#8a8a8a]">
                   <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                     <input type="checkbox" checked={useDemoDb} onChange={e=>setUseDemoDb(e.target.checked)} className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"/>
                     <Database size={16} className="text-orange-500" />
                     Use Student Database
                   </label>
                   <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                     <input type="checkbox" checked={batchByColumn} onChange={e=>setBatchByColumn(e.target.checked)} className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"/>
                     <Layout size={16} className="text-orange-500" />
                     Fill By Columns
                   </label>
                   <label className="flex items-center gap-3 text-sm font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:text-orange-600 dark:hover:text-orange-400 transition-colors">
                     <input type="checkbox" checked={enforceNoAdjacentBatches} onChange={e=>setEnforceNoAdjacentBatches(e.target.checked)} className="w-5 h-5 rounded border-2 border-gray-300 text-orange-600 focus:ring-2 focus:ring-orange-500"/>
                     <MapPin size={16} className="text-orange-500" />
                     Enforce Batch Gap
                   </label>
                </div>

                <div className="pt-4 border-t-2 border-[#c0c0c0] dark:border-[#8a8a8a]">
                  <Button onClick={handleResetDatabase} variant="destructive" className="w-full h-11 text-sm font-bold uppercase tracking-wide" disabled={resetting}>
                    {resetting ? <Loader2 className="animate-spin mr-2" size={16}/> : <Trash2 size={16} className="mr-2"/>}
                    {resetting ? 'Resetting Database...' : 'Reset All Data'}
                  </Button>
                </div>
             </div>
             
             <div className="p-6 border-t-2 border-[#c0c0c0] dark:border-[#8a8a8a] bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750">
                <Button onClick={generate} disabled={loading} className="w-full h-14 bg-gradient-to-r from-orange-500 to-amber-500 text-white hover:from-orange-600 hover:to-amber-600 shadow-lg hover:shadow-xl text-base font-black uppercase tracking-wide">
                  {loading ? <><Loader2 className="animate-spin mr-2" size={20}/>Generating...</> : <><Play className="mr-2" size={20}/>Generate Seating Plan</>}
                </Button>
             </div>
          </Card>

          <Card className="xl:col-span-8 h-full flex flex-col relative overflow-hidden p-6 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_32px_rgba(192,192,192,0.24)] dark:shadow-[0_0_32px_rgba(138,138,138,0.26)]" ref={chartRef}>
             <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                  <h2 className="text-2xl font-black text-gray-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
                    <Layout className="text-orange-500" size={24} />
                    <SplitText text={`Live Preview`} className="uppercase" splitType="chars" delay={20} />
                  </h2>
                  {webData && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-mono">{webData.seating.flat().filter(s => !s.is_unallocated && !s.is_broken).length} seats allocated</p>}
                </div>
                {webData && (
                  <div className="flex gap-2 flex-wrap">
                     <Button onClick={showConstraints} className="h-10 px-4 bg-purple-100 text-purple-700 hover:bg-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:hover:bg-purple-900/50 text-xs font-bold">
                       <Settings size={14} className="mr-2"/> Rules
                     </Button>
                     <div className="relative group">
                        <Button className="h-10 px-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-600 hover:to-emerald-700 text-xs font-bold flex gap-2">
                          <Download size={14}/> Export PDF
                        </Button>
                        <div className="absolute right-0 top-full mt-2 w-52 bg-white dark:bg-gray-800 shadow-[0_0_32px_rgba(192,192,192,0.3)] dark:shadow-[0_0_32px_rgba(138,138,138,0.32)] rounded-xl border-2 border-[#c0c0c0] dark:border-[#8a8a8a] hidden group-hover:block z-50 p-2 animate-fadeIn">
                          <button onClick={()=>downloadPdf('client')} className="w-full text-left px-4 py-3 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg text-sm font-bold text-gray-900 dark:text-white transition-colors flex items-center gap-2">
                            <Zap size={14} className="text-orange-500" />
                            Client PDF (Fast)
                          </button>
                          <button onClick={()=>downloadPdf('server')} className="w-full text-left px-4 py-3 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg text-sm font-bold text-gray-900 dark:text-white transition-colors flex items-center gap-2">
                            <Download size={14} className="text-orange-500" />
                            Server PDF (HQ)
                          </button>
                        </div>
                     </div>
                  </div>
                )}
             </div>
             
             {!webData ? (
               <div className="flex-1 flex flex-col items-center justify-center text-gray-300 dark:text-gray-600">
                 <div className="relative mb-6">
                   <div className="absolute inset-0 bg-orange-500 rounded-full blur-2xl opacity-20"></div>
                   <Layout size={80} className="relative opacity-20"/>
                 </div>
                 <p className="font-bold uppercase tracking-widest text-sm">Ready to Generate Seating Plan</p>
                 <p className="text-xs mt-2 text-gray-400">Configure your settings and click Generate</p>
               </div>
             ) : (
               <div className="flex-1 overflow-auto p-4 custom-scrollbar">
                 <div className="relative mb-8">
                   <div className="w-2/3 h-2 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-500 mx-auto rounded-full shadow-lg"></div>
                   <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-black text-orange-600 dark:text-orange-400 uppercase tracking-[0.5em] flex items-center gap-2">
                     <ChevronRight size={12} className="rotate-180"/>Board<ChevronRight size={12}/>
                   </div>
                 </div>
                 <div className="grid gap-2 mx-auto" style={{ gridTemplateColumns: `repeat(${cols}, minmax(50px, 1fr))`, width: 'fit-content' }}>
                    {webData.seating.map((row, rIdx) => row.map((seat, cIdx) => renderSeat(seat, rIdx, cIdx)))}
                 </div>
               </div>
             )}
          </Card>
        </div>
      </div>
      <style>{`.custom-scrollbar::-webkit-scrollbar{width:8px;height:8px}.custom-scrollbar::-webkit-scrollbar-track{background:transparent}.custom-scrollbar::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:10px}.custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#9ca3af}.dark .custom-scrollbar::-webkit-scrollbar-thumb{background:#4b5563}.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover{background:#6b7280}`}</style>
    </div>
  );
};
export default AllocationPage;