// frontend/src/components/SessionIndicator.jsx
import React from 'react';
import { useSession } from '../contexts/SessionContext';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

const SessionIndicator = () => {
  // Direct hook call with safe fallback handling
  let session = null;
  let hasActiveSession = false;
  let loading = false;

  try {
    const sessionData = useSession();
    session = sessionData.session;
    hasActiveSession = sessionData.hasActiveSession;
    loading = sessionData.loading;
  } catch (error) {
    console.warn('SessionContext not available:', error);
  }

  if (loading) {
    return (
      <div className="bg-gray-100 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-xl p-4 flex items-center gap-3">
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-transparent"></div>
        <span className="text-sm font-bold text-gray-600 dark:text-gray-400">Loading session...</span>
      </div>
    );
  }

  if (!hasActiveSession || !session) {
    return (
      <div className="bg-amber-50 dark:bg-amber-900/20 border-2 border-amber-200 dark:border-amber-800 rounded-xl p-4 flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-bold text-amber-900 dark:text-amber-100">No Active Session</div>
          <div className="text-xs text-amber-700 dark:text-amber-300">Upload student data to begin</div>
        </div>
      </div>
    );
  }

  // CRITICAL FIX: Safe defaults for ALL values
  const totalStudents = Number(session.total_students) || 0;
  const allocatedCount = Number(session.allocated_count) || 0;
  const pendingCount = Number(session.pending_count) || 0;
  
  const progress = totalStudents > 0 
    ? Math.round((allocatedCount / totalStudents) * 100) 
    : 0;
  
  const isComplete = pendingCount === 0 && totalStudents > 0;

  // CRITICAL FIX: Ensure allocated_rooms is ALWAYS an array
  const allocatedRooms = Array.isArray(session.allocated_rooms) 
    ? session.allocated_rooms 
    : [];

  return (
    <div className={`border-2 rounded-xl p-4 ${
      isComplete 
        ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-500 dark:border-emerald-400'
        : 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 dark:border-blue-400'
    }`}>
      <div className="flex items-start gap-3">
        {isComplete ? (
          <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
        ) : (
          <Clock className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        )}
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className={`text-sm font-bold ${
                isComplete 
                  ? 'text-emerald-900 dark:text-emerald-100'
                  : 'text-blue-900 dark:text-blue-100'
              }`}>
                {isComplete ? 'Allocation Complete' : 'Session In Progress'}
              </h3>
              <p className={`text-xs font-mono ${
                isComplete
                  ? 'text-emerald-700 dark:text-emerald-300'
                  : 'text-blue-700 dark:text-blue-300'
              }`}>
                ID: {session.plan_id || 'N/A'}
              </p>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-black ${
                isComplete
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-blue-600 dark:text-blue-400'
              }`}>
                {progress}%
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-2">
            <div 
              className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ${
                isComplete
                  ? 'bg-emerald-500'
                  : 'bg-blue-500'
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Stats */}
          <div className="flex justify-between text-xs font-mono">
            <span className={isComplete ? 'text-emerald-700 dark:text-emerald-300' : 'text-blue-700 dark:text-blue-300'}>
              {allocatedCount} / {totalStudents} allocated
            </span>
            <span className={isComplete ? 'text-emerald-700 dark:text-emerald-300' : 'text-blue-700 dark:text-blue-300'}>
              {pendingCount} pending
            </span>
          </div>

          {/* CRITICAL FIX: Safe array rendering */}
          {allocatedRooms.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="text-xs font-bold text-gray-600 dark:text-gray-400 mb-2">Rooms:</div>
              <div className="flex flex-wrap gap-2">
                {allocatedRooms.map((room, idx) => (
                  <span 
                    key={idx}
                    className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs font-mono"
                  >
                    {room?.classroom_name || 'Unknown'} ({room?.count || 0})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SessionIndicator;