import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, AlertCircle, CheckCircle, Database, Search, Users, LayoutDashboard, User, MessageSquare, ChevronRight } from "lucide-react";

// --- Matrix Data ---
const MATRIX_DATA = [
  { id: 1, text: "OPTIMIZING VECTORS" },
  { id: 2, text: "SEAT_MATRIX_ACTIVE" },
  { id: 3, text: "SYNC_COMPLETE" }
];

export default function ExamPortal() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [examData, setExamData] = useState(null);

  useEffect(() => {
    const initMatrix = async () => {
      try {
        setLoading(true);
        // Simulated matrix loading
        await new Promise(r => setTimeout(r, 1500));
        setExamData({
          examName: 'End Semester Matrix',
          status: 'ready',
          seats: 450,
          rooms: 12
        });
      } catch (err) {
        setError('Failed to sync with Matrix Core');
      } finally {
        setLoading(false);
      }
    };
    initMatrix();
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#050505] flex flex-col items-center justify-center text-orange-500 overflow-hidden">
        <motion.div 
          animate={{ rotate: 360 }} 
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
        >
          <Loader2 className="w-16 h-16 opacity-80" />
        </motion.div>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ repeat: Infinity, duration: 1, repeatType: "reverse" }}
          className="mt-6 font-mono text-sm tracking-[0.3em] uppercase"
        >
          Initializing Seat Matrix...
        </motion.p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-screen bg-[#050505] flex items-center justify-center text-red-500 font-mono">
        <div className="text-center p-8 border border-red-500/20 bg-red-500/10 rounded-2xl backdrop-blur-md">
          <AlertCircle className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-xl tracking-widest mb-2 uppercase">Matrix Error</h2>
          <p className="text-red-400 mb-6 text-sm">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="border border-red-500/50 hover:bg-red-500/20 text-red-400 py-2 px-6 rounded transition-colors text-sm uppercase tracking-widest"
          >
            System Reboot
          </button>
        </div>
      </div>
    );
  }

  // A sleek, one-slide smooth UI
  return (
    <div className="h-screen w-screen bg-[#050505] text-white overflow-hidden font-sans flex flex-col relative selection:bg-orange-500 selection:text-white">
      {/* Background Matrix Glow */}
      <div className="absolute top-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-orange-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-orange-600/5 blur-[120px] pointer-events-none" />

      {/* Header element */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full h-24 px-8 md:px-12 flex items-center justify-between border-b border-white/10 z-10 bg-black/20 backdrop-blur-lg"
      >
        <div className="flex flex-col">
          <h1 className="text-2xl md:text-3xl font-black tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-600">
            Seat Matrix
          </h1>
          <span className="text-[10px] font-mono text-gray-500 tracking-[0.2em] uppercase">Core Engine Active</span>
        </div>
        <div className="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2 rounded-full">
          <CheckCircle className="w-4 h-4 text-orange-500" />
          <span className="text-xs font-bold tracking-widest text-orange-500 uppercase">Synced</span>
        </div>
      </motion.header>

      {/* Main Single Slide Content */}
      <div className="flex-1 flex flex-col lg:flex-row w-full max-w-[1600px] mx-auto p-6 md:p-12 gap-8 z-10 overflow-y-auto">
        
        {/* Left Panel: Status & Info */}
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="flex-1 flex flex-col justify-center space-y-12"
        >
          <div className="space-y-6">
            <h2 className="text-5xl md:text-7xl font-black uppercase leading-[0.85] tracking-tighter">
              Spatial<br/>
              <span className="text-gray-500">Intelligence.</span>
            </h2>
            <p className="text-gray-400 font-medium max-w-md text-lg leading-relaxed">
              Welcome to the Seat Matrix terminal. Navigate your examinations, download real-time vector plans, and oversee real-time diagnostics from one unified interface.
            </p>
          </div>

          {/* Database Info Snippets */}
          <div className="grid grid-cols-2 gap-4 max-w-md">
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
              <div className="text-orange-500 mb-2"><Users size={24}/></div>
              <div className="text-3xl font-black">{examData.seats}</div>
              <div className="text-xs text-gray-500 uppercase tracking-widest mt-1">Total Seats</div>
            </div>
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl">
              <div className="text-orange-500 mb-2"><Database size={24}/></div>
              <div className="text-3xl font-black">{examData.rooms}</div>
              <div className="text-xs text-gray-500 uppercase tracking-widest mt-1">Configured Rooms</div>
            </div>
          </div>
        </motion.div>

        {/* Right Panel: Actions */}
        <motion.div 
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex-1 flex flex-col justify-center"
        >
          <div className="grid grid-cols-1 gap-4 max-w-lg ml-auto w-full">
            <h3 className="text-xs font-mono text-gray-500 tracking-[0.2em] mb-4 uppercase">Command Modules</h3>
            
            <ActionCard
              icon={<Search size={20} />}
              title="Matrix Locator"
              desc="Find exact assigned coordinates."
              onClick={() => navigate('/seat-locator')}
            />
            
            <ActionCard
              icon={<LayoutDashboard size={20} />}
              title="Main Dashboard"
              desc="View system overviews."
              onClick={() => navigate('/dashboard')}
            />

            <ActionCard
              icon={<User size={20} />}
              title="Operator Profile"
              desc="Manage your secure credentials."
              onClick={() => navigate('/profile')}
            />

            <ActionCard
              icon={<MessageSquare size={20} />}
              title="System Feedback"
              desc="Report anomalies in the matrix."
              onClick={() => navigate('/feedback')}
            />
          </div>
        </motion.div>
      </div>

      {/* Footer Info line */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="w-full p-6 text-center text-xs font-mono text-gray-600 tracking-[0.2em] uppercase z-10"
      >
        Seat Matrix Core &bull; Node Active
      </motion.div>
    </div>
  );
}

// Reusable Action Card
function ActionCard({ icon, title, desc, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, x: 10 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="group relative w-full bg-white/[0.03] border border-white/10 hover:border-orange-500/50 p-5 rounded-2xl flex items-center justify-between text-left transition-all overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-orange-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-0 transition-transform duration-500" />
      <div className="flex items-center gap-4 relative z-10">
        <div className="w-12 h-12 rounded-xl bg-orange-500/10 text-orange-500 flex items-center justify-center group-hover:bg-orange-500 group-hover:text-white transition-colors">
          {icon}
        </div>
        <div>
          <h4 className="text-white font-bold text-lg">{title}</h4>
          <p className="text-gray-500 text-sm">{desc}</p>
        </div>
      </div>
      <div className="relative z-10 text-gray-600 group-hover:text-orange-500 transition-colors">
        <ChevronRight size={24} />
      </div>
    </motion.button>
  );
}
