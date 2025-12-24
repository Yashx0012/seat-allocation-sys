import React, { useState, useEffect } from 'react';
import { ClipboardList, Download, FileText, Search, Printer, X, Loader2, UserCheck } from 'lucide-react';

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
      // FIX: Since this is a separate page, we fetch the students for this batch 
      // to pass them to the PDF generator.
      const studentRes = await fetch(`/api/students?batch_id=${batch.id}`);
      const students = await studentRes.json();

      const response = await fetch('/api/generate-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          // We wrap students in a list to match the 'seating_data' expectation 
          // of the flatten logic in your Python script
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8 transition-colors duration-300">
      <div className="max-w-6xl mx-auto">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white flex items-center gap-3">
              <UserCheck className="text-blue-600" size={32} />
              Attendance Sheets
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Generate printable signature sheets for allocated batches.</p>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text"
              placeholder="Search batches..."
              className="pl-10 pr-4 py-2 w-full md:w-64 border rounded-md bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-md shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-gray-500">
              <Loader2 className="animate-spin mb-2" size={32} />
              <p>Loading batches...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-4 text-sm font-semibold text-gray-600 dark:text-gray-300">Batch Details</th>
                    <th className="px-6 py-4 text-sm font-semibold text-gray-600 dark:text-gray-300">Date Created</th>
                    <th className="px-6 py-4 text-sm font-semibold text-gray-600 dark:text-gray-300 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {filteredAllocations.map((batch) => (
                    <tr key={batch.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900 dark:text-white">{batch.batch_name}</div>
                        <div className="text-xs text-gray-500">ID: {batch.id}</div>
                      </td>
                      <td className="px-6 py-4 text-gray-600 dark:text-gray-400 text-sm">
                        {batch.date ? new Date(batch.date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <button 
                            onClick={() => handlePreview(batch)}
                            disabled={!!actionLoading}
                            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition"
                          >
                            {actionLoading === `preview-${batch.id}` ? <Loader2 className="animate-spin" size={16}/> : <FileText size={16} />}
                            Preview
                          </button>
                          <button 
                            onClick={() => handlePrint(batch)}
                            disabled={!!actionLoading}
                            className="flex items-center gap-2 px-4 py-1.5 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-md transition shadow-sm"
                          >
                            {actionLoading === `print-${batch.id}` ? <Loader2 className="animate-spin" size={16}/> : <Printer size={16} />}
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
            <div className="py-20 text-center text-gray-500 dark:text-gray-400">
              No batches found.
            </div>
          )}
        </div>

        {/* --- PREVIEW MODAL --- */}
        {previewData && (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-md w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
              <div className="p-6 border-b dark:border-gray-700 flex justify-between items-center">
                <h2 className="font-bold text-xl text-gray-900 dark:text-white">{previewData.batch_name}</h2>
                <button onClick={() => setPreviewData(null)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">
                  <X size={24} className="text-gray-500" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-6">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr className="text-gray-600 dark:text-gray-300 uppercase text-xs">
                      <th className="text-left p-3">S.No</th>
                      <th className="text-left p-3">Enrollment</th>
                      <th className="text-left p-3">Name</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y dark:divide-gray-700">
                    {previewData.students.map((student, idx) => (
                      <tr key={idx}>
                        <td className="p-3 text-gray-500">{idx + 1}</td>
                        <td className="p-3 font-mono dark:text-gray-200">{student.enrollment}</td>
                        <td className="p-3 dark:text-gray-300">{student.name || '---'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-4 border-t dark:border-gray-700 text-right">
                <button onClick={() => setPreviewData(null)} className="px-6 py-2 bg-gray-900 dark:bg-blue-600 text-white rounded-md">
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AttendancePage;