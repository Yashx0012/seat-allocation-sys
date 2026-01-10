// src/components/database/DatabaseManager.jsx

import React, { useState } from 'react';
import {
  Database,
  Archive,
  RefreshCw,
  FolderTree,
  Table
} 
from 'lucide-react';
import DatabaseHierarchyView from './DatabaseHierarchyView';
import DatabaseTableView from './DatabaseTableView';
import useDatabaseApi from './hooks/useDatabaseApi';

const DatabaseManager = ({ showToast }) => {
  const [viewMode, setViewMode] = useState('hierarchy');
  const [refreshKey, setRefreshKey] = useState(0);

  const { createBackup } = useDatabaseApi();

  // Use parent's showToast, fallback to console if not provided
  const handleToast = (message, type = 'success') => {
    if (showToast) {
      showToast(message, type);
    } else {
      console.log(`[${type}] ${message}`);
    }
  };

  const handleBackup = async () => {
    const result = await createBackup();
    if (result.success) {
      handleToast(`Backup created: ${result.backupFile}`, 'success');
    } else {
      handleToast(result.error || 'Backup failed', 'error');
    }
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0a0a0a] p-4 md:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Database className="w-7 h-7 md:w-8 md:h-8 text-orange-500" />
              Database Manager
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1 text-sm md:text-base">
              View and manage all database records
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleBackup}
              className="px-3 md:px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2 transition-colors text-sm font-medium"
            >
              <Archive className="w-4 h-4" />
              <span className="hidden sm:inline">Backup</span>
            </button>
            <button
              onClick={handleRefresh}
              className="px-3 md:px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2 transition-colors text-sm font-medium"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>

        {/* View Mode Tabs */}
        <div className="flex gap-1 p-1 bg-gray-200 dark:bg-gray-800 rounded-xl w-fit">
          <button
            onClick={() => setViewMode('hierarchy')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              viewMode === 'hierarchy'
                ? 'bg-white dark:bg-gray-700 text-orange-600 dark:text-orange-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <FolderTree className="w-4 h-4" />
            Hierarchy
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              viewMode === 'table'
                ? 'bg-white dark:bg-gray-700 text-orange-600 dark:text-orange-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Table className="w-4 h-4" />
            Table
          </button>
        </div>

        {/* Content */}
        {viewMode === 'hierarchy' ? (
          <DatabaseHierarchyView key={`hierarchy-${refreshKey}`} onToast={handleToast} />
        ) : (
          <DatabaseTableView key={`table-${refreshKey}`} onToast={handleToast} />
        )}
      </div>
    </div>
  );
};

export default DatabaseManager;