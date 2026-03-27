// src/components/database/hooks/useDatabaseApi.js

import { useState, useCallback } from 'react';
import { getToken } from '../../../utils/tokenStorage';

export const useDatabaseApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getHeaders = useCallback(() => {
    const token = getToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }, []);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/database/overview', {
        headers: getHeaders()
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);
      return data.overview;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [getHeaders]);

  const fetchHierarchy = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/database/hierarchy', {
        headers: getHeaders()
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);
      return data.hierarchy;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, [getHeaders]);

  const fetchTableData = useCallback(async (tableName, options = {}) => {
    const { page = 1, perPage = 50, search = '', sortBy = 'id', sortOrder = 'DESC' } = options;
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        search,
        sort_by: sortBy,
        sort_order: sortOrder
      });

      const res = await fetch(`/api/database/table/${tableName}?${params}`, {
        headers: getHeaders()
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      return {
        data: data.data,
        columns: data.columns,
        pagination: data.pagination
      };
    } catch (err) {
      setError(err.message);
      return { data: [], columns: [], pagination: { page: 1, pages: 1, total: 0, per_page: 50 } };
    } finally {
      setLoading(false);
    }
  }, [getHeaders]);

  const updateRecord = useCallback(async (tableName, recordId, data) => {
    try {
      const res = await fetch(`/api/database/table/${tableName}/${recordId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(data)
      });
      const result = await res.json();
      if (!result.success) throw new Error(result.error);
      return { success: true, message: result.message };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  const deleteRecord = useCallback(async (tableName, recordId) => {
    try {
      const res = await fetch(`/api/database/table/${tableName}/${recordId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      const result = await res.json();
      if (!result.success) throw new Error(result.error);
      return { success: true, message: result.message };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  const bulkDeleteRecords = useCallback(async (tableName, ids) => {
    try {
      const res = await fetch(`/api/database/table/${tableName}/bulk-delete`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ ids })
      });
      const result = await res.json();
      if (!result.success) throw new Error(result.error);
      return { success: true, message: result.message };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  const deleteBatch = useCallback(async (batchId) => {
    try {
      const res = await fetch(`/api/database/batch/${batchId}/delete`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      const result = await res.json();
      if (!result.success) throw new Error(result.error);
      return { success: true, message: result.message, deleted: result.deleted };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  // In useDatabaseApi.jsx
const deleteSession = async (sessionId) => {
    const token = getToken();
    
    // Use the sessions endpoint, not database
    const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || 'Delete failed');
    }
    
    return data;
};

  const exportTable = useCallback(async (tableName) => {
    try {
      const res = await fetch(`/api/database/table/${tableName}/export`, {
        headers: getHeaders()
      });
      if (!res.ok) throw new Error('Export failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${tableName}_export.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  const createBackup = useCallback(async () => {
    try {
      const res = await fetch('/api/database/backup', {
        method: 'POST',
        headers: getHeaders()
      });
      const result = await res.json();
      if (!result.success) throw new Error(result.error);
      return { success: true, backupFile: result.backup_file };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [getHeaders]);

  return {
    loading,
    error,
    fetchOverview,
    fetchHierarchy,
    fetchTableData,
    updateRecord,
    deleteRecord,
    bulkDeleteRecords,
    deleteBatch,
    deleteSession,
    exportTable,
    createBackup
  };
};

export default useDatabaseApi;