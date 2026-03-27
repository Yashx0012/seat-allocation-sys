import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle } from 'lucide-react';

const FeatureTooltip = ({ children, title, description }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-flex items-center gap-1">
      {children}
      <div
        className="relative"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        <HelpCircle
          size={14}
          className="text-gray-400 dark:text-gray-600 hover:text-orange-500 dark:hover:text-orange-400 cursor-help transition-colors"
        />
        <AnimatePresence>
          {isVisible && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -8 }}
              transition={{ duration: 0.2 }}
              className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50"
            >
              <div className="bg-gray-900 dark:bg-gray-800 text-white rounded-lg p-3 w-48 shadow-xl border border-gray-700">
                <h4 className="font-bold text-sm mb-1.5 text-orange-400">{title}</h4>
                <p className="text-xs leading-relaxed text-gray-200">{description}</p>
                {/* Tooltip arrow */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-800"></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default FeatureTooltip;
