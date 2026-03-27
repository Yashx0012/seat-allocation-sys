// frontend/src/App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
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
import AdminFeedbackPage from './pages/AdminFeedbackPage';
import AboutusPage from './pages/AboutusPage';
import TemplateEditor from './pages/TemplateEditor';
import AttendancePage from './pages/AttendencePage';
import MoreOptionsPage from './pages/MoreOptionsPage';
import ClassroomPage from './pages/ClassroomPage';
import { DatabaseManager } from './components/database';
import ManualAllocation from './pages/ManualAllocation';

// -------------------------------------------------------------------
// PAGE TRANSITION CONFIG (Single source of truth)
// -------------------------------------------------------------------
const pageTransitionVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

const pageTransitionConfig = {
  duration: 0.2,
  ease: [0.25, 0.1, 0.25, 1],
};

// -------------------------------------------------------------------
// ANIMATED LAYOUT (The key component - animates Outlet)
// -------------------------------------------------------------------
const AnimatedLayout = ({ showToast }) => {
  const location = useLocation();
  
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial="initial"
        animate="animate"
        exit="exit"
        variants={pageTransitionVariants}
        transition={pageTransitionConfig}
      >
        <Outlet context={{ showToast }} />
      </motion.div>
    </AnimatePresence>
  );
};

// -------------------------------------------------------------------
// PROTECTED ROUTE (Clean, no nesting issues)
// -------------------------------------------------------------------
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-200 dark:border-gray-700 border-t-orange-500 rounded-full animate-spin" />
      </div>
    );
  }

  return user ? children : <Navigate to="/login" replace />;
};

// -------------------------------------------------------------------
// SESSION RECOVERY HANDLER
// -------------------------------------------------------------------
const SessionRecoveryHandler = () => {
  const sessionCtx = useSession();
  const [showRecoveryModal, setShowRecoveryModal] = useState(false);

  const sessions = React.useMemo(() => {
    return Array.isArray(sessionCtx?.recoverableSessions) ? sessionCtx.recoverableSessions : [];
  }, [sessionCtx?.recoverableSessions]);

  React.useEffect(() => {
    if (sessions.length > 0) {
      setShowRecoveryModal(true);
    }
  }, [sessions]);

  if (!showRecoveryModal || sessions.length === 0) return null;
  return <SessionRecoveryModal onClose={() => setShowRecoveryModal(false)} />;
};

// -------------------------------------------------------------------
// ROOT LAYOUT (Navbar + Animated Content + Footer)
// -------------------------------------------------------------------
const RootLayout = ({ showToast }) => {
  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-[#050505] transition-colors duration-200">
      <SessionRecoveryHandler />
      <Navbar />
      <main className="flex-1">
        <AnimatedLayout showToast={showToast} />
      </main>
      <Footer />
    </div>
  );
};

// -------------------------------------------------------------------
// APP ROUTES (Clean, no wrapper on each route)
// -------------------------------------------------------------------
const AppRoutes = () => {
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <>
      <Routes>
        {/* Root Layout wraps all routes - handles animation once */}
        <Route element={<RootLayout showToast={showToast} />}>
          
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/aboutus" element={<AboutusPage showToast={showToast} />} />
          <Route path="/login" element={<LoginPage showToast={showToast} />} />
          <Route path="/signup" element={<SignupPage showToast={showToast} />} />

          {/* Protected Routes - Clean syntax */}
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/manual-allocation" element={<ProtectedRoute><ManualAllocation showToast={showToast} /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><UploadPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/allocation" element={<ProtectedRoute><Allocation showToast={showToast} /></ProtectedRoute>} />
          <Route path="/create-plan" element={<ProtectedRoute><CreatePlan /></ProtectedRoute>} />
          <Route path="/classroom" element={<ProtectedRoute><ClassroomPage /></ProtectedRoute>} />
          <Route path="/feedback" element={<ProtectedRoute><FeedbackPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/admin-feedback" element={<ProtectedRoute><AdminFeedbackPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/template-editor" element={<ProtectedRoute><TemplateEditor showToast={showToast} /></ProtectedRoute>} />
          <Route path="/attendance/:planId" element={<ProtectedRoute><AttendancePage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/more-options/:planId" element={<ProtectedRoute><MoreOptionsPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/database" element={<ProtectedRoute><DatabaseManager showToast={showToast} /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>

      {/* Toast - Outside routes */}
      <AnimatePresence>
        {toast && (
          <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
        )}
      </AnimatePresence>
    </>
  );
};

// -------------------------------------------------------------------
// APP CONTENT (Handles loading states)
// -------------------------------------------------------------------
const AppContent = () => {
  const { loading: authLoading } = useAuth();
  const sessionCtx = useSession();

  if (authLoading || sessionCtx?.loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-[#050505] flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-2 border-gray-200 dark:border-gray-700 border-t-orange-500 rounded-full animate-spin mx-auto" />
          <p className="text-gray-500 dark:text-gray-400 text-sm">Initializing...</p>
        </div>
      </div>
    );
  }

  return <AppRoutes />;
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