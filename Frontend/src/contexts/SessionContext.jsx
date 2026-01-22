// frontend/src/contexts/SessionContext.jsx - PROPERLY FIXED
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
      refreshTotals: async () => {},
      completeSession: async () => {},
      clearSession: () => {},
      clearCompletedSession: () => {},
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

  // ============================================================================
  // HELPER: Parse session data safely
  // ============================================================================
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

  // ============================================================================
  // Update session from API response
  // ============================================================================
  const updateSessionFromResponse = useCallback((responseData) => {
    const sessionData = responseData?.session || responseData?.session_data;
    if (!sessionData) {
      console.warn('⚠️ No session data in response');
      return;
    }

    const safeSession = parseSafeSession(sessionData);
    if (safeSession) {
      console.log('✅ Session updated:', safeSession);
      setSession(safeSession);
      setHasActiveSession(safeSession.status === 'active');
      setError(null);
    }
  }, [parseSafeSession]);

  // ============================================================================
  // Fetch active session from API
  // ============================================================================
  const fetchActiveSession = useCallback(async () => {
    try {
      setError(null);
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/sessions/active', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      if (!response.ok) {
        if (response.status === 500) {
          setError('Server error');
          setLoading(false);
          return;
        }
        setSession(null);
        setHasActiveSession(false);
        setLoading(false);
        return;
      }

      const data = await response.json();

      if (data.success && data.session_data) {
        const safeSession = parseSafeSession(data.session_data);
        
        // Only set if session is actually active
        if (safeSession && safeSession.status === 'active') {
          console.log('✅ Active session found:', safeSession.session_id);
          setSession(safeSession);
          setHasActiveSession(true);
        } else {
          console.log('🧹 Session not active, clearing');
          setSession(null);
          setHasActiveSession(false);
          localStorage.removeItem('currentSession');
        }
      } else {
        console.log('ℹ️ No active session');
        setSession(null);
        setHasActiveSession(false);
      }
    } catch (err) {
      console.error('❌ Fetch error:', err);
      setError(err.message);
      setSession(null);
      setHasActiveSession(false);
    } finally {
      setLoading(false);
    }
  }, [parseSafeSession]);

  // ============================================================================
  // Initial load
  // ============================================================================
  useEffect(() => {
    fetchActiveSession();
  }, [fetchActiveSession]);

  // ============================================================================
  // Update/refresh session
  // ============================================================================
  const updateSession = useCallback(async () => {
    console.log('🔄 Refreshing session...');
    await fetchActiveSession();
  }, [fetchActiveSession]);

  // ============================================================================
  // Refresh totals after adding batches
  // ============================================================================
  const refreshTotals = useCallback(async () => {
    if (!session?.session_id) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/sessions/${session.session_id}/refresh-totals`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSession(prev => ({
            ...prev,
            total_students: data.total_students,
            allocated_count: data.allocated_count,
            pending_count: data.pending_count
          }));
          console.log('✅ Totals refreshed:', data);
        }
      }
    } catch (err) {
      console.error('❌ Refresh totals error:', err);
    }
  }, [session?.session_id]);

  // ============================================================================
  // CREATE SESSION - The function that was "missing"!
  // ============================================================================
  const createSession = useCallback(async (uploadIds = [], classroomIds = []) => {
    if (!Array.isArray(uploadIds) || uploadIds.length === 0) {
      throw new Error('No upload IDs provided');
    }

    console.log('🆕 Creating/adding to session with', uploadIds.length, 'uploads');
    
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
        throw new Error(data.error || 'Failed to create session');
      }

      if (data.success && data.session) {
        const newSession = parseSafeSession(data.session);
        
        if (data.added_to_existing) {
          console.log('📎 Added to existing session:', newSession.session_id);
        } else {
          console.log('✅ New session created:', newSession.session_id);
        }
        
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

  // ============================================================================
  // Complete/Finalize session
  // ============================================================================
  const completeSession = useCallback(async () => {
    if (!session?.session_id) return;

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
        const data = await response.json();
        throw new Error(data.error || 'Failed to finalize');
      }

      console.log('✅ Session completed');
      setSession(null);
      setHasActiveSession(false);
      localStorage.removeItem('currentSession');

    } catch (err) {
      console.error('❌ Finalize error:', err);
      throw err;
    }
  }, [session?.session_id]);

  // ============================================================================
  // Clear session (manual)
  // ============================================================================
  const clearSession = useCallback(() => {
    console.log('🧹 Clearing session');
    setSession(null);
    setHasActiveSession(false);
    setError(null);
    localStorage.removeItem('currentSession');
  }, []);

  // ============================================================================
  // Clear completed session (auto-cleanup)
  // ============================================================================
  const clearCompletedSession = useCallback(() => {
    if (session && session.status === 'completed') {
      console.log('🧹 Auto-clearing completed session');
      setSession(null);
      setHasActiveSession(false);
      localStorage.removeItem('currentSession');
    }
  }, [session]);

  // ============================================================================
  // CONTEXT VALUE - All functions must be included here!
  // ============================================================================
  const value = {
    // State
    session,
    hasActiveSession,
    loading,
    error,
    
    // Actions
    createSession,           // ← THIS WAS MISSING IN YOUR BROKEN VERSION!
    updateSession,
    refreshTotals,
    updateSessionFromResponse,
    completeSession,
    clearSession,
    clearCompletedSession,
    
    // Alias for compatibility
    fetchSession: fetchActiveSession
  };
  useEffect(() => {
  if (session && session.status !== 'active') {
    console.log('🧹 Auto-clearing non-active session:', session.status);
    setSession(null);
    setHasActiveSession(false);
    localStorage.removeItem('currentSession');
  }
}, [session?.status]);

  // ============================================================================
  // SINGLE RETURN - Only one!
  // ============================================================================
  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export default SessionContext;