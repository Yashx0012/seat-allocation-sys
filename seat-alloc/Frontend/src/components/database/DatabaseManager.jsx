// src/components/database/DatabaseManager.jsx

import React, { useState, useEffect, useCallback } from 'react';  // ← ADDED useEffect, useCallback
import {
  Database,
  Archive,
  RefreshCw,
  FolderTree,
  Table,
  Zap,      // ← ADDED
  ZapOff    // ← ADDED
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import DatabaseHierarchyView from './DatabaseHierarchyView';
import DatabaseTableView from './DatabaseTableView';
import useDatabaseApi from './hooks/useDatabaseApi';

const DatabaseManager = ({ showToast }) => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState('hierarchy');
  const [refreshKey, setRefreshKey] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(false);        // ← ADDED
  const [lastRefresh, setLastRefresh] = useState(new Date());   // ← ADDED

  const { createBackup } = useDatabaseApi();

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

  // ← CHANGED: Wrapped with useCallback
  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    setLastRefresh(new Date());
  }, []);

  // ← ADDED: Auto-refresh interval
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      handleRefresh();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, handleRefresh]);

  // ← ADDED: Listen for external database update events
  useEffect(() => {
    const handleDatabaseUpdate = () => {
      console.log('🔄 Database update event received');
      handleRefresh();
    };

    // Listen for various update events
    window.addEventListener('database-updated', handleDatabaseUpdate);
    window.addEventListener('session-finalized', handleDatabaseUpdate);
    window.addEventListener('allocation-completed', handleDatabaseUpdate);
    window.addEventListener('students-uploaded', handleDatabaseUpdate);

    return () => {
      window.removeEventListener('database-updated', handleDatabaseUpdate);
      window.removeEventListener('session-finalized', handleDatabaseUpdate);
      window.removeEventListener('allocation-completed', handleDatabaseUpdate);
      window.removeEventListener('students-uploaded', handleDatabaseUpdate);
    };
  }, [handleRefresh]);

  // Re-fetch when user changes (account switch)
  const userIdentity = user?.email || user?.id;
  useEffect(() => {
    if (userIdentity) {
      handleRefresh();
    }
  }, [userIdentity]); // eslint-disable-line react-hooks/exhaustive-deps

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
            {/* ← UPDATED: Added last refresh time */}
            <p className="text-gray-600 dark:text-gray-400 mt-1 text-sm md:text-base flex items-center gap-2 flex-wrap">
              View and manage all database records
              <span className="text-xs text-gray-400 dark:text-gray-500">
                • Updated: {lastRefresh.toLocaleTimeString()}
              </span>
            </p>
          </div>

          <div className="flex gap-2 flex-wrap">
            {/* ← ADDED: Auto-Refresh Toggle */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 md:px-4 py-2 rounded-lg flex items-center gap-2 transition-all text-sm font-medium border ${
                autoRefresh
                  ? 'bg-green-500 text-white border-green-500 hover:bg-green-600'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
              title={autoRefresh ? 'Auto-refresh ON (5s)' : 'Click to enable auto-refresh'}
            >
              {autoRefresh ? (
                <>
                  <Zap className="w-4 h-4" />
                  <span className="hidden sm:inline">Live</span>
                </>
              ) : (
                <>
                  <ZapOff className="w-4 h-4" />
                  <span className="hidden sm:inline">Auto</span>
                </>
              )}
            </button>

            {/* ← UPDATED: Made Refresh button more prominent */}
            <button
              onClick={handleRefresh}
              className="px-3 md:px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center gap-2 transition-colors text-sm font-medium"
            >
              <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            <button
              onClick={handleBackup}
              className="px-3 md:px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2 transition-colors text-sm font-medium"
            >
              <Archive className="w-4 h-4" />
              <span className="hidden sm:inline">Backup</span>
            </button>
          </div>
        </div>

        {/* ← ADDED: Auto-refresh indicator */}
        {autoRefresh && (
          <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded-lg w-fit border border-green-200 dark:border-green-800">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            Auto-refreshing every 5 seconds
          </div>
        )}

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