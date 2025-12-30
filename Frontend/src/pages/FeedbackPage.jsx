import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Send, CheckCircle, Paperclip, History, Loader } from 'lucide-react';

const FeedbackPage = ({ showToast }) => {
  const [issueType, setIssueType] = useState('Visual/Aesthetic Issue');
  const [priority, setPriority] = useState('Medium Priority');
  const [description, setDescription] = useState('');
  const [featureSuggestion, setFeatureSuggestion] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previousFeedback, setPreviousFeedback] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const issueOptions = [
    'Functionality Issue', 'Visual/Aesthetic Issue', 'Performance Issue',
    'Security Issue', 'Data/Content Issue', 'Crash/Error Issue',
    'Localization/Internationalization Issue', 'Usability/UX Issue', 'Other'
  ];

  const priorityOptions = [
    { label: 'High Priority', colorClass: 'bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600' },
    { label: 'Medium Priority', colorClass: 'bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-500 dark:hover:bg-yellow-600' },
    { label: 'Low Priority', colorClass: 'bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600' },
  ];

  useEffect(() => {
    if (showHistory) {
      fetchPreviousFeedback();
    }
  }, [showHistory]);

  const fetchPreviousFeedback = async () => {
    setIsLoadingHistory(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/feedback', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPreviousFeedback(data.feedback || []);
      } else {
        showToast('Failed to load feedback history', 'error');
      }
    } catch (error) {
      console.error('Error fetching feedback:', error);
      showToast('Error loading feedback history', 'error');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSubmit = async () => {
    if (!description.trim()) {
      showToast('Please provide a description', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      
      formData.append('issueType', issueType);
      formData.append('priority', priority);
      formData.append('description', description);
      formData.append('featureSuggestion', featureSuggestion);
      formData.append('additionalInfo', additionalInfo);
      
      if (imageFile) {
        formData.append('file', imageFile);
      }

      const response = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsSubmitted(true);
        if (showToast) showToast('Feedback submitted successfully!', 'success');

        setTimeout(() => {
          setIssueType('Visual/Aesthetic Issue');
          setPriority('Medium Priority');
          setDescription('');
          setFeatureSuggestion('');
          setAdditionalInfo('');
          setImageFile(null);
          setIsSubmitted(false);
          
          if (showHistory) {
            fetchPreviousFeedback();
          }
        }, 2000);
      } else {
        showToast(data.error || 'Failed to submit feedback', 'error');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      showToast('Error submitting feedback. Please try again.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      resolved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${statusColors[status] || statusColors.pending}`}>
        {status || 'pending'}
      </span>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8 min-h-screen p-8"
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-4 py-2 rounded-full mb-6 font-bold text-sm uppercase tracking-widest">
            <MessageCircle size={16} />
            Help Us Improve
          </div>
          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter text-gray-900 dark:text-white mb-4">
            Feedback & Support
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Found a bug or have a feature suggestion? We'd love to hear from you. Your feedback helps us build a better system.
          </p>

          <motion.button
            onClick={() => setShowHistory(!showHistory)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="mt-6 inline-flex items-center gap-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition font-bold text-sm uppercase tracking-wide"
          >
            <History size={16} />
            {showHistory ? 'Hide History' : 'View Previous Feedback'}
          </motion.button>
        </motion.div>

        {/* Feedback History - GLASS CARD */}
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8 glass-card p-6"
          >
            <h3 className="text-xl font-bold uppercase tracking-tight text-gray-900 dark:text-white mb-4">
              Your Feedback History
            </h3>
            
            {isLoadingHistory ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="animate-spin text-blue-600 dark:text-blue-400" size={32} />
              </div>
            ) : previousFeedback.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No previous feedback submitted
              </p>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {previousFeedback.map((feedback) => (
                  <div
                    key={feedback.id}
                    className="glass-card-light p-4"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                          {feedback.issue_type}
                        </span>
                        {getStatusBadge(feedback.status)}
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDate(feedback.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                      {feedback.description}
                    </p>
                    {feedback.admin_response && (
                      <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600/50">
                        <p className="text-xs font-bold text-blue-600 dark:text-blue-400 mb-1">Admin Response:</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {feedback.admin_response}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Success Message */}
        {isSubmitted && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8 bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-400 p-6 rounded-2xl flex items-center gap-4 shadow-lg"
          >
            <CheckCircle className="text-green-600 dark:text-green-400 w-8 h-8 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-green-800 dark:text-green-300 text-lg uppercase tracking-tight">Thank You!</h3>
              <p className="text-green-700 dark:text-green-400 text-sm mt-1">Your feedback has been successfully submitted.</p>
            </div>
          </motion.div>
        )}

        {/* Main Form Card - GLASS CARD */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="glass-card p-8 md:p-12"
        >
          <div className="space-y-10">
            
            {/* Issue Type Selection */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-4 block">
                1. Reason for Reporting
              </label>
              <div className="flex flex-wrap gap-2">
                {issueOptions.map(issue => (
                  <motion.button
                    key={issue}
                    onClick={() => setIssueType(issue)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`px-4 py-2 text-xs font-bold uppercase tracking-wide rounded-xl transition-all duration-200 border-2 ${
                      issueType === issue
                        ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-500 dark:border-blue-400 shadow-lg'
                        : 'bg-gray-100 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600/50 hover:border-blue-400'
                    }`}
                  >
                    {issue}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-2 block">
                2. Detailed Description *
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="6"
                placeholder="Provide a detailed description including steps to reproduce, expected behavior, and actual behavior..."
                required
                className="w-full bg-white/50 dark:bg-gray-900/50 text-gray-900 dark:text-white border-2 border-gray-200 dark:border-gray-700/50 rounded-xl p-4 font-mono text-sm focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all backdrop-blur-sm"
              />
            </div>

            {/* Feature Suggestion */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-2 block">
                3. Feature Suggestions (Optional)
              </label>
              <textarea
                value={featureSuggestion}
                onChange={(e) => setFeatureSuggestion(e.target.value)}
                rows="4"
                placeholder="Describe any new features or improvements you'd like to see..."
                className="w-full bg-white/50 dark:bg-gray-900/50 text-gray-900 dark:text-white border-2 border-gray-200 dark:border-gray-700/50 rounded-xl p-4 font-mono text-sm focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all backdrop-blur-sm"
              />
            </div>

            {/* Priority Selection */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-4 block">
                4. Priority Level
              </label>
              <div className="flex flex-wrap gap-4">
                {priorityOptions.map(opt => (
                  <motion.button
                    key={opt.label}
                    onClick={() => setPriority(opt.label)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`px-6 py-3 text-sm font-bold uppercase tracking-wide rounded-xl text-white transition-all duration-200 border-2 border-transparent shadow-md ${
                      priority === opt.label
                        ? opt.colorClass
                        : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500'
                    }`}
                  >
                    {opt.label}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* File Upload */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-3 block">
                5. Attach Files (Screenshots/Logs)
              </label>
              <label className="flex items-center gap-3 p-4 border-2 border-dashed border-gray-300 dark:border-gray-700/50 rounded-xl hover:border-blue-400 dark:hover:border-blue-400 transition-colors cursor-pointer group backdrop-blur-sm">
                <Paperclip className="text-gray-400 group-hover:text-blue-600 transition-colors w-6 h-6" />
                <span className="text-sm font-bold text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  {imageFile ? imageFile.name : 'Choose file or drag & drop'}
                </span>
                <input
                  type="file"
                  accept="image/*,video/*,.log,.txt"
                  onChange={(e) => setImageFile(e.target.files[0])}
                  className="hidden"
                />
              </label>
            </div>

            {/* Additional Info */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-2 block">
                6. Additional Information
              </label>
              <textarea
                value={additionalInfo}
                onChange={(e) => setAdditionalInfo(e.target.value)}
                rows="4"
                placeholder="Error logs, console outputs, browser info, or any additional context..."
                className="w-full bg-white/50 dark:bg-gray-900/50 text-gray-900 dark:text-white border-2 border-gray-200 dark:border-gray-700/50 rounded-xl p-4 font-mono text-sm focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all backdrop-blur-sm"
              />
            </div>

            {/* Submit Button */}
            <motion.button
              onClick={handleSubmit}
              disabled={isSubmitting}
              whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
              whileTap={{ scale: isSubmitting ? 1 : 0.98 }}
              className="w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold uppercase tracking-wide rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader className="animate-spin" size={20} />
                  Submitting...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Submit Feedback
                </>
              )}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default FeedbackPage;