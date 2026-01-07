import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, Download, Layout, AlertTriangle, CheckCircle, 
  User, RefreshCw, ChevronLeft, Grid, Box, Maximize2, XCircle
} from 'lucide-react';

const initialFormState = {
    rows: 8,
    cols: 10,
    numBatches: 3,
    brokenSeatsStr: '',
    batchStudentCountsStr: '1:30, 2:30, 3:30',
    startRollsStr: '', 
    startSerials: { 1: 1, 2: 101, 3: 201 },
    blockWidth: 3,
    fillByColumn: true,
    enforceAdj: false,
    batchNamesStr: '1:CS, 2:IT, 3:ME',
    roomNo: '101',
};

const getContrastTextColor = (hexcolor) => {
    if (!hexcolor || hexcolor.length !== 7) return 'text-black';
    const r = parseInt(hexcolor.slice(1, 3), 16);
    const g = parseInt(hexcolor.slice(3, 5), 16);
    const b = parseInt(hexcolor.slice(5, 7), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.6 ? 'text-black' : 'text-white';
};

const ManualAllocation = ({ showToast }) => {
    const navigate = useNavigate();
    const [form, setForm] = useState(initialFormState);
    const [seatingData, setSeatingData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isPdfGenerating, setIsPdfGenerating] = useState(false);

    useEffect(() => {
        const serials = {};
        for (let i = 1; i <= form.numBatches; i++) {
            serials[i] = (i - 1) * 100 + 1;
        }
        setForm(prev => ({ ...prev, startSerials: serials }));
    }, [form.numBatches]);

    const handleInputChange = (e) => {
        const { id, value, type, checked } = e.target;
        setForm(prev => ({
            ...prev,
            [id]: type === 'checkbox' ? checked : (type === 'number' ? parseInt(value) || '' : value)
        }));
    };

    const handleStartSerialChange = (idx, value) => {
        setForm(prev => ({
            ...prev,
            startSerials: { ...prev.startSerials, [idx]: parseInt(value) || 1 }
        }));
    };

    const generateSeating = useCallback(async () => {
        setError(null);
        setIsLoading(true);
        
        const startSerialsApiStr = Object.entries(form.startSerials)
            .map(([idx, serial]) => `${idx}:${serial}`).join(',');

        const payload = {
            rows: form.rows,
            cols: form.cols,
            num_batches: form.numBatches,
            block_width: form.blockWidth,
            batch_by_column: form.fillByColumn,
            enforce_no_adjacent_batches: form.enforceAdj,
            broken_seats: form.brokenSeatsStr,
            batch_student_counts: form.batchStudentCountsStr,
            start_rolls: form.startRollsStr, // Removed default prefix string here
            start_serials: startSerialsApiStr,
            batch_names: form.batchNamesStr,
            room_no: form.roomNo,
        };
        
        try {
            const response = await fetch('/api/generate-manual-seating', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            setSeatingData(data);
            if(showToast) showToast("Seating Generated Successfully", "success");
        } catch (err) {
            setError(err.message);
            if(showToast) showToast(err.message, "error");
        } finally {
            setIsLoading(false);
        }
    }, [form, showToast]);

    const handleDownloadPdf = async () => {
        setIsPdfGenerating(true);
        try {
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(seatingData)
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `manual_plan_Room_${form.roomNo}_${Date.now()}.pdf`;
            a.click();
        } catch (err) {
            if(showToast) showToast("PDF Generation Failed", "error");
        } finally {
            setIsPdfGenerating(false);
        }
    };

    const inputStyle = "w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 dark:text-white focus:border-orange-500 outline-none transition-all font-bold text-sm";
    const labelStyle = "text-[11px] font-black uppercase tracking-widest text-gray-900 dark:text-white mb-2 block ml-1";
    const sectionHeading = "text-xs font-black text-orange-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-2";

    return (
        <div className="min-h-screen bg-white dark:bg-[#050505] text-gray-900 dark:text-white pb-20">
            <div className="max-w-[1800px] mx-auto px-6 pt-12">
                
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
                    <div>
                        <Link to="/create-plan" className="flex items-center gap-2 text-gray-400 hover:text-orange-500 transition-colors mb-4 group">
                            <ChevronLeft size={18} />
                            <span className="text-xs font-black uppercase tracking-widest">Back to Planner</span>
                        </Link>
                        <h1 className="text-5xl font-black tracking-tighter uppercase">
                            Manual <span className="text-orange-500">Allocation</span>
                        </h1>
                    </div>
                    <button 
                        onClick={generateSeating} 
                        disabled={isLoading} 
                        className="h-14 px-10 bg-orange-500 hover:bg-orange-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs flex items-center gap-2 transition-all shadow-lg disabled:opacity-50"
                    >
                        {isLoading ? <RefreshCw className="animate-spin" /> : <Layout size={20} />}
                        Generate Plan
                    </button>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                    {/* SIDEBAR */}
                    <div className="xl:col-span-3 space-y-6">
                        <div className="p-6 rounded-3xl bg-gray-50 dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800">
                            <h2 className={sectionHeading}><Grid size={16} /> Grid Geometry</h2>
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div><label className={labelStyle}>Rows</label><input type="number" id="rows" value={form.rows} onChange={handleInputChange} className={inputStyle} /></div>
                                <div><label className={labelStyle}>Columns</label><input type="number" id="cols" value={form.cols} onChange={handleInputChange} className={inputStyle} /></div>
                            </div>
                            <div className="mb-4">
                                <label className={labelStyle}>Number of Batches</label>
                                <input type="number" id="numBatches" value={form.numBatches} onChange={handleInputChange} className={inputStyle} />
                            </div>
                            <label className={labelStyle}>Block Width</label>
                            <input type="number" id="blockWidth" value={form.blockWidth} onChange={handleInputChange} className={inputStyle} />
                        </div>

                        <div className="p-6 rounded-3xl bg-gray-50 dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800">
                            <h2 className={sectionHeading}><Box size={16} /> Batch Serials</h2>
                            <div className="grid grid-cols-2 gap-3">
                                {Object.entries(form.startSerials).slice(0, form.numBatches).map(([idx, val]) => (
                                    <div key={idx} className="p-3 rounded-xl bg-white dark:bg-black/40 border border-gray-200 dark:border-gray-800">
                                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block">Batch {idx} Serial</label>
                                        <input type="number" value={val} onChange={(e) => handleStartSerialChange(idx, e.target.value)} className="w-full bg-transparent font-black text-orange-500 outline-none" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="xl:col-span-9 space-y-8">
                        <div className="p-8 rounded-3xl bg-gray-50 dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800 shadow-sm">
                            <h2 className={sectionHeading}><User size={16} /> Batch Enrollment Details</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="md:col-span-2">
                                    <label className={labelStyle}>Batch Names</label>
                                    <input type="text" id="batchNamesStr" value={form.batchNamesStr} onChange={handleInputChange} className={inputStyle} placeholder="1:CS, 2:IT, 3:ME" />
                                </div>
                                <div>
                                    <label className={labelStyle}>Room Number</label>
                                    <input type="text" id="roomNo" value={form.roomNo} onChange={handleInputChange} className={inputStyle} placeholder="101" />
                                </div>
                                <div className="md:col-span-2">
                                    <label className={labelStyle}>Batch Start Roll Numbers (Overrides)</label>
                                    <input 
                                        type="text" id="startRollsStr" value={form.startRollsStr} onChange={handleInputChange} className={inputStyle} 
                                        placeholder="Optional (e.g. 1:101, 2:501). Leave blank for simple serials." 
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className={labelStyle}>Student Counts Per Batch</label>
                                    <input type="text" id="batchStudentCountsStr" value={form.batchStudentCountsStr} onChange={handleInputChange} className={inputStyle} placeholder="1:30, 2:25..." />
                                </div>
                            </div>
                        </div>

                        <div className="p-8 rounded-3xl bg-white dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800 shadow-2xl min-h-[600px]">
                            <div className="flex justify-between items-center mb-8">
                                <h2 className={sectionHeading}><Maximize2 size={16} /> Visual Arrangement (Room {form.roomNo})</h2>
                                {seatingData && (
                                    <button onClick={handleDownloadPdf} className="flex items-center gap-2 text-xs font-black uppercase text-orange-500 hover:scale-105 transition-all">
                                        <Download size={16} /> Export PDF
                                    </button>
                                )}
                            </div>

                            <AnimatePresence mode="wait">
                                {seatingData ? (
                                    <motion.div initial={{opacity:0}} animate={{opacity:1}} className="overflow-x-auto pb-6 custom-scrollbar">
                                        <div 
                                            className="grid gap-2 min-w-max" 
                                            style={{ gridTemplateColumns: `repeat(${seatingData.metadata.cols}, 120px)` }}
                                        >
                                            {seatingData.seating.map((row, rIdx) => (
                                                row.map((seat, cIdx) => {
                                                    const isBroken = seat.is_broken;
                                                    const isEmpty = !seat.batch && !isBroken;
                                                    const batchColor = isBroken ? '#ef4444' : (isEmpty ? 'transparent' : (seat.color || '#374151'));
                                                    const borderStyle = isEmpty ? 'border-2 border-dashed border-gray-200 dark:border-gray-800' : 'border border-black/10';
                                                    
                                                    return (
                                                        <div 
                                                            key={`${rIdx}-${cIdx}`} 
                                                            style={{ backgroundColor: batchColor }} 
                                                            className={`h-24 rounded-xl flex flex-col items-center justify-center p-2 text-center shadow-sm transition-all hover:scale-[1.02] ${borderStyle} ${getContrastTextColor(batchColor)}`}
                                                        >
                                                            {isBroken ? (
                                                                <div className="flex flex-col items-center opacity-60">
                                                                    <XCircle size={16} className="mb-1" />
                                                                    <span className="text-[10px] font-black italic">BROKEN</span>
                                                                </div>
                                                            ) : isEmpty ? (
                                                                <span className="text-[10px] font-black opacity-20 tracking-tighter">R{rIdx+1}-C{cIdx+1}</span>
                                                            ) : (
                                                                <>
                                                                    <span className="text-[9px] font-black opacity-60 uppercase">Batch {seat.batch}</span>
                                                                    <span className="text-[12px] font-black leading-tight truncate w-full">{seat.roll_number || 'NA'}</span>
                                                                    <span className="text-[8px] font-bold opacity-40 mt-1 uppercase tracking-tighter">{seat.position}</span>
                                                                </>
                                                            )}
                                                        </div>
                                                    );
                                                })
                                            ))}
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-40 text-gray-400">
                                        <Layout size={60} strokeWidth={1} className="mb-4 opacity-10" />
                                        <p className="font-bold text-sm tracking-widest uppercase opacity-40">Configure grid and click generate</p>
                                    </div>
                                )}
                            </AnimatePresence>

                            {seatingData && (
                                <div className="mt-8 p-6 bg-orange-500/5 border-2 border-orange-500/20 rounded-2xl">
                                    <h3 className={`font-black text-xs uppercase mb-4 flex items-center gap-2 ${seatingData.validation.is_valid ? 'text-green-500' : 'text-red-500'}`}>
                                        {seatingData.validation.is_valid ? <CheckCircle size={16} /> : <AlertTriangle size={16} />} Allocation Intelligence
                                    </h3>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                        <div className="p-4 rounded-xl bg-white dark:bg-white/5 border border-gray-100 dark:border-gray-800">
                                            <p className="text-[10px] font-black text-gray-400 uppercase mb-1">Room Capacity</p>
                                            <p className="text-lg font-black">{seatingData.metadata.rows * seatingData.metadata.cols - (seatingData.summary.broken_seats || 0)} usable</p>
                                        </div>
                                        {Object.entries(seatingData.summary.total_per_batch || {}).map(([batch, count]) => (
                                            <div key={batch} className="p-4 rounded-xl bg-white dark:bg-white/5 border border-orange-500/20">
                                                <p className="text-[10px] font-black text-orange-500 uppercase mb-1">Batch {batch} Seated</p>
                                                <p className="text-lg font-black">{count} Students</p>
                                            </div>
                                        ))}
                                    </div>
                                    
                                    {!seatingData.validation.is_valid && (
                                        <div className="mt-6 p-4 bg-red-500/10 rounded-xl border border-red-500/20">
                                            <h4 className="text-xs font-black text-red-500 uppercase mb-2">Conflicts Detected</h4>
                                            <ul className="text-sm font-medium text-red-600 space-y-1">
                                                {seatingData.validation.errors.map((err, i) => <li key={i}>• {err}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <style>{`
                .custom-scrollbar::-webkit-scrollbar { height: 8px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #f97316; border-radius: 20px; border: 2px solid transparent; background-clip: content-box; }
            `}</style>
        </div>
    );
};

export default ManualAllocation;