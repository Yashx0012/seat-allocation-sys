import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle, CheckCircle, Save, Calendar, Users } from 'lucide-react';
import StyledInput from '../components/Template/StyledInput.jsx';
import StyledButton from '../components/Template/StyledButton.jsx';

/**
 * MajorAttendanceForm Modal Component
 * 
 * Usage:
 * const [showForm, setShowForm] = useState(false);
 * const handleDownload = async (data) => {
 *   // API call with data
 *   setShowForm(false);
 * };
 * <MajorAttendanceForm isOpen={showForm} onClose={() => setShowForm(false)} onSubmit={handleDownload} />
 */

function MajorAttendanceForm({ isOpen, onClose, onSubmit, loading = false }) {
    const [formData, setFormData] = useState({
        exam_name: '',
        examDate: '',
        department: '',
        course_name: '',
        course_code: '',
        invigilator1: '',
        invigilator2: '',
        invigilator3: '',
        notes: ''
    });

    const [errors, setErrors] = useState({});
    const [submitted, setSubmitted] = useState(false);

    // Reset form when modal opens
    useEffect(() => {
        if (isOpen) {
            setSubmitted(false);
            setErrors({});
        }
    }, [isOpen]);

    const validateForm = () => {
        const newErrors = {};

        if (!formData.exam_name.trim()) {
            newErrors.exam_name = 'Exam name is required';
        }

        if (!formData.examDate) {
            newErrors.examDate = 'Exam date is required';
        }

        if (!formData.department.trim()) {
            newErrors.department = 'Department is required';
        }

        if (!formData.course_name.trim()) {
            newErrors.course_name = 'Course name is required';
        }

        if (!formData.course_code.trim()) {
            newErrors.course_code = 'Course code is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error for this field when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setSubmitted(true);

        try {
            await onSubmit(formData);
            // Reset form after successful submission
            setFormData({
                exam_name: '',
                examDate: '',
                department: '',
                course_name: '',
                course_code: '',
                invigilator1: '',
                invigilator2: '',
                invigilator3: '',
                notes: ''
            });
        } catch (error) {
            console.error('Form submission error:', error);
            setErrors({ submit: error.message || 'Failed to process form' });
        } finally {
            setSubmitted(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 z-40"
                        onClick={onClose}
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ duration: 0.2 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4"
                        onClick={onClose}
                    >
                        <motion.div
                            className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-800"
                            onClick={(e) => e.stopPropagation()}
                            layout
                        >
                            {/* Header */}
                            <div className="sticky top-0 flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Attendance Metadata
                                </h2>
                                <button
                                    type="button"
                                    onClick={onClose}
                                    disabled={loading}
                                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                    <X size={20} className="text-gray-500 dark:text-gray-400" />
                                </button>
                            </div>

                            {/* Form */}
                            <form onSubmit={handleSubmit} className="p-6 space-y-5">

                                {/* Exam Name */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                        Exam Name *
                                    </label>
                                    <StyledInput
                                        type="text"
                                        name="exam_name"
                                        value={formData.exam_name}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Major-I Examination"
                                        disabled={loading}
                                    />
                                    {errors.exam_name && (
                                        <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                                            <AlertCircle size={14} /> {errors.exam_name}
                                        </p>
                                    )}
                                </div>

                                {/* Exam Date */}
                                <div className="space-y-2">
                                    <label className="flex text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide items-center gap-2">
                                        <Calendar size={16} className="text-orange-500" />
                                        Exam Date *
                                    </label>
                                    <StyledInput
                                        type="date"
                                        name="examDate"
                                        value={formData.examDate}
                                        onChange={handleInputChange}
                                        disabled={loading}
                                    />
                                    {errors.examDate && (
                                        <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                                            <AlertCircle size={14} /> {errors.examDate}
                                        </p>
                                    )}
                                </div>

                                {/* Department */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                        Department *
                                    </label>
                                    <StyledInput
                                        type="text"
                                        name="department"
                                        value={formData.department}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Computer Science & Engineering"
                                        disabled={loading}
                                    />
                                    {errors.department && (
                                        <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                                            <AlertCircle size={14} /> {errors.department}
                                        </p>
                                    )}
                                </div>

                                {/* Course Name */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                        Course Name *
                                    </label>
                                    <StyledInput
                                        type="text"
                                        name="course_name"
                                        value={formData.course_name}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Data Structures"
                                        disabled={loading}
                                    />
                                    {errors.course_name && (
                                        <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                                            <AlertCircle size={14} /> {errors.course_name}
                                        </p>
                                    )}
                                </div>

                                {/* Course Code */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                        Course Code *
                                    </label>
                                    <StyledInput
                                        type="text"
                                        name="course_code"
                                        value={formData.course_code}
                                        onChange={handleInputChange}
                                        placeholder="e.g., CSE2001"
                                        disabled={loading}
                                    />
                                    {errors.course_code && (
                                        <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                                            <AlertCircle size={14} /> {errors.course_code}
                                        </p>
                                    )}
                                </div>

                                {/* INVIGILATORS SECTION */}
                                <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-2">
                                    <div className="mb-4">
                                        <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-3 flex items-center gap-2">
                                            <Users size={16} className="text-blue-500" />
                                            Invigilators
                                        </h3>

                                        {/* Chief Invigilator */}
                                        <div className="space-y-2 mb-3">
                                            <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
                                                Chief Invigilator
                                            </label>
                                            <StyledInput
                                                type="text"
                                                name="invigilator1"
                                                value={formData.invigilator1}
                                                onChange={handleInputChange}
                                                placeholder="Name of chief invigilator"
                                                disabled={loading}
                                            />
                                        </div>

                                        {/* Invigilator 2 */}
                                        <div className="space-y-2 mb-3">
                                            <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
                                                Invigilator 2
                                            </label>
                                            <StyledInput
                                                type="text"
                                                name="invigilator2"
                                                value={formData.invigilator2}
                                                onChange={handleInputChange}
                                                placeholder="Name (optional)"
                                                disabled={loading}
                                            />
                                        </div>

                                        {/* Invigilator 3 */}
                                        <div className="space-y-2">
                                            <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
                                                Invigilator 3
                                            </label>
                                            <StyledInput
                                                type="text"
                                                name="invigilator3"
                                                value={formData.invigilator3}
                                                onChange={handleInputChange}
                                                placeholder="Name (optional)"
                                                disabled={loading}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Notes (Optional) */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                        Additional Notes
                                    </label>
                                    <StyledInput
                                        type="textarea"
                                        name="notes"
                                        value={formData.notes}
                                        onChange={handleInputChange}
                                        placeholder="Optional notes or remarks..."
                                        rows="2"
                                        disabled={loading}
                                    />
                                </div>

                                {/* Submit Error */}
                                {errors.submit && (
                                    <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
                                        <AlertCircle size={18} className="text-red-600 dark:text-red-400 flex-shrink-0" />
                                        <p className="text-sm text-red-700 dark:text-red-300">{errors.submit}</p>
                                    </div>
                                )}

                                {/* Actions */}
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
                                                Generate PDF
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

export default MajorAttendanceForm;
