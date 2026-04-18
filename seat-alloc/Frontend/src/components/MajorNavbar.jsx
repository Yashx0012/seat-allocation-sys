import React, { useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Layout,
  LogOut,
  Menu,
  X,
  Moon,
  Sun,
  LayoutDashboard,
  User,
  MessageSquare,
  Info,
  ArrowRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

const MajorNavbar = () => {
  const { user, logout, setExamType } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    setExamType(null);
    localStorage.removeItem('examType');
    navigate('/');
    setMobileMenuOpen(false);
  };

  const switchToMinor = () => {
    setExamType('minor');
    localStorage.setItem('examType', JSON.stringify('minor'));
    navigate('/create-plan');
    setMobileMenuOpen(false);
  };

  const navItems = useMemo(() => {
    return [
      { name: 'Dashboard', page: '/dashboard', icon: LayoutDashboard },
      { name: 'Create Plan', page: '/major-exam/create-plan', icon: Layout },
      { name: 'Feedback', page: '/feedback', icon: MessageSquare },
      { name: 'About us', page: '/aboutus', icon: Info },
      { name: 'Profile', page: '/profile', icon: User }
    ];
  }, []);

  const isActive = (page) => location.pathname === page;

  return (
    <>
      {/* Desktop Navbar */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="sticky top-0 z-40 hidden md:block"
      >
        <div className="w-[95%] max-w-7xl mx-auto pt-4 transition-all duration-500">
          <div className="bg-white/30 dark:bg-black/20 backdrop-blur-2xl rounded-2xl px-6 h-20 flex items-center justify-between shadow-2xl shadow-black/5 border border-white/40 dark:border-white/10 font-sans">
            {/* Logo */}
            <div
              className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => navigate('/dashboard')}
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <div>
                <h1 className="text-lg font-bold leading-none uppercase tracking-tighter bg-gradient-to-r from-gray-900 dark:from-white to-gray-600 dark:to-gray-400 bg-clip-text text-transparent">
                  SeatAlloc
                </h1>
                <span className="text-[8px] font-bold uppercase tracking-widest text-orange-600 dark:text-orange-400">Major Exam</span>
              </div>
            </div>

            {/* Navigation Links */}
            {user && (
              <div className="ml-4 flex items-center gap-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.page);

                  return (
                    <motion.button
                      key={item.page}
                      onClick={() => navigate(item.page)}
                      className={`px-4 py-2 rounded-lg transition-all duration-200 font-bold text-sm uppercase tracking-wide flex items-center gap-2 ${
                        active
                          ? 'bg-white/40 dark:bg-white/10 text-gray-900 dark:text-white border border-white/80 dark:border-white/20'
                          : 'text-gray-700 dark:text-gray-200 hover:bg-white/20 dark:hover:bg-white/5 border border-transparent'
                      }`}
                      whileHover={!active ? { scale: 1.02 } : {}}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className="w-4 h-4" />
                      {item.name}
                    </motion.button>
                  );
                })}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-4 ml-auto">
              <motion.button
                onClick={toggleTheme}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-10 h-10 rounded-full border border-gray-200/60 dark:border-gray-700/60 hover:bg-gray-200/40 dark:hover:bg-gray-700/40 flex items-center justify-center transition-colors"
                aria-label="Toggle theme"
              >
                {theme === 'light' ? (
                  <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Sun className="w-5 h-5 text-amber-500" />
                )}
              </motion.button>

              <div className="h-8 w-px bg-gray-200/40 dark:bg-gray-600/40" />

              {/* Switch to Minor Exam */}
              <motion.button
                onClick={switchToMinor}
                className="flex items-center gap-2 px-3 py-2 text-xs font-bold uppercase tracking-wide text-purple-600 dark:text-purple-400 border border-purple-600/60 dark:border-purple-400/60 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <ArrowRight size={14} />
                Minor
              </motion.button>

              {user ? (
                <div className="flex items-center gap-2">
                  <motion.button
                    onClick={() => navigate('/profile')}
                    className="w-10 h-10 rounded-full border border-gray-200/60 dark:border-gray-600/60 hover:bg-gray-200/40 dark:hover:bg-gray-700/40 flex items-center justify-center transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label="Profile"
                  >
                    <User className="w-5 h-5 text-gray-700 dark:text-gray-200" />
                  </motion.button>

                  <motion.button
                    onClick={handleLogout}
                    className="flex items-center gap-2 bg-red-500 text-white px-3 py-2 rounded-lg border border-red-400/60 hover:bg-red-600 transition-all duration-200 font-bold text-xs uppercase tracking-wide shadow-md"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <LogOut size={14} />
                  </motion.button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <motion.button
                    onClick={() => navigate('/login')}
                    className="text-purple-600 dark:text-purple-400 px-4 py-2 rounded-lg border border-purple-600/60 dark:border-purple-400/60 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition font-bold text-sm uppercase tracking-wide"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Login
                  </motion.button>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Navbar */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="sticky top-0 z-40 w-full md:hidden bg-white/30 dark:bg-black/20 border-b border-white/20 dark:border-white/10 shadow-xl font-sans backdrop-blur-xl"
      >
        <div className="px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg">
              <Layout className="text-white w-5 h-5" />
            </div>
            <span className="text-lg font-bold uppercase tracking-tighter text-gray-900 dark:text-white">
              SeatAlloc
            </span>
          </div>

          {/* Mobile Actions */}
          <div className="flex items-center gap-2">
            <motion.button
              onClick={toggleTheme}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-lg border border-gray-200/60 dark:border-gray-700/60 hover:bg-gray-100/40 dark:hover:bg-gray-700/40 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="text-gray-700 dark:text-gray-300" size={20} />
              ) : (
                <Sun className="text-amber-500" size={20} />
              )}
            </motion.button>

            {user && (
              <motion.button
                onClick={() => {
                  navigate('/profile');
                  setMobileMenuOpen(false);
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 rounded-lg border border-gray-200/60 dark:border-gray-700/60 hover:bg-gray-100/40 dark:hover:bg-gray-700/40 transition-colors"
                aria-label="Profile"
              >
                <User className="text-gray-700 dark:text-gray-300" size={20} />
              </motion.button>
            )}

            <motion.button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700 dark:text-gray-300 p-2"
              whileTap={{ scale: 0.95 }}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        <motion.div
          initial={false}
          animate={mobileMenuOpen ? { opacity: 1, height: 'auto' } : { opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-white/60 dark:bg-black/40 border-t border-white/10 dark:border-white/5 overflow-hidden backdrop-blur-2xl"
        >
          <div className="px-4 py-4 space-y-2">
            {user ? (
              <>
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.page);

                  return (
                    <motion.button
                      key={item.page}
                      onClick={() => {
                        navigate(item.page);
                        setMobileMenuOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center gap-3 font-bold text-sm uppercase tracking-wide ${
                        active
                          ? 'bg-purple-100/60 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border border-purple-400/40'
                          : 'text-gray-700 dark:text-gray-300 border border-gray-200/60 dark:border-gray-700/60 hover:bg-gray-100/40 dark:hover:bg-gray-700/40'
                      }`}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className="w-5 h-5" />
                      {item.name}
                    </motion.button>
                  );
                })}

                <motion.button
                  onClick={switchToMinor}
                  className="w-full text-left px-4 py-3 rounded-lg border border-purple-400/50 text-purple-600 dark:text-purple-400 hover:bg-purple-50/40 dark:hover:bg-purple-900/20 transition-all duration-200 flex items-center gap-3 font-bold text-sm uppercase tracking-wide"
                  whileTap={{ scale: 0.98 }}
                >
                  <ArrowRight className="w-4 h-4" />
                  Switch to Minor
                </motion.button>

                <motion.button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-3 rounded-lg border border-red-400/50 text-red-600 dark:text-red-400 hover:bg-red-50/40 dark:hover:bg-red-900/20 transition-all duration-200 flex items-center gap-3 font-bold text-sm uppercase tracking-wide"
                  whileTap={{ scale: 0.98 }}
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </motion.button>
              </>
            ) : null}
          </div>
        </motion.div>
      </motion.nav>
    </>
  );
};

export default MajorNavbar;
