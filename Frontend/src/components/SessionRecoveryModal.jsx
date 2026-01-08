// frontend/src/components/SessionRecoveryModal.jsx
import React from 'react';
import { useSession } from '../contexts/SessionContext';

const SessionRecoveryModal = ({ onClose }) => {
  const sessionCtx = useSession();
  const [recovering, setRecovering] = React.useState(false);

  // SAFE DESTRUCTURING
  const sessions = Array.isArray(sessionCtx?.recoverableSessions) ? sessionCtx.recoverableSessions : [];
  const recoverSession = sessionCtx?.recoverSession || (async () => {});
  const clearSession = sessionCtx?.clearSession || (() => {});

  if (sessions.length === 0) {
    return null;
  }

  const handleRecover = async (sessionId) => {
    setRecovering(true);
    try {
      await recoverSession(sessionId);
      onClose?.();
    } catch (err) {
      alert('Failed to recover session: ' + err.message);
    } finally {
      setRecovering(false);
    }
  };

  const handleStartFresh = () => {
    clearSession();
    onClose?.();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999]">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center mb-6">
          <div className="bg-orange-100 dark:bg-orange-900/30 rounded-full p-3 mr-4">
            <svg className="w-8 h-8 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Session Expired
          </h3>
        </div>

        <p className="text-gray-600 dark:text-gray-400 mb-6">
          You have {sessions.length} session(s) that can be recovered. Would you like to resume your previous work?
        </p>

        <div className="space-y-4 mb-8 max-h-[300px] overflow-y-auto pr-2">
          {sessions.map((session) => (
            <div key={session.session_id} className="border-2 border-gray-100 dark:border-gray-700 rounded-xl p-4 hover:border-blue-500 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-bold text-gray-900 dark:text-white">
                    Session #{session.session_id}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {session.total_students || 0} students • {session.upload_count || 0} uploads
                  </p>
                </div>
              </div>
              
              <button
                onClick={() => handleRecover(session.session_id)}
                disabled={recovering}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg disabled:opacity-50 transition-all text-sm font-bold flex items-center justify-center gap-2"
              >
                {recovering ? 'Recovering...' : 'Resume Session'}
              </button>
            </div>
          ))}
        </div>

        <button
          onClick={handleStartFresh}
          className="w-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-3 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 font-bold transition-all text-sm"
        >
          Discard & Start Fresh
        </button>
      </div>
    </div>
  );
};

export default SessionRecoveryModal;