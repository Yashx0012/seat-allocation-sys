// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SessionProvider, useSession } from './contexts/SessionContext';

// --- Components ---
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Toast from './components/Toast';
import SessionRecoveryModal from './components/SessionRecoveryModal';
import ErrorBoundary from './components/ErrorBoundary';

// --- Pages ---
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ProfilePage from './pages/ProfilePage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import Allocation from './pages/Allocation';
import CreatePlan from './pages/CreatePlan';
import FeedbackPage from './pages/FeedbackPage';
import AboutusPage from './pages/AboutusPage';
import TemplateEditor from './pages/TemplateEditor';
import AttendancePage from './pages/AttendencePage';
import ClassroomPage from './pages/ClassroomPage';
import DatabaseManager from './pages/DatabaseManager';
import ManualAllocation from './pages/ManualAllocation';

// -------------------------------------------------------------------
// PROTECTED ROUTE COMPONENT
// -------------------------------------------------------------------
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 font-medium">Loading your session…</p>
        </div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" replace />;
};

// -------------------------------------------------------------------
// SESSION RECOVERY HANDLER (FIXED)
// -------------------------------------------------------------------
const SessionRecoveryHandler = () => {
  const sessionCtx = useSession();
  const [showRecoveryModal, setShowRecoveryModal] = useState(false);

  // CRITICAL FIX: Safe access to recoverableSessions
  const sessions = React.useMemo(() => {
    return Array.isArray(sessionCtx?.recoverableSessions) ? sessionCtx.recoverableSessions : [];
  }, [sessionCtx?.recoverableSessions]);

  useEffect(() => {
    if (sessions.length > 0) {
      setShowRecoveryModal(true);
    }
  }, [sessions]);

  if (!showRecoveryModal || sessions.length === 0) return null;

  return <SessionRecoveryModal onClose={() => setShowRecoveryModal(false)} />;
};

// -------------------------------------------------------------------
// APP CONTENT
// -------------------------------------------------------------------
const AppContent = () => {
  const { loading: authLoading } = useAuth();
  const sessionCtx = useSession();
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const closeToast = () => setToast(null);

  // Show loading if either Auth or Session is loading
  if (authLoading || sessionCtx?.loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-phantom-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 font-medium">Initializing System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-white dark:bg-phantom-black">
      {/* Global Session Recovery UI */}
      <SessionRecoveryHandler />

      <Navbar />

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/aboutus" element={<AboutusPage showToast={showToast} />} />
          <Route path="/login" element={<LoginPage showToast={showToast} />} />
          <Route path="/signup" element={<SignupPage showToast={showToast} />} />

          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage showToast={showToast} /></ProtectedRoute>} />
          <Route 
            path="/manual-allocation" 
            element={<ProtectedRoute><ManualAllocation showToast={showToast} /></ProtectedRoute>} 
          />
          <Route path="/upload" element={<ProtectedRoute><UploadPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/allocation" element={<ProtectedRoute><Allocation showToast={showToast} /></ProtectedRoute>} />
          <Route path="/create-plan" element={<ProtectedRoute><CreatePlan /></ProtectedRoute>} />
          <Route path="/classroom" element={<ProtectedRoute><ClassroomPage /></ProtectedRoute>} />
          <Route path="/feedback" element={<ProtectedRoute><FeedbackPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/template-editor" element={<ProtectedRoute><TemplateEditor showToast={showToast} /></ProtectedRoute>} />
          <Route path="/attendance/:planId" element={<ProtectedRoute><AttendancePage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/database-manager" element={<ProtectedRoute><DatabaseManager showToast={showToast} /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={closeToast}
        />
      )}
    </div>
  );
};

// -------------------------------------------------------------------
// ROOT APP
// -------------------------------------------------------------------
const App = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <SessionProvider>
            <Router>
              <AppContent />
            </Router>
          </SessionProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;