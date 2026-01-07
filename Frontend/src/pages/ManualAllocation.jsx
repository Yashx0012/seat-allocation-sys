import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, Download, Layout, AlertTriangle, CheckCircle, 
  User, RefreshCw, ChevronLeft, Edit3, Grid, Box
} from 'lucide-react';

// Define the initial state for the form inputs
const initialFormState = {
    rows: 8,
    cols: 10,
    numBatches: 3,
    brokenSeatsStr: '',
    batchStudentCountsStr: '',
    startRollsStr: '',
    startSerials: { 1: 1, 2: 101, 3: 201 },
    blockWidth: 3,
    fillByColumn: true,
    enforceAdj: false,
};

const BATCH_COLORS_DEV = ['#3b82f6', '#10b981', '#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b', '#06b6d4', '#f43f5e', '#14b8a6'];

const getDefaultStartSerials = (numBatches) => {
    const serials = {};
    for (let i = 1; i <= numBatches; i++) {
        let defaultRoll = 1;
        if (i === 2) defaultRoll = 101;
        else if (i === 3) defaultRoll = 201;
        else if (i > 3) defaultRoll = (i * 100 + 1);
        serials[i] = defaultRoll;
    }
    return serials;
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
    const [form, setForm] = useState(() => ({
        ...initialFormState,
        startSerials: getDefaultStartSerials(initialFormState.numBatches)
    }));
    const [seatingData, setSeatingData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isPdfGenerating, setIsPdfGenerating] = useState(false);

    const isDownloadDisabled = !seatingData || seatingData.error || seatingData.validation?.is_valid === false;

    // --- Handlers ---
    const handleInputChange = (e) => {
        const { id, value, type, checked } = e.target;
        setForm(prev => ({
            ...prev,
            [id]: type === 'checkbox' ? checked : (type === 'number' ? parseInt(value) || '' : value)
        }));
    };

    const handleStartSerialChange = useCallback((batchIndex, value) => {
        setForm(prev => ({
            ...prev,
            startSerials: { ...prev.startSerials, [batchIndex]: parseInt(value) || 1 }
        }));
    }, []);

    useEffect(() => {
        setForm(prev => ({
            ...prev,
            startSerials: getDefaultStartSerials(prev.numBatches)
        }));
    }, [form.numBatches]);

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
            start_rolls: form.startRollsStr,
            start_serials: startSerialsApiStr,
        };
        
        try {
            const response = await fetch('http://localhost:5000/api/generate-seating', {
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
            const response = await fetch('http://localhost:5000/api/generate-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(seatingData)
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `manual_seating_${Date.now()}.pdf`;
            a.click();
        } catch (err) {
            if(showToast) showToast("PDF Generation Failed", "error");
        } finally {
            setIsPdfGenerating(false);
        }
    };

    // --- Styling Classes (Matching Modern UI) ---
    const inputStyle = "w-full h-12 px-4 rounded-xl border-2 border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 dark:text-white focus:border-orange-500 outline-none transition-all font-medium text-sm";
    const labelStyle = "text-[10px] font-black uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-2 block ml-1";

    return (
        <div className="min-h-screen bg-white dark:bg-[#050505] text-gray-900 dark:text-white pb-20">
            {/* Header */}
            <div className="max-w-7xl mx-auto px-6 pt-12">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
                    <div>
                        <Link to="/" className="flex items-center gap-2 text-gray-400 hover:text-orange-500 transition-colors mb-4 group">
                            <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                            <span className="text-xs font-black uppercase tracking-widest">Back to Home</span>
                        </Link>
                        <h1 className="text-5xl font-black tracking-tighter uppercase flex items-center gap-4">
                            <Settings className="text-orange-500" size={40} />
                            Manual <span className="text-orange-500">Allocation</span>
                        </h1>
                        <p className="text-gray-500 font-medium mt-2">Custom classroom parameters & specific roll number ranges.</p>
                    </div>

                    <div className="flex gap-3">
                        <button 
                            onClick={generateSeating}
                            disabled={isLoading}
                            className="h-14 px-8 bg-orange-500 hover:bg-orange-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs flex items-center gap-2 transition-all shadow-lg shadow-orange-500/20 disabled:opacity-50"
                        >
                            {isLoading ? <RefreshCw className="animate-spin" size={18} /> : <Layout size={18} />}
                            Generate Plan
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Sidebar: Form Controls */}
                    <div className="lg:col-span-4 space-y-6">
                        <div className="p-8 rounded-3xl bg-gray-50 dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800">
                            <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-2">
                                <Grid size={16} /> Grid Geometry
                            </h2>
                            
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div>
                                    <label className={labelStyle}>Rows</label>
                                    <input type="number" id="rows" value={form.rows} onChange={handleInputChange} className={inputStyle} />
                                </div>
                                <div>
                                    <label className={labelStyle}>Columns</label>
                                    <input type="number" id="cols" value={form.cols} onChange={handleInputChange} className={inputStyle} />
                                </div>
                            </div>

                            <div className="mb-6">
                                <label className={labelStyle}>Number of Batches</label>
                                <input type="number" id="numBatches" value={form.numBatches} onChange={handleInputChange} className={inputStyle} />
                            </div>

                            <div>
                                <label className={labelStyle}>Broken Seats (Row-Col)</label>
                                <textarea 
                                    id="brokenSeatsStr" 
                                    placeholder="1-3, 2-1..." 
                                    value={form.brokenSeatsStr} 
                                    onChange={handleInputChange} 
                                    className={`${inputStyle} h-24 py-3 resize-none`}
                                />
                            </div>
                        </div>

                        <div className="p-8 rounded-3xl bg-gray-50 dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800">
                            <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-2">
                                <Box size={16} /> Allocation Logic
                            </h2>
                            
                            <div className="space-y-6">
                                <div>
                                    <label className={labelStyle}>Block Width</label>
                                    <input type="number" id="blockWidth" value={form.blockWidth} onChange={handleInputChange} className={inputStyle} />
                                </div>

                                <div className="flex flex-col gap-4">
                                    <label className="flex items-center gap-3 cursor-pointer group">
                                        <div className="relative">
                                            <input type="checkbox" id="fillByColumn" checked={form.fillByColumn} onChange={handleInputChange} className="sr-only" />
                                            <div className={`w-12 h-6 rounded-full transition-colors ${form.fillByColumn ? 'bg-orange-500' : 'bg-gray-300 dark:bg-gray-700'}`} />
                                            <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${form.fillByColumn ? 'translate-x-6' : ''}`} />
                                        </div>
                                        <span className="text-sm font-bold text-gray-600 dark:text-gray-400 group-hover:text-orange-500 transition-colors">Fill By Column</span>
                                    </label>

                                    <label className="flex items-center gap-3 cursor-pointer group">
                                        <div className="relative">
                                            <input type="checkbox" id="enforceAdj" checked={form.enforceAdj} onChange={handleInputChange} className="sr-only" />
                                            <div className={`w-12 h-6 rounded-full transition-colors ${form.enforceAdj ? 'bg-orange-500' : 'bg-gray-300 dark:bg-gray-700'}`} />
                                            <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${form.enforceAdj ? 'translate-x-6' : ''}`} />
                                        </div>
                                        <span className="text-sm font-bold text-gray-600 dark:text-gray-400 group-hover:text-orange-500 transition-colors">Enforce No Adjacency</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Area: Detailed Inputs & Preview */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* Batch Specifics */}
                        <div className="p-8 rounded-3xl bg-white dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800 shadow-xl shadow-black/5">
                            <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-2">
                                <User size={16} /> Batch Enrollment Details
                            </h2>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="md:col-span-2">
                                    <label className={labelStyle}>Batch Start Roll Numbers (Overrides)</label>
                                    <input 
                                        type="text" 
                                        id="startRollsStr" 
                                        placeholder="1:BTCS24O1135, 2:BTCD24O2001..." 
                                        value={form.startRollsStr} 
                                        onChange={handleInputChange} 
                                        className={inputStyle} 
                                    />
                                </div>
                                
                                <div className="md:col-span-2">
                                    <label className={labelStyle}>Student Counts Per Batch</label>
                                    <input 
                                        type="text" 
                                        id="batchStudentCountsStr" 
                                        placeholder="1:35, 2:30, 3:25..." 
                                        value={form.batchStudentCountsStr} 
                                        onChange={handleInputChange} 
                                        className={inputStyle} 
                                    />
                                </div>

                                <div className="md:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {Object.entries(form.startSerials).slice(0, form.numBatches).map(([idx, val]) => (
                                        <div key={idx} className="p-4 rounded-2xl bg-gray-50 dark:bg-black/20 border border-gray-100 dark:border-gray-800">
                                            <label className="text-[9px] font-black uppercase text-gray-400 mb-2 block">Batch {idx} Serial</label>
                                            <input 
                                                type="number" 
                                                value={val} 
                                                onChange={(e) => handleStartSerialChange(idx, e.target.value)}
                                                className="w-full bg-transparent font-black text-orange-500 outline-none"
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Preview Section */}
                        <div className="p-8 rounded-3xl bg-white dark:bg-white/5 border-2 border-gray-100 dark:border-gray-800 shadow-xl shadow-black/5 min-h-[500px]">
                            <div className="flex justify-between items-center mb-8">
                                <h2 className="text-xs font-black text-orange-500 uppercase tracking-[0.3em] flex items-center gap-2">
                                    <Layout size={16} /> Visual Arrangement
                                </h2>
                                {seatingData && (
                                    <button 
                                        onClick={handleDownloadPdf}
                                        disabled={isPdfGenerating}
                                        className="flex items-center gap-2 text-xs font-black uppercase text-orange-500 hover:text-orange-600"
                                    >
                                        {isPdfGenerating ? <RefreshCw className="animate-spin" size={14}/> : <Download size={14}/>}
                                        Export PDF
                                    </button>
                                )}
                            </div>

                            <AnimatePresence mode="wait">
                                {isLoading ? (
                                    <motion.div initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="flex flex-col items-center justify-center py-20">
                                        <RefreshCw className="animate-spin text-orange-500 mb-4" size={40} />
                                        <p className="font-black text-xs uppercase tracking-[0.2em] text-gray-500">Calculating Matrix...</p>
                                    </motion.div>
                                ) : seatingData ? (
                                    <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} className="overflow-x-auto pb-6 custom-scrollbar">
                                        <div 
                                            className="grid gap-2"
                                            style={{ gridTemplateColumns: `repeat(${seatingData.metadata.cols}, minmax(100px, 1fr))` }}
                                        >
                                            {seatingData.seating.map((row, rIdx) => (
                                                row.map((seat, cIdx) => {
                                                    const isBlockStart = (cIdx % form.blockWidth === 0 && cIdx !== 0);
                                                    const batchColor = seat.is_broken ? '#ef4444' : (seat.color || '#374151');
                                                    const textColor = getContrastTextColor(batchColor);

                                                    return (
                                                        <div 
                                                            key={`${rIdx}-${cIdx}`}
                                                            style={{ 
                                                                backgroundColor: batchColor,
                                                                marginLeft: isBlockStart ? '12px' : '0px'
                                                            }}
                                                            className={`h-24 rounded-xl flex flex-col items-center justify-center p-2 text-center shadow-sm border border-black/10 transition-transform hover:scale-[1.02] ${textColor}`}
                                                        >
                                                            {seat.is_broken ? (
                                                                <span className="text-[10px] font-black uppercase italic opacity-80">Broken</span>
                                                            ) : (
                                                                <>
                                                                    <span className="text-[9px] font-black uppercase opacity-60">Batch {seat.batch}</span>
                                                                    <span className="text-xs font-black truncate w-full">{seat.roll_number || 'EMPTY'}</span>
                                                                    <span className="text-[8px] mt-1 font-bold opacity-50">{seat.position}</span>
                                                                </>
                                                            )}
                                                        </div>
                                                    );
                                                })
                                            ))}
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                                        <Grid size={48} strokeWidth={1} className="mb-4 opacity-20" />
                                        <p className="text-sm font-medium">Configure parameters and click "Generate Plan"</p>
                                    </div>
                                )}
                            </AnimatePresence>

                            {/* Summary Footer */}
                            {seatingData && (
                                <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800 grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-gray-800">
                                        <p className="text-[9px] font-black text-gray-400 uppercase">Total Seats</p>
                                        <p className="text-xl font-black">{seatingData.summary.total_available_seats}</p>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-gray-800">
                                        <p className="text-[9px] font-black text-gray-400 uppercase">Allocated</p>
                                        <p className="text-xl font-black text-orange-500">{seatingData.summary.total_allocated_students}</p>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-gray-800">
                                        <p className="text-[9px] font-black text-gray-400 uppercase">Validation</p>
                                        <div className="flex items-center gap-2 mt-1">
                                            {seatingData.validation.is_valid ? 
                                                <><CheckCircle size={16} className="text-green-500" /> <span className="text-xs font-bold text-green-500 uppercase">Clear</span></> : 
                                                <><AlertTriangle size={16} className="text-red-500" /> <span className="text-xs font-bold text-red-500 uppercase">Conflict</span></>
                                            }
                                        </div>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-gray-800">
                                        <p className="text-[9px] font-black text-gray-400 uppercase">Unallocated</p>
                                        <p className="text-xl font-black">{Object.values(seatingData.summary.unallocated_per_batch || {}).reduce((a, b) => a + b, 0)}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            <style>{`
                .custom-scrollbar::-webkit-scrollbar { height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #f97316; border-radius: 10px; }
            `}</style>
        </div>
    );
};

export default ManualAllocation;