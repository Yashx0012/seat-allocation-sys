import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, BookOpen, FileText } from 'lucide-react';

const ExamTypeSelector = ({ onSelect, isOpen }) => {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full p-8"
      >
        <h2 className="text-3xl font-bold text-center mb-2 text-slate-900 dark:text-white">
          Choose Exam Type
        </h2>
        <p className="text-center text-slate-600 dark:text-slate-400 mb-8">
          Select how you want to manage this exam
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Minor Exam Card */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect('minor')}
            className="relative p-8 border-2 border-slate-200 dark:border-slate-700 rounded-xl hover:border-indigo-500 dark:hover:border-indigo-400 transition-all group"
          >
            <div className="text-center">
              <div className="mb-4 inline-block p-4 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <BookOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-slate-900 dark:text-white">
                Minor Exam
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Standard exam planning with batch-wise allocation
              </p>
              <ul className="mt-4 text-xs text-slate-500 dark:text-slate-400 space-y-1">
                <li>✓ Permanent database storage</li>
                <li>✓ Batch-based seating</li>
                <li>✓ Full template access</li>
              </ul>
            </div>
          </motion.button>

          {/* Major Exam Card */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect('major')}
            className="relative p-8 border-2 border-indigo-500 dark:border-indigo-600 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 hover:shadow-lg transition-all group"
          >
            <div className="absolute top-3 right-3">
              <span className="px-2 py-1 bg-indigo-500 text-white text-xs font-bold rounded">
                NEW
              </span>
            </div>
            <div className="text-center">
              <div className="mb-4 inline-block p-4 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg">
                <FileText className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-slate-900 dark:text-white">
                Major Exam
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Upload student data with names, codes, passwords
              </p>
              <ul className="mt-4 text-xs text-slate-500 dark:text-slate-400 space-y-1">
                <li>✓ Direct file upload</li>
                <li>✓ Full student metadata</li>
                <li>✓ Dynamic allocation</li>
              </ul>
            </div>
          </motion.button>
        </div>

        <p className="text-xs text-center text-slate-500 dark:text-slate-400 mt-8">
          You can switch exam types anytime from the dashboard
        </p>
      </motion.div>
    </motion.div>
  );
};

export default ExamTypeSelector;
