import React, { useState, useEffect } from 'react';
import SplitText from '../components/SplitText';
import { ClipboardList, Download, FileText, Search, Printer, X, Loader2, UserCheck, Calendar, Hash, Eye } from 'lucide-react';

const AttendancePage = ({ showToast }) => {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(null); 
  const [searchTerm, setSearchTerm] = useState("");
  const [previewData, setPreviewData] = useState(null);

  useEffect(() => {
    fetchAllocations();
  }, []);

  const fetchAllocations = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/allocations');
      if (!response.ok) throw new Error("Failed to fetch batches");
      const data = await response.json();
      setAllocations(data);
    } catch (err) {
      showToast("Could not load allocations", "error");
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async (batch) => {
    setActionLoading(`preview-${batch.id}`);
    try {
      const response = await fetch(`/api/students?batch_id=${batch.id}`);
      if (!response.ok) throw new Error("Preview failed");
      const students = await response.json();
      setPreviewData({
        batch_name: batch.batch_name,
        students: students
      });
    } catch (err) {
      showToast("Error loading preview", "error");
    } finally {
      setActionLoading(null);
    }
  };

  const handlePrint = async (batch) => {
    setActionLoading(`print-${batch.id}`);
    try {
      const studentRes = await fetch(`/api/students?batch_id=${batch.id}`);
      const students = await studentRes.json();

      const response = await fetch('/api/generate-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          seating: [students], 
          batch_name: batch.batch_name
        }),
      });

      if (!response.ok) throw new Error("PDF generation failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `Attendance_${batch.batch_name}.pdf`;
      document.body.appendChild(link);
      link.click(); 
      link.remove();
      window.URL.revokeObjectURL(url); 
      
      showToast("PDF Downloaded successfully", "success");
    } catch (err) {
      console.error(err);
      showToast("Error generating PDF", "error");
    } finally {
      setActionLoading(null);
    }
  };

  const filteredAllocations = allocations.filter(a => 
    a.batch_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_4px_26px_rgba(192,192,192,0.22)] dark:shadow-[0_4px_26px_rgba(138,138,138,0.22)]">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Attendance Management</span>
            </div>
            <SplitText
              text={`Attendance Sheets`}
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              splitType="chars"
              delay={30}
            />
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Generate printable signature sheets for allocated batches
            </p>
          </div>
          
          <div className="flex gap-4">
            <div className="text-right">
              <div className="micro-label mb-1">Total Batches</div>
              <div className="font-mono text-2xl text-orange-600 dark:text-orange-400 stat-number">{allocations.length}</div>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="glass-card p-6 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input 
              type="text"
              placeholder="Search batches by name..."
              className="w-full pl-12 pr-4 py-3.5 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:border-orange-500 dark:focus:border-orange-400 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all duration-200"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {/* Table Card */}
        <div className="glass-card overflow-hidden border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-gray-500">
              <Loader2 className="animate-spin mb-4 text-orange-500" size={40} />
              <p className="text-gray-600 dark:text-gray-400 font-medium">Loading batches...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b-2 border-[#c0c0c0] dark:border-[#8a8a8a]">
                    <th className="px-6 py-4 text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                      <div className="flex items-center gap-2">
                        <ClipboardList className="text-orange-500" size={18} />
                        Batch Details
                      </div>
                    </th>
                    <th className="px-6 py-4 text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                      <div className="flex items-center gap-2">
                        <Calendar className="text-orange-500" size={18} />
                        Date Created
                      </div>
                    </th>
                    <th className="px-6 py-4 text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300 text-right">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#d9d9d9] dark:divide-[#6b6b6b]">
                  {filteredAllocations.map((batch, idx) => (
                    <tr 
                      key={batch.id} 
                      className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
                      style={{
                        animation: `fadeIn 0.3s ease-out ${idx * 0.05}s forwards`,
                        opacity: 0
                      }}
                    >
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-white font-bold shadow-md">
                            {idx + 1}
                          </div>
                          <div>
                            <div className="font-bold text-gray-900 dark:text-white group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                              {batch.batch_name}
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-1">
                              <Hash size={12} />
                              ID: {batch.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <Calendar size={16} className="text-gray-400" />
                          <span className="font-mono text-sm">
                            {batch.date ? new Date(batch.date).toLocaleDateString() : 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex justify-end gap-2">
                          <button 
                            onClick={() => handlePreview(batch)}
                            disabled={!!actionLoading}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-all duration-200 border-2 border-transparent hover:border-orange-500 dark:hover:border-orange-400 disabled:opacity-50 disabled:cursor-not-allowed group"
                          >
                            {actionLoading === `preview-${batch.id}` ? (
                              <Loader2 className="animate-spin" size={16}/>
                            ) : (
                              <Eye size={16} className="group-hover:scale-110 transition-transform" />
                            )}
                            Preview
                          </button>
                          <button 
                            onClick={() => handlePrint(batch)}
                            disabled={!!actionLoading}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed group"
                          >
                            {actionLoading === `print-${batch.id}` ? (
                              <Loader2 className="animate-spin" size={16}/>
                            ) : (
                              <Printer size={16} className="group-hover:scale-110 transition-transform" />
                            )}
                            Print PDF
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!loading && filteredAllocations.length === 0 && (
            <div className="py-20 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 mb-4">
                <ClipboardList className="text-gray-400 dark:text-gray-500" size={32} />
              </div>
              <p className="text-gray-600 dark:text-gray-400 font-semibold text-lg mb-2">No batches found</p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                {searchTerm ? 'Try adjusting your search criteria' : 'Create your first batch to get started'}
              </p>
            </div>
          )}
        </div>

        {/* Preview Modal */}
        {previewData && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
            <div className="glass-card w-full max-w-3xl max-h-[85vh] overflow-hidden flex flex-col border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_32px_rgba(192,192,192,0.26)] dark:shadow-[0_0_32px_rgba(138,138,138,0.28)] animate-fadeInUp">
              
              {/* Modal Header */}
              <div className="p-6 border-b-2 border-[#c0c0c0] dark:border-[#8a8a8a] flex justify-between items-center bg-gradient-to-r from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Eye className="text-orange-500" size={20} />
                    <span className="text-xs font-mono text-orange-500 uppercase tracking-wider">Preview Mode</span>
                  </div>
                  <h2 className="font-bold text-2xl text-gray-900 dark:text-white">{previewData.batch_name}</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Total Students: {previewData.students.length}
                  </p>
                </div>
                <button 
                  onClick={() => setPreviewData(null)} 
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors group"
                >
                  <X size={24} className="text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors" />
                </button>
              </div>
              
              {/* Modal Body - Scrollable Table */}
              <div className="flex-1 overflow-y-auto p-6">
                <div className="border border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl overflow-hidden shadow-[0_0_22px_rgba(192,192,192,0.22)] dark:shadow-[0_0_22px_rgba(138,138,138,0.24)]">
                  <table className="w-full text-sm">
                    <thead className="bg-gradient-to-r from-orange-500 to-amber-500 text-white sticky top-0">
                      <tr>
                        <th className="text-left p-4 font-bold uppercase tracking-wide">#</th>
                        <th className="text-left p-4 font-bold uppercase tracking-wide">Enrollment</th>
                        <th className="text-left p-4 font-bold uppercase tracking-wide">Name</th>
                        <th className="text-left p-4 font-bold uppercase tracking-wide">Signature</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800">
                      {previewData.students.map((student, idx) => (
                        <tr 
                          key={idx}
                          className="hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                        >
                          <td className="p-4 text-gray-500 dark:text-gray-400 font-semibold">{idx + 1}</td>
                          <td className="p-4 font-mono font-semibold text-gray-900 dark:text-gray-200">{student.enrollment}</td>
                          <td className="p-4 text-gray-700 dark:text-gray-300">{student.name || '---'}</td>
                          <td className="p-4">
                            <div className="h-8 border-b-2 border-dashed border-[#c0c0c0] dark:border-[#8a8a8a]"></div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Modal Footer */}
              <div className="p-6 border-t-2 border-[#c0c0c0] dark:border-[#8a8a8a] flex justify-end gap-3 bg-gray-50 dark:bg-gray-800/50">
                <button 
                  onClick={() => setPreviewData(null)} 
                  className="px-6 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200"
                >
                  Close
                </button>
                <button 
                  onClick={() => {
                    const batch = allocations.find(b => b.batch_name === previewData.batch_name);
                    if (batch) handlePrint(batch);
                  }}
                  className="px-6 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg font-semibold hover:from-orange-600 hover:to-amber-600 transition-all duration-200 shadow-md hover:shadow-lg flex items-center gap-2"
                >
                  <Printer size={18} />
                  Print This Sheet
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

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

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-fadeInUp {
          animation: fadeInUp 0.4s ease-out;
        }
      `}</style>
    </div>
  );
};

export default AttendancePage;