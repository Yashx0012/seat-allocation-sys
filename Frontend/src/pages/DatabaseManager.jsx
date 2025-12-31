import React, { useState, useEffect } from 'react';
import {
  Database,
  Table,
  Search,
  Download,
  Trash2,
  Edit2,
  Plus,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Archive,
  Eye,
  X,
  Check,
  AlertCircle,
  Loader2,
  BarChart3,
  FileDown
} from 'lucide-react';

const DatabaseManager = () => {
  const [selectedTable, setSelectedTable] = useState('students');
  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 50 });
  const [selectedRows, setSelectedRows] = useState([]);
  const [editingRow, setEditingRow] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [toast, setToast] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({ show: false, title: '', action: null });

  const tables = [
    { name: 'students', label: 'Students', icon: '👨‍🎓' },
    { name: 'classrooms', label: 'Classrooms', icon: '🏫' },
    { name: 'uploads', label: 'Uploads', icon: '📤' },
    { name: 'allocations', label: 'Allocations', icon: '📍' },
    { name: 'feedback', label: 'Feedback', icon: '💬' }
  ];

  useEffect(() => {
    fetchOverview();
  }, []);

  useEffect(() => {
    fetchTableData();
  }, [selectedTable, page, searchQuery]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchOverview = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/database/overview', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) {
        setOverview(data.overview);
      }
    } catch (error) {
      console.error('Error fetching overview:', error);
    }
  };

  const fetchTableData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '50',
        search: searchQuery,
        sort_by: 'id',
        sort_order: 'DESC'
      });

      const res = await fetch(`/api/database/table/${selectedTable}?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await res.json();
      if (data.success) {
        setTableData(data.data);
        setColumns(data.columns);
        setPagination(data.pagination);
      }
    } catch (error) {
      console.error('Error fetching table data:', error);
      showToast('Failed to load table data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    setConfirmDialog({
      show: true,
      title: 'Are you sure you want to delete this record?',
      action: async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await fetch(`/api/database/table/${selectedTable}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          });

          const data = await res.json();
          if (data.success) {
            showToast('Record deleted successfully');
            fetchTableData();
            fetchOverview();
          } else {
            throw new Error(data.error);
          }
        } catch (error) {
          showToast(error.message, 'error');
        }
      }
    });
  };

  const handleBulkDelete = async () => {
    if (!selectedRows.length) return;
    
    setConfirmDialog({
      show: true,
      title: `Delete ${selectedRows.length} records?`,
      action: async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await fetch(`/api/database/table/${selectedTable}/bulk-delete`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ids: selectedRows })
          });

          const data = await res.json();
          if (data.success) {
            showToast('Records deleted successfully');
            setSelectedRows([]);
            fetchTableData();
            fetchOverview();
          } else {
            throw new Error(data.error);
          }
        } catch (error) {
          showToast(error.message, 'error');
        }
      }
    });
  };

  const handleUpdate = async (id, updatedData) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/database/table/${selectedTable}/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
      });

      const data = await res.json();
      if (data.success) {
        showToast('Record updated successfully');
        setEditingRow(null);
        fetchTableData();
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      showToast(error.message, 'error');
    }
  };

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/database/table/${selectedTable}/export`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) throw new Error('Export failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedTable}_export.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      showToast('Table exported successfully');
    } catch (error) {
      showToast('Export failed', 'error');
    }
  };

  const handleBackup = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/database/backup', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await res.json();
      if (data.success) {
        showToast(`Backup created: ${data.backup_file}`);
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      showToast(error.message, 'error');
    }
  };

  const toggleRowSelection = (id) => {
    setSelectedRows(prev =>
      prev.includes(id) ? prev.filter(rowId => rowId !== id) : [...prev, id]
    );
  };

  const toggleAllRows = () => {
    if (selectedRows.length === tableData.length) {
      setSelectedRows([]);
    } else {
      setSelectedRows(tableData.map(row => row.id));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white flex items-center gap-3">
              <Database className="w-8 h-8 text-orange-500" />
              Database Manager
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              View and manage all database tables
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleBackup}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2 transition-colors"
            >
              <Archive className="w-4 h-4" />
              Backup
            </button>
            <button
              onClick={fetchTableData}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Overview Cards */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {Object.entries(overview.tables).map(([table, count]) => (
              <div
                key={table}
                onClick={() => setSelectedTable(table)}
                className={`glass-card p-4 cursor-pointer transition-all border-2 ${
                  selectedTable === table
                    ? 'border-orange-500 shadow-lg shadow-orange-500/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-orange-300'
                }`}
              >
                <div className="text-2xl mb-2">
                  {tables.find(t => t.name === table)?.icon || '📊'}
                </div>
                <div className="text-3xl font-black text-gray-900 dark:text-white">
                  {count.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {table}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Controls */}
        <div className="glass-card p-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search records..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 outline-none"
              />
            </div>

            {/* Bulk Actions */}
            {selectedRows.length > 0 && (
              <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                <span className="text-sm font-medium text-orange-700 dark:text-orange-300">
                  {selectedRows.length} selected
                </span>
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" />
                  Delete
                </button>
              </div>
            )}
          </div>

          <button
            onClick={handleExport}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2 transition-colors"
          >
            <FileDown className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-left">
                        <input
                          type="checkbox"
                          checked={selectedRows.length === tableData.length && tableData.length > 0}
                          onChange={toggleAllRows}
                          className="rounded"
                        />
                      </th>
                      {columns.map((col) => (
                        <th
                          key={col.name}
                          className="px-4 py-3 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
                        >
                          {col.name}
                          {col.primary_key && (
                            <span className="ml-1 text-orange-500">🔑</span>
                          )}
                        </th>
                      ))}
                      <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {tableData.map((row) => (
                      <tr
                        key={row.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selectedRows.includes(row.id)}
                            onChange={() => toggleRowSelection(row.id)}
                            className="rounded"
                          />
                        </td>
                        {columns.map((col) => (
                          <td
                            key={col.name}
                            className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate"
                            title={row[col.name]}
                          >
                            {editingRow === row.id ? (
                              <input
                                type="text"
                                defaultValue={row[col.name]}
                                className="w-full px-2 py-1 border rounded text-sm"
                                onBlur={(e) => {
                                  const updatedData = { ...row, [col.name]: e.target.value };
                                  delete updatedData.id;
                                  handleUpdate(row.id, updatedData);
                                }}
                              />
                            ) : (
                              row[col.name] || <span className="text-gray-400">NULL</span>
                            )}
                          </td>
                        ))}
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => setEditingRow(editingRow === row.id ? null : row.id)}
                              className="p-1 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                              title="Edit"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(row.id)}
                              className="p-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gray-50 dark:bg-gray-800/50">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Showing <span className="font-medium">{((page - 1) * pagination.per_page) + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(page * pagination.per_page, pagination.total)}</span> of{' '}
                  <span className="font-medium">{pagination.total}</span> results
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>

                  <span className="px-4 py-1 text-sm font-medium">
                    Page {page} of {pagination.pages}
                  </span>

                  <button
                    onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
                    disabled={page === pagination.pages}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 animate-fadeIn">
          <div className={`glass-card px-6 py-4 flex items-center gap-3 shadow-lg ${
            toast.type === 'success' 
              ? 'border-l-4 border-green-500' 
              : 'border-l-4 border-red-500'
          }`}>
            {toast.type === 'success' ? (
              <Check className="w-5 h-5 text-green-500" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500" />
            )}
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {toast.message}
            </span>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {confirmDialog.show && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-md p-6 border border-gray-300 dark:border-gray-600 shadow-lg animate-fadeIn">
            <div className="flex items-start gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Confirm Action
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {confirmDialog.title}
                </p>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setConfirmDialog({ ...confirmDialog, show: false })}
                className="px-4 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  if (confirmDialog.action) {
                    await confirmDialog.action();
                  }
                  setConfirmDialog({ show: false, title: '', action: null });
                }}
                className="px-4 py-2 rounded-md text-sm font-medium text-white bg-red-500 hover:bg-red-600 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseManager;