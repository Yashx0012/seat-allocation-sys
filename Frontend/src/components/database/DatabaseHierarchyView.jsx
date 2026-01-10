// src/components/database/DatabaseHierarchyView.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Folder,
  FolderOpen,
  Users,
  Calendar,
  Loader2,
  AlertCircle,
  Trash2,
  RefreshCw
} from 'lucide-react';
import useDatabaseApi from './hooks/useDatabaseApi';
import DeleteConfirmModal from './DeleteConfirmModal';

const DatabaseHierarchyView = ({ onToast }) => {
  const [hierarchy, setHierarchy] = useState([]);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [expandedBatches, setExpandedBatches] = useState({});
  const [deleteModal, setDeleteModal] = useState({ open: false, type: null, data: null });
  const [isDeleting, setIsDeleting] = useState(false);

  const { loading, error, fetchHierarchy, deleteBatch, deleteSession } = useDatabaseApi();

  const loadData = useCallback(async () => {
    const data = await fetchHierarchy();
    setHierarchy(data || []);
  }, [fetchHierarchy]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleSession = (sessionId) => {
    setExpandedSessions(prev => ({ ...prev, [sessionId]: !prev[sessionId] }));
  };

  const toggleBatch = (batchId) => {
    setExpandedBatches(prev => ({ ...prev, [batchId]: !prev[batchId] }));
  };

  const handleDeleteBatch = (uploadId, batchName) => {
    setDeleteModal({ open: true, type: 'batch', data: { uploadId, batchName } });
  };

  const handleDeleteSession = (sessionId, planId) => {
    setDeleteModal({ open: true, type: 'session', data: { sessionId, planId } });
  };

  const confirmDelete = async () => {
    setIsDeleting(true);
    const { type, data } = deleteModal;

    let result;
    if (type === 'batch') {
      result = await deleteBatch(data.uploadId);
    } else {
      result = await deleteSession(data.sessionId);
    }

    setIsDeleting(false);
    setDeleteModal({ open: false, type: null, data: null });

    if (result.success) {
      onToast?.(result.message, 'success');
      loadData();
    } else {
      onToast?.(result.error || 'Delete failed', 'error');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      expired: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
    };
    return styles[status] || styles.draft;
  };

  if (loading && hierarchy.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (error && hierarchy.length === 0) {
    return (
      <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-start gap-4">
        <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
        <div>
          <h3 className="font-semibold text-red-900 dark:text-red-400">Error Loading Data</h3>
          <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
          <button onClick={loadData} className="mt-3 text-sm text-red-600 hover:text-red-800 flex items-center gap-1">
            <RefreshCw className="w-4 h-4" /> Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {hierarchy.length === 0 ? (
          <div className="text-center py-16 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl">
            <Folder className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 font-medium">No allocations found</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Upload student data to get started</p>
          </div>
        ) : (
          hierarchy.map((session) => (
            <div key={session.session_id} className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-white dark:bg-gray-800">
              {/* Session Row */}
              <div
                onClick={() => toggleSession(session.session_id)}
                className="flex items-center gap-3 p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors group"
              >
                <div className="text-gray-400">
                  {expandedSessions[session.session_id] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                </div>

                {expandedSessions[session.session_id] ? (
                  <FolderOpen className="w-5 h-5 text-blue-500" />
                ) : (
                  <Folder className="w-5 h-5 text-blue-400" />
                )}

                <div className="flex-1 flex items-center gap-3 min-w-0">
                  <span className="font-semibold text-gray-900 dark:text-white truncate">{session.plan_id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusBadge(session.status)}`}>{session.status}</span>
                </div>

                <div className="hidden md:flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                  <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" />{session.total_students || 0}</span>
                  <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{new Date(session.created_at).toLocaleDateString()}</span>
                </div>

                <button
                  onClick={(e) => { e.stopPropagation(); handleDeleteSession(session.session_id, session.plan_id); }}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Batches */}
              {expandedSessions[session.session_id] && (
                <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                  {Object.values(session.batches || {}).length > 0 ? (
                    Object.values(session.batches).map((batch) => (
                      <div key={batch.batch_id}>
                        <div
                          onClick={() => toggleBatch(batch.batch_id)}
                          className="flex items-center gap-3 p-3 pl-12 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                        >
                          <div className="text-gray-400">
                            {expandedBatches[batch.batch_id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                          </div>

                          <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: batch.batch_color || '#3b82f6' }} />

                          <span className="font-medium text-gray-700 dark:text-gray-200 flex-1">{batch.batch_name}</span>

                          <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                            {batch.student_count} students
                          </span>

                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteBatch(batch.upload_id, batch.batch_name); }}
                            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-all opacity-0 group-hover:opacity-100"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        {/* Students */}
                        {expandedBatches[batch.batch_id] && (
                          <div className="bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700">
                            {batch.students?.length > 0 ? (
                              <div className="max-h-64 overflow-y-auto">
                                {batch.students.map((student, idx) => (
                                  <div
                                    key={student.id}
                                    className={`flex items-center gap-3 px-4 py-2 pl-20 text-sm hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${
                                      idx !== batch.students.length - 1 ? 'border-b border-gray-100 dark:border-gray-700' : ''
                                    }`}
                                  >
                                    <span className="w-6 text-xs text-gray-400 text-right">{idx + 1}.</span>
                                    <span className="font-mono text-gray-700 dark:text-gray-300 w-32 truncate">{student.enrollment}</span>
                                    <span className="text-gray-600 dark:text-gray-400 flex-1 truncate">{student.name || '—'}</span>
                                    {student.department && (
                                      <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">{student.department}</span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-sm text-gray-500 p-4 pl-20 italic">No students in this batch</div>
                            )}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-gray-500 dark:text-gray-400 p-4 pl-12 italic">No batches in this session</div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <DeleteConfirmModal
        isOpen={deleteModal.open}
        onClose={() => setDeleteModal({ open: false, type: null, data: null })}
        onConfirm={confirmDelete}
        isLoading={isDeleting}
        title={deleteModal.type === 'batch' ? 'Delete Batch?' : 'Delete Session?'}
        message={
          deleteModal.type === 'batch'
            ? `Are you sure you want to delete "${deleteModal.data?.batchName}"? All students will be removed.`
            : `Are you sure you want to delete session "${deleteModal.data?.planId}"? All data will be removed.`
        }
        confirmText={deleteModal.type === 'batch' ? 'Delete Batch' : 'Delete Session'}
      />
    </>
  );
};

export default DatabaseHierarchyView;