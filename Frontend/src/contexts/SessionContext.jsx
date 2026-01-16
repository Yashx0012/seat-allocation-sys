// frontend/src/contexts/SessionContext.jsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const SessionContext = createContext(null);

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    console.warn('useSession must be used within SessionProvider');
    return {
      session: null,
      hasActiveSession: false,
      loading: true,
      error: null,
      createSession: async () => {},
      updateSession: async () => {},
      completeSession: async () => {},
      clearSession: () => {},
      updateSessionFromResponse: () => {}
    };
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [session, setSession] = useState(null);
  const [hasActiveSession, setHasActiveSession] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Helper to safely parse session from response
  const parseSafeSession = useCallback((rawSession) => {
    if (!rawSession) return null;

    const totalStudents = parseInt(rawSession.total_students) || 0;
    const allocatedCount = parseInt(rawSession.allocated_count) || 0;
    const pendingCount = Math.max(0, totalStudents - allocatedCount);

    return {
      session_id: rawSession.session_id || null,
      plan_id: rawSession.plan_id || '',
      total_students: totalStudents,
      allocated_count: allocatedCount,
      pending_count: pendingCount,
      status: rawSession.status || 'active',
      created_at: rawSession.created_at || null,
      last_activity: rawSession.last_activity || null,
      allocated_rooms: Array.isArray(rawSession.allocated_rooms) 
        ? rawSession.allocated_rooms 
        : []
    };
  }, []);

  // CRITICAL: Update session directly from API response (for Save & Continue)
  const updateSessionFromResponse = useCallback((responseData) => {
    if (!responseData?.session) {
      console.warn('⚠️ No session data in response');
      return;
    }

    const safeSession = parseSafeSession(responseData.session);
    if (safeSession) {
      console.log('✅ Session updated from response:', safeSession);
      setSession(safeSession);
      setHasActiveSession(true);
      setError(null);
    }
  }, [parseSafeSession]);

  const fetchActiveSession = useCallback(async () => {
    try {
      setError(null);
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/sessions/active', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      // Handle non-200 responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Session fetch failed:', response.status, errorData);
        
        // 500 error - backend issue, don't clear session
        if (response.status === 500) {
          setError('Server error - backend unavailable');
          // Preserve existing session state on server error
          setLoading(false);
          return;
        }
        
        // 4xx errors - no active session
        setSession(null);
        setHasActiveSession(false);
        setLoading(false);
        return;
      }

      const data = await response.json();

      if (data.success && data.session_data) {
        const safeSession = parseSafeSession(data.session_data);
        if (safeSession) {
          console.log('✅ Session fetched:', {
            id: safeSession.session_id,
            total: safeSession.total_students,
            allocated: safeSession.allocated_count,
            pending: safeSession.pending_count
          });
          
          setSession(safeSession);
          setHasActiveSession(true);
          setError(null);
        }
      } else {
        console.log('ℹ️ No active session found');
        setSession(null);
        setHasActiveSession(false);
      }
    } catch (err) {
      console.error('❌ Session fetch error:', err);
      setError(err.message);
      // On network error, preserve session state
    } finally {
      setLoading(false);
    }
  }, [parseSafeSession]);

  // Initial fetch on mount
  useEffect(() => {
    fetchActiveSession();
  }, [fetchActiveSession]);

  // Refresh session (after allocation save, etc)
  const updateSession = useCallback(async () => {
    console.log('🔄 Updating session from server...');
    await fetchActiveSession();
  }, [fetchActiveSession]);

  // Create new session
  const createSession = useCallback(async (uploadIds = [], classroomIds = []) => {
    if (!Array.isArray(uploadIds) || uploadIds.length === 0) {
      throw new Error('No upload IDs provided');
    }

    console.log('🆕 Creating session with', uploadIds.length, 'uploads');
    
    try {
      setError(null);
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/sessions/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ 
          upload_ids: uploadIds,
          selected_classrooms: classroomIds || []
        })
      });

      const data = await response.json();

      if (!response.ok) {
        // Check if blocked by existing session
        if (data.existing_session) {
          console.log('⚠️ Active session exists:', data.existing_session);
          const error = new Error(data.error || 'An active session already exists');
          error.existing_session = data.existing_session;
          throw error;
        }
        throw new Error(data.error || 'Failed to create session');
      }

      if (data.success && data.session) {
        const newSession = parseSafeSession(data.session);
        
        console.log('✅ Session created:', {
          id: newSession.session_id,
          plan: newSession.plan_id,
          total: newSession.total_students
        });
        
        setSession(newSession);
        setHasActiveSession(true);
        setError(null);
        
        return newSession;
      }
      
      throw new Error('Invalid response from server');
      
    } catch (err) {
      console.error('❌ Create session error:', err);
      setError(err.message);
      throw err;
    }
  }, [parseSafeSession]);

  // Complete session (called by Finalize button only)
  const completeSession = useCallback(async () => {
    console.log('🏁 Completing session...');
    
    if (!session?.session_id) {
      console.warn('⚠️ No session to complete');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/sessions/${session.session_id}/finalize`,
        { 
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );

      if (!response.ok) {
        throw new Error('Failed to finalize session');
      }

      console.log('✅ Session completed');
      setSession(null);
      setHasActiveSession(false);
      setError(null);

    } catch (err) {
      console.error('❌ Complete session error:', err);
      setError(err.message);
      throw err;
    }
  }, [session?.session_id]);

  // Clear session (called when user logs out, etc)
  const clearSession = useCallback(() => {
    console.log('🗑️ Clearing session');
    setSession(null);
    setHasActiveSession(false);
    setError(null);
  }, []);

  const value = {
    session,
    hasActiveSession,
    loading,
    error,
    createSession,
    updateSession,
    updateSessionFromResponse,  // NEW: Direct update from API response
    completeSession,
    clearSession
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export default SessionContext;