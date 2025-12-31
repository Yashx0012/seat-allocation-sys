import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Layout, 
  MapPin, 
  Download, 
  Upload, 
  CheckCircle,
  ArrowUpRight,
  Terminal,
  AlertCircle,
  Database  // NEW: Added Database icon
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SplitText from '../components/SplitText';

// StatCard Component with counter animation
const StatCard = ({ stat, index }) => {
  const [count, setCount] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    const duration = 1500;
    const steps = 60;
    const interval = duration / steps;
    const targetValue = parseInt(stat.value.replace(/,/g, ''));
    
    if (isNaN(targetValue)) {
      setCount(stat.value);
      setIsAnimating(false);
      return;
    }

    let current = 0;
    const timer = setInterval(() => {
      current += targetValue / steps;
      if (current >= targetValue) {
        current = targetValue;
        clearInterval(timer);
        setIsAnimating(false);
      }
      setCount(Math.floor(current).toLocaleString());
    }, interval);

    return () => clearInterval(timer);
  }, [stat.value]);

  // Animation variants
  const cardStyle = {
    opacity: 0,
    y: 20,
    animation: `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`
  };

  return (
    <div
      style={cardStyle}
      className="glass-card relative overflow-hidden p-6 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_22px_rgba(192,192,192,0.2)] dark:shadow-[0_0_22px_rgba(138,138,138,0.22)] hover:scale-[1.01] hover:shadow-2xl hover:shadow-orange-500/10 transition-all duration-300 group"
    >
      {/* Background Icon */}
      <div className="absolute top-0 right-0 p-4 opacity-5 transform rotate-12 group-hover:scale-110 transition-transform duration-500">
        <stat.icon className="w-24 h-24 text-gray-900 dark:text-gray-100" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 rounded-xl bg-gray-100 dark:bg-gray-700 border border-[#c0c0c0] dark:border-[#8a8a8a]">
            <stat.icon className={`w-6 h-6 ${stat.color}`} />
          </div>
          <div className="flex items-center gap-1 text-xs font-mono text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-full">
            <ArrowUpRight className="w-3 h-3" />
            <span>+2.4%</span>
          </div>
        </div>
        
        <div className="space-y-1">
          <div className="text-4xl font-black tracking-tight text-gray-900 dark:text-gray-100 font-mono stat-number">
            {count}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{stat.label}</p>
        </div>
      </div>
    </div>
  );
};

const DashboardPage = ({ setCurrentPage }) => {
  const { user } = useAuth();

  const stats = [
    { label: 'Total Students', value: '1,245', icon: Users, color: 'text-orange-500 dark:text-orange-400' },
    { label: 'Classrooms', value: '24', icon: Layout, color: 'text-amber-500 dark:text-amber-400' },
    { label: 'Allocated Classrooms', value: '48', icon: MapPin, color: 'text-orange-600 dark:text-orange-500' },
    { label: 'Reports', value: '156', icon: Download, color: 'text-amber-600 dark:text-amber-500' }
  ];

  // UPDATED: Added Database Manager to quick actions
  const quickActions = [
    { label: 'Create Plan', page: 'create-plan', icon: Upload, color: 'bg-orange-500 dark:bg-orange-600' },
    { label: 'Database Manager', page: 'database-manager', icon: Database, color: 'bg-purple-500 dark:bg-purple-600' }, // NEW
    { label: 'Template Editor', page: 'template-editor', icon: Layout, color: 'bg-amber-500 dark:bg-amber-600' },
    { label: 'Classroom Layout', page: 'classroom', icon: MapPin, color: 'bg-orange-600 dark:bg-orange-700' }
  ];

  const activityLog = [
    { id: 1, time: '2 hours ago', message: 'Seat allocation completed for Classroom A', type: 'success' },
    { id: 2, time: '5 hours ago', message: 'Student data uploaded successfully', type: 'success' },
    { id: 3, time: '1 day ago', message: 'PDF report generated', type: 'success' },
    { id: 4, time: '2 days ago', message: 'System synchronized with main database', type: 'info' },
    { id: 5, time: '3 days ago', message: 'Batch CS-2024 allocation initiated', type: 'process' }
  ];

  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState('');
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setShowDownloadModal(true);
    setDownloading(true);
    setDownloadStatus('Starting download...');
    try {
      const res = await fetch('/api/download-report');
      if (!res.ok) throw new Error('No report available');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Report.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setDownloadStatus('Downloaded successfully');
    } catch (e) {
      setDownloadStatus('Failed to download report');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-t-0 border-r-0 border-l-0 border-[#c0c0c0] dark:border-[#8a8a8a] bg-transparent shadow-none dark:shadow-none">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-emerald-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-emerald-500 rounded-full border border-emerald-400"></div>
              </div>
              <span className="text-xs font-mono text-emerald-500 tracking-wider uppercase">Live Connection</span>
            </div>
            <SplitText
              text={`Good Morning,\n${user?.name || 'Administrator'}`}
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              delay={45}
              duration={0.6}
              ease="ease-out"
              splitType="chars"
              onLetterAnimationComplete={() => {}}
            />
          </div>
          
          <div className="flex gap-4">
            <div className="text-right hidden md:block">
              <div className="micro-label mb-1">Current Session</div>
              <div className="font-mono text-xl text-gray-900 dark:text-gray-100">Fall Semester 2025</div>
            </div>
            <div className="w-px bg-gray-200 dark:bg-gray-700 h-12 hidden md:block"></div>
            <div className="text-right">
              <div className="micro-label mb-1">Next Exam</div>
              <div className="font-mono text-xl text-orange-600 dark:text-orange-400">08:00 AM</div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <StatCard key={stat.label} stat={stat} index={i} />
          ))}
        </div>

        {/* Quick Actions */}
        <div className="glass-card p-6 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.22)] dark:shadow-[0_0_26px_rgba(138,138,138,0.24)]">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => action.page === 'download-report' ? handleDownload() : setCurrentPage(action.page)}
                className="flex flex-col items-center gap-3 p-6 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-lg shadow-[0_0_18px_rgba(192,192,192,0.18)] dark:shadow-[0_0_18px_rgba(138,138,138,0.22)] hover:border-orange-500 dark:hover:border-orange-400 hover:shadow-md transition-all duration-300 bg-white dark:bg-gray-800 group"
              >
                <div className={`${action.color} p-3 rounded-lg group-hover:scale-110 transition-transform duration-300`}>
                  <action.icon className="text-white" size={24} />
                </div>
                <span className="font-medium text-gray-700 dark:text-gray-300">{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Activity and Chart Section */}
        <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
          
          {/* Terminal Log */}
          <div className="glass-card p-6 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_28px_rgba(192,192,192,0.2)] dark:shadow-[0_0_28px_rgba(138,138,138,0.24)] flex flex-col min-h-[400px]">
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
              <Terminal className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              <h2 className="text-xl font-bold tracking-widest uppercase text-gray-900 dark:text-gray-100">System Log</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto pr-2 space-y-4 font-mono text-xl">
              {activityLog.map((log, i) => (
                <div
                  key={log.id}
                  className="flex gap-3 group animate-fadeIn"
                  style={{ animationDelay: `${i * 0.1}s` }}
                >
                  <div className="w-28 text-base text-gray-500 dark:text-gray-400 pt-1 shrink-0 flex-none">{log.time}</div>
                  <div className="flex flex-col flex-1 min-w-0">
                    <span className={`text-lg break-words ${
                      log.type === 'warning' ? 'text-amber-500' :
                      log.type === 'success' ? 'text-emerald-500' :
                      log.type === 'process' ? 'text-orange-500' :
                      'text-gray-700 dark:text-gray-300'
                    }`}>
                      {log.type === 'warning' ? '⚠ ' : 
                       log.type === 'success' ? '✓ ' :
                       log.type === 'process' ? '⚙ ' : '> '}
                      {log.message}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Download Modal */}
        {showDownloadModal && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="glass-card w-full max-w-md p-6 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)] animate-fadeIn">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">Download Report</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">{downloadStatus}</p>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => { if (!downloading) setShowDownloadModal(false); }}
                  disabled={downloading}
                  className={`px-4 py-2 rounded-md transition-colors ${
                    downloading 
                      ? 'bg-gray-300 text-gray-600 cursor-not-allowed' 
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {downloading ? 'Downloading…' : 'Close'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
          opacity: 0;
        }
        :global(.dark) .stat-number {
          color: #c0c0c0 !important;
          text-shadow: 0 0 10px rgba(192,192,192,0.95);
          transition: text-shadow 0.3s ease, color 0.3s ease;
        }
      `}</style>
    </div>
  );
};

export default DashboardPage;