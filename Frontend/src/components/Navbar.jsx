import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { Layout, LogOut, Menu, X, Moon, Sun, Flame } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ currentPage, setCurrentPage }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isTop, setIsTop] = useState(true);
  const navRef = useRef(null);

  const handleLogout = async () => {
    await logout();
    setCurrentPage('landing');
    setMobileMenuOpen(false);
  };

  useLayoutEffect(() => {
    const updateOffset = () => {
      if (navRef.current) {
        const rect = navRef.current.getBoundingClientRect();
        document.documentElement.style.setProperty('--navbar-offset', `${rect.bottom}px`);
      }
    };
    updateOffset();
    window.addEventListener('resize', updateOffset);
    return () => window.removeEventListener('resize', updateOffset);
  }, [mobileMenuOpen]);

  useEffect(() => {
    const onScroll = () => {
      setIsTop(window.scrollY < 100);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navItems = user
    ? [
        { name: 'Dashboard', page: 'dashboard' },
        { name: 'Create', page: 'create-plan' },
        { name: 'Profile', page: 'profile' },
        { name: 'Feedback', page: 'feedback' },
        { name: 'About us', page: 'aboutus' },
        { name: 'Template Editor', page: 'template-editor' },
        { name: 'Attendence', page: 'attendence' }
      ]
    : [];

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 flex justify-center transition-all duration-500"
    >
      <div
        className={`w-[95%] max-w-7xl px-6 h-20 flex items-center justify-between transition-all duration-500 shadow-md rounded-b-2xl bg-transparent backdrop-blur-2xl backdrop-saturate-150 border-b ${
          theme === 'dark'
            ? 'border-gray-800/40'
            : 'border-gray-200/30'
        }`}
      >
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentPage('landing')}>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl blur-md opacity-50"></div>
            <div className="relative bg-gradient-to-br from-orange-500 to-amber-500 p-2.5 rounded-xl shadow-lg">
              <Flame className="text-white" size={24} />
            </div>
          </div>
          <span className={`text-xl font-black ${
            theme === 'dark' 
              ? 'text-white drop-shadow-[0_0_10px_rgba(192,192,192,0.8)]' 
              : 'text-gray-800'
          }`}>SeatAlloc</span>
        </div>

        <div className="hidden md:flex items-center gap-2">
          {navItems.map((item) => (
            <button
              key={item.page}
              onClick={() => setCurrentPage(item.page)}
              className={`nav-pill px-4 py-2 text-sm font-semibold rounded-full transition-all duration-200 ${
                currentPage === item.page
                  ? 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20'
                  : theme === 'dark'
                    ? 'text-gray-300 hover:text-orange-400 hover:bg-gray-700/40 drop-shadow-[0_0_8px_rgba(192,192,192,0.6)]'
                    : 'text-gray-700 hover:text-orange-600 hover:bg-gray-100'
              }`}
            >
              {item.name}
            </button>
          ))}

          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200 hover:scale-110 ml-2"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon className="text-gray-700" size={20} /> : <Sun className="text-amber-500" size={20} />}
          </button>

          {user ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-2xl hover:scale-105 font-semibold ml-2"
            >
              <LogOut size={18} /> Logout
            </button>
          ) : (
            <div className="flex gap-2 ml-2">
              <button
                onClick={() => setCurrentPage('login')}
                className="text-orange-600 dark:text-orange-400 px-4 py-2 rounded-lg border-2 border-orange-600 dark:border-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 font-semibold"
              >
                Login
              </button>
              <button
                onClick={() => setCurrentPage('signup')}
                className="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-xl font-semibold"
              >
                Sign Up
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon className="text-gray-700" size={20} /> : <Sun className="text-amber-500" size={20} />}
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden pb-4 bg-transparent backdrop-blur-2xl backdrop-saturate-150 border-t border-gray-200/30 dark:border-gray-800/40 animate-slideDown">
          <div className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.page}
                onClick={() => {
                  setCurrentPage(item.page);
                  setMobileMenuOpen(false);
                }}
                className={`block w-full text-left px-4 py-3 text-sm font-semibold rounded-lg transition-all ${
                  currentPage === item.page
                    ? 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {item.name}
              </button>
            ))}
            {user ? (
              <button
                onClick={handleLogout}
                className="block w-full text-left px-4 py-3 text-sm font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
              >
                <LogOut className="inline mr-2" size={18} /> Logout
              </button>
            ) : (
              <>
                <button
                  onClick={() => {
                    setCurrentPage('login');
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-center px-4 py-3 text-sm font-semibold text-orange-600 dark:text-orange-400 border-2 border-orange-600 dark:border-orange-400 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-all"
                >
                  Login
                </button>
                <button
                  onClick={() => {
                    setCurrentPage('signup');
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-center px-4 py-3 text-sm font-semibold bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg shadow-md hover:shadow-xl"
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
