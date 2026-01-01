import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';

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

// -------------------------------------------------------------------
// PROTECTED ROUTE COMPONENT
// -------------------------------------------------------------------
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
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
// APP CONTENT (inside providers)
// -------------------------------------------------------------------
const AppContent = () => {
  const { loading } = useAuth();
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const closeToast = () => setToast(null);

  // --------------------------------------------------
  // LOADING SCREEN
  // --------------------------------------------------
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 font-medium">Loading your session…</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // MAIN LAYOUT WITH ROUTES
  // --------------------------------------------------
  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-white dark:bg-phantom-black">
      <Navbar />

      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/landing" element={<LandingPage />} />
          <Route path="/aboutus" element={<AboutusPage showToast={showToast} />} />
          
          {/* Auth Routes - Redirect to dashboard if already logged in */}
          <Route 
            path="/login" 
            element={<LoginPage showToast={showToast} />} 
          />
          <Route 
            path="/signup" 
            element={<SignupPage showToast={showToast} />} 
          />

          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} 
          />
          <Route 
            path="/profile" 
            element={<ProtectedRoute><ProfilePage showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/upload" 
            element={<ProtectedRoute><UploadPage showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/allocation" 
            element={<ProtectedRoute><Allocation showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/create-plan" 
            element={<ProtectedRoute><CreatePlan /></ProtectedRoute>} 
          />
          <Route 
            path="/classroom" 
            element={<ProtectedRoute><ClassroomPage /></ProtectedRoute>} 
          />
          <Route 
            path="/feedback" 
            element={<ProtectedRoute><FeedbackPage showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/template-editor" 
            element={<ProtectedRoute><TemplateEditor showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/attendance/:planId" 
            element={<ProtectedRoute><AttendancePage showToast={showToast} /></ProtectedRoute>} 
          />
          <Route 
            path="/database-manager" 
            element={<ProtectedRoute><DatabaseManager showToast={showToast} /></ProtectedRoute>} 
          />

          {/* Fallback */}
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
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
