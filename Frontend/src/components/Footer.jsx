import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white dark:bg-[#050505] text-gray-800 dark:text-gray-200 py-8 mt-auto transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-3 text-orange-600 dark:text-orange-400">SeatAlloc System</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Efficient seat allocation system for educational institutions.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3 text-orange-600 dark:text-orange-400">Quick Links</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li><a href="#about" className="hover:text-orange-600 dark:hover:text-orange-400 transition">About</a></li>
              <li><a href="#docs" className="hover:text-orange-600 dark:hover:text-orange-400 transition">Documentation</a></li>
              <li><a href="#support" className="hover:text-orange-600 dark:hover:text-orange-400 transition">Support</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3 text-orange-600 dark:text-orange-400">Contact</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Email: support@seatalloc.com<br />
              Phone: +1 (555) 123-4567
            </p>
          </div>
        </div>
        <div className="mt-8">
          <div className="h-1 w-full bg-gradient-to-r from-orange-400 to-orange-600 rounded-sm mb-4" />
          <div className="text-center text-sm text-gray-600 dark:text-gray-400">
            © 2025 SeatAlloc System. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;