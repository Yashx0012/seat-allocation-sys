import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'; // Added Router components
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { FaSun, FaMoon } from 'react-icons/fa';

// --- Components ---
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Toast from './components/Toast';

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

// --------------------------------------------------
// ROUTE GUARD COMPONENT (Handles Protected Routes)
// --------------------------------------------------
const ProtectedRoute = ({ children, user, loading }) => {
  if (loading) return null; 
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

const AppContent = () => {
  const { user, loading } = useAuth();
  const [toast, setToast] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Helper to maintain your original setCurrentPage logic if needed elsewhere
  const setCurrentPage = (page) => {
    navigate(`/${page}`);
  };

  // Extract "currentPage" from URL for your Navbar/Logic
  const currentPage = location.pathname.split('/')[1] || 'landing';

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  // --------------------------------------------------
  // PAGE RENDERER
  // --------------------------------------------------
  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage setCurrentPage={setCurrentPage} />;
      case 'login':
        return <LoginPage setCurrentPage={setCurrentPage} showToast={showToast} />;
      case 'signup':
        return <SignupPage setCurrentPage={setCurrentPage} showToast={showToast} />;
      case 'profile':
        return <ProfilePage showToast={showToast} setCurrentPage={setCurrentPage} />;
      case 'dashboard':
        return <DashboardPage setCurrentPage={setCurrentPage} />;
      case 'upload':
        return <UploadPage showToast={showToast} />;
      case 'create-plan':
        return <CreatePlan setCurrentPage={setCurrentPage} />;
      case 'allocation':
        return <Allocation showToast={showToast} />;
      case 'classroom':
        return <ClassroomPage setCurrentPage={setCurrentPage} />;
      case 'feedback':
        return <FeedbackPage showToast={showToast} />;
      case 'aboutus':
        return <AboutusPage showToast={showToast} />;
      case 'template-editor':
        return <TemplateEditor showToast={showToast} />;
      case 'attendence':
        return <AttendancePage showToast={showToast} />;
      case 'database-manager':
        return <DatabaseManager setCurrentPage={setCurrentPage} showToast={showToast} />;
      default:
        return <LandingPage setCurrentPage={setCurrentPage} />;
    }
  };

  // --------------------------------------------------
  // MAIN LAYOUT
  // --------------------------------------------------
  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-white dark:bg-phantom-black">
      {/* Navbar stays at the top */}
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage setCurrentPage={setCurrentPage} />} />
          <Route path="/landing" element={<LandingPage setCurrentPage={setCurrentPage} />} />
          <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage setCurrentPage={setCurrentPage} showToast={showToast} />} />
          <Route path="/signup" element={user ? <Navigate to="/dashboard" /> : <SignupPage setCurrentPage={setCurrentPage} showToast={showToast} />} />
          <Route path="/aboutus" element={<AboutusPage showToast={showToast} />} />
          <Route path="/feedback" element={<FeedbackPage showToast={showToast} />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute user={user} loading={loading}><DashboardPage setCurrentPage={setCurrentPage} /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute user={user} loading={loading}><ProfilePage showToast={showToast} setCurrentPage={setCurrentPage} /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute user={user} loading={loading}><UploadPage showToast={showToast} /></ProtectedRoute>} />
          <Route path="/allocation" element={<ProtectedRoute user={user} loading={loading}><Allocation showToast={showToast} /></ProtectedRoute>} />
          <Route path="/create-plan" element={<ProtectedRoute user={user} loading={loading}><CreatePlan setCurrentPage={setCurrentPage} /></ProtectedRoute>} />
          <Route path="/classroom" element={<ProtectedRoute user={user} loading={loading}><ClassroomPage setCurrentPage={setCurrentPage} /></ProtectedRoute>} />
          <Route path="/template-editor" element={<ProtectedRoute user={user} loading={loading}><TemplateEditor showToast={showToast} /></ProtectedRoute>} />
          
          {/* UPDATED: Attendance Route with planId parameter */}
          <Route path="/attendance/:planId" element={<ProtectedRoute user={user} loading={loading}><AttendancePage showToast={showToast} /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>

      <Footer />

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
};

const App = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router> {/* This provides the context for useNavigate() */}
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;