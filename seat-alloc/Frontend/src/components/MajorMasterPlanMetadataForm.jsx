import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle, CheckCircle } from 'lucide-react';

const defaultForm = {
  exam_name: '',
  department: '',
  course_name: '',
  course_code: '',
  examDate: '',
  invigilator1: '',
  invigilator2: '',
  invigilator3: ''
};

function MajorMasterPlanMetadataForm({ isOpen, onClose, onSubmit, initialData = {}, loading = false }) {
  const [formData, setFormData] = useState(defaultForm);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isOpen) {
      setFormData({
        ...defaultForm,
        ...initialData
      });
      setErrors({});
    }
  }, [isOpen, initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const next = {};
    if (!formData.exam_name.trim()) next.exam_name = 'Exam name is required';
    if (!formData.department.trim()) next.department = 'Department is required';
    if (!formData.course_name.trim()) next.course_name = 'Course name is required';
    if (!formData.course_code.trim()) next.course_code = 'Course code is required';
    if (!formData.examDate) next.examDate = 'Exam date is required';
    if (!formData.invigilator1.trim()) next.invigilator1 = 'Chief invigilator is required';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit(formData);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 z-40"
            onClick={onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          >
            <motion.div
              className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-800"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="sticky top-0 flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Master Plan Metadata</h2>
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500 dark:text-gray-400" />
                </button>
              </div>

              <form onSubmit={submit} className="p-6 space-y-4">
                {[
                  ['exam_name', 'Exam Name'],
                  ['department', 'Department'],
                  ['course_name', 'Course Name'],
                  ['course_code', 'Course Code'],
                  ['invigilator1', 'Chief Invigilator']
                ].map(([key, label]) => (
                  <div key={key}>
                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-1">
                      {label} *
                    </label>
                    <input
                      name={key}
                      value={formData[key] || ''}
                      onChange={handleChange}
                      disabled={loading}
                      className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />
                    {errors[key] && (
                      <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1 mt-1">
                        <AlertCircle size={13} /> {errors[key]}
                      </p>
                    )}
                  </div>
                ))}

                <div>
                  <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-1">
                    Exam Date *
                  </label>
                  <input
                    type="date"
                    name="examDate"
                    value={formData.examDate || ''}
                    onChange={handleChange}
                    disabled={loading}
                    className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                  {errors.examDate && (
                    <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1 mt-1">
                      <AlertCircle size={13} /> {errors.examDate}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-1">
                      Invigilator 2
                    </label>
                    <input
                      name="invigilator2"
                      value={formData.invigilator2 || ''}
                      onChange={handleChange}
                      disabled={loading}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-1">
                      Invigilator 3
                    </label>
                    <input
                      name="invigilator3"
                      value={formData.invigilator3 || ''}
                      onChange={handleChange}
                      disabled={loading}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={onClose}
                    disabled={loading}
                    className="flex-1 px-4 py-2.5 bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors font-semibold disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg hover:from-orange-600 hover:to-amber-600 transition-all duration-200 font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <CheckCircle size={18} />
                        Download Master Plan
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default MajorMasterPlanMetadataForm;
