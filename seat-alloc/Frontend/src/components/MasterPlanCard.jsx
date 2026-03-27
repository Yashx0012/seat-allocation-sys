import React, { useState, useEffect } from 'react';
import { Download, Loader2, PenTool, Calendar } from 'lucide-react';
import { getToken } from '../utils/tokenStorage';

const MasterPlanCard = ({ planId, showToast }) => {
  const [generating, setGenerating] = useState(false);

  // Form fields
  const [deptName, setDeptName] = useState('Department of Computer Science & Engineering');
  const [examName, setExamName] = useState('Minor-II Examination, November 2025');
  const [dateText, setDateText] = useState('Date: 10th to 14th November, 2025');
  const [title, setTitle] = useState('Master Seating Plan');
  const [leftSignName, setLeftSignName] = useState('');
  const [leftSignTitle, setLeftSignTitle] = useState('Dept. Exam Coordinator');
  const [rightSignName, setRightSignName] = useState('');
  const [rightSignTitle, setRightSignTitle] = useState('Prof. & Head, Department of CSE');

  // Load template config only (plan info comes from parent)
  useEffect(() => {
    const loadTemplate = async () => {
      try {
        const token = getToken();
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const tplRes = await fetch('/api/template/config', { headers });
        if (tplRes.ok) {
          const tplData = await tplRes.json();
          if (tplData.success && tplData.template) {
            const tpl = tplData.template;
            if (tpl.dept_name) setDeptName(tpl.dept_name);
            if (tpl.exam_details) setExamName(tpl.exam_details);
            if (tpl.coordinator_name) setLeftSignName(tpl.coordinator_name);
            if (tpl.coordinator_title) setLeftSignTitle(tpl.coordinator_title);
          }
        }
      } catch (err) {
        console.error('Failed to load template config:', err);
      }
    };
    if (planId) loadTemplate();
  }, [planId]);

  // Generate PDF
  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const token = getToken();
      const response = await fetch('/api/generate-master-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          plan_id: planId,
          dept_name: deptName,
          exam_name: examName,
          date_text: dateText,
          title,
          left_sign_name: leftSignName,
          left_sign_title: leftSignTitle,
          right_sign_name: rightSignName,
          right_sign_title: rightSignTitle,
        }),
      });

      if (!response.ok) throw new Error('Generation failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `master_plan_${planId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      showToast?.('Master plan downloaded successfully!', 'success');
    } catch (err) {
      showToast?.(`Error: ${err.message}`, 'error');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Form Container */}
      <div className="space-y-6 glass-card p-6 rounded-xl">
        {/* Header Section */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Header Information</h3>

          <div>
            <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5">Department Name</label>
            <input
              type="text"
              value={deptName}
              onChange={(e) => setDeptName(e.target.value)}
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:outline-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5">Exam Name</label>
            <input
              type="text"
              value={examName}
              onChange={(e) => setExamName(e.target.value)}
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:outline-none transition-colors"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5 flex items-center gap-1">
                <Calendar size={14} />
                Date
              </label>
              <input
                type="text"
                value={dateText}
                onChange={(e) => setDateText(e.target.value)}
                className="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:outline-none transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 dark:border-gray-700" />

        {/* Signatures Section */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Signatures</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Signature */}
            <div className="space-y-3 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
              <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Left Signature</p>
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  value={leftSignName}
                  onChange={(e) => setLeftSignName(e.target.value)}
                  className="w-full px-3 py-2.5 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:border-purple-500 focus:outline-none transition-colors text-sm"
                  placeholder="Dr. Dheeraj K. Dixit"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Title</label>
                <input
                  type="text"
                  value={leftSignTitle}
                  onChange={(e) => setLeftSignTitle(e.target.value)}
                  className="w-full px-3 py-2.5 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:border-purple-500 focus:outline-none transition-colors text-sm"
                  placeholder="Dept. Exam Coordinator"
                />
              </div>
            </div>

            {/* Right Signature */}
            <div className="space-y-3 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
              <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Right Signature</p>
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  value={rightSignName}
                  onChange={(e) => setRightSignName(e.target.value)}
                  className="w-full px-3 py-2.5 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:border-purple-500 focus:outline-none transition-colors text-sm"
                  placeholder="Dr. Manish Dixit"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Title</label>
                <input
                  type="text"
                  value={rightSignTitle}
                  onChange={(e) => setRightSignTitle(e.target.value)}
                  className="w-full px-3 py-2.5 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:border-purple-500 focus:outline-none transition-colors text-sm"
                  placeholder="Prof. & Head, Department of CSE"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={generating}
        className={`w-full px-6 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all duration-300 ${
          generating
            ? 'bg-purple-400 cursor-not-allowed opacity-70'
            : 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 shadow-lg hover:shadow-purple-500/25'
        } text-white`}
      >
        {generating ? (
          <>
            <Loader2 size={22} className="animate-spin" />
            Generating Master Plan...
          </>
        ) : (
          <>
            <Download size={22} />
            Generate & Download Master Plan
          </>
        )}
      </button>

      <style jsx>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.65);
          backdrop-filter: blur(14px) saturate(140%);
          -webkit-backdrop-filter: blur(14px) saturate(140%);
          border-radius: 16px;
          border: 1px solid rgba(100, 116, 139, 0.18);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.6);
        }
        :global(.dark) .glass-card {
          position: relative;
          background: rgba(17, 24, 39, 0.55);
          backdrop-filter: blur(14px) saturate(130%);
          border-radius: 16px;
        }
        :global(.dark) .glass-card::before {
          content: "";
          position: absolute;
          inset: 0;
          border-radius: inherit;
          padding: 1px;
          background: linear-gradient(180deg, rgba(203, 213, 225, 0.22), rgba(203, 213, 225, 0.08));
          -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          pointer-events: none;
        }
      `}</style>
    </div>
  );
};

export default MasterPlanCard;
