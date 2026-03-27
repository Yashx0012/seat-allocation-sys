import React, { useState, useEffect } from 'react';
import { X, ArrowRight, Save, link } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const OptimizationConfigModal = ({ isOpen, onClose, selectedBatches = [], allBatches = [], onSaveSuccessors, initialSuccessors = {} }) => {
  const [successors, setSuccessors] = useState(initialSuccessors);

  // Reset when opened
  useEffect(() => {
    if (isOpen) {
      setSuccessors(initialSuccessors || {});
    }
  }, [isOpen, initialSuccessors]);

  const handleSuccessorChange = (batchId, nextBatchId) => {
    setSuccessors(prev => ({
      ...prev,
      // Store as string (or whatever the generic value is) to ensure matching with Option value
      [batchId]: (!nextBatchId || nextBatchId === "none") ? null : nextBatchId
    }));
  };

  const handleSave = () => {
    onSaveSuccessors(successors);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
              Optimization Chain
            </h3>
            <button 
              onClick={onClose}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
            >
              <X size={20} className="text-gray-500" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              When a batch finishes filling its allocated columns, which batch should be used to fill the remaining seats?
            </p>

            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
              {selectedBatches.map(batch => (
                <div key={batch.id} className="flex items-center gap-3 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
                  {/* Origin Batch */}
                  <div className="flex items-center gap-2 min-w-[120px]">
                    <div 
                      className="w-3 h-3 rounded-full shadow-sm"
                      style={{ backgroundColor: batch.color }}
                    />
                    <span className="font-semibold text-gray-700 dark:text-gray-200 text-sm">
                      {batch.label}
                    </span>
                  </div>

                  <ArrowRight size={16} className="text-gray-400" />

                  {/* Successor Select */}
                  <select
                    value={successors[batch.id] || "none"}
                    onChange={(e) => handleSuccessorChange(batch.id, e.target.value)}
                    className="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-shadow"
                  >
                    <option value="none" className="text-gray-400">-- Stop / Auto --</option>
                    {/* Use allBatches instead of selectedBatches */}
                    {(allBatches.length > 0 ? allBatches : selectedBatches)
                      .filter(b => b.batch_id !== batch.id && b.id !== batch.id) // Exclude self (handle both id formats)
                      .map(optBatch => (
                        <option key={optBatch.batch_id || optBatch.id} value={optBatch.batch_id || optBatch.id}>
                           Fill with {optBatch.batch_name || optBatch.label}
                        </option>
                      ))
                    }
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex justification-end gap-3 justify-end">
            <button 
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button 
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-all active:scale-95"
            >
              <Save size={16} />
              Save Strategy
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default OptimizationConfigModal;
