// src/components/database/DatabaseTableView.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Trash2,
  Edit2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  FileDown,
  Check,
  X
} from 'lucide-react';
import useDatabaseApi from './hooks/useDatabaseApi';
import DeleteConfirmModal from './DeleteConfirmModal';

const TABLES = [
  { name: 'students', label: 'Students', icon: '👨‍🎓' },
  { name: 'classrooms', label: 'Classrooms', icon: '🏫' },
  { name: 'uploads', label: 'Uploads', icon: '📤' },
  { name: 'allocations', label: 'Allocations', icon: '📍' },
  { name: 'feedback', label: 'Feedback', icon: '💬' }
];

const DatabaseTableView = ({ onToast }) => {
  const [selectedTable, setSelectedTable] = useState('students');
  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [overview, setOverview] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 50 });
  const [selectedRows, setSelectedRows] = useState([]);
  const [editingRow, setEditingRow] = useState(null);
  const [editValues, setEditValues] = useState({});
  const [deleteModal, setDeleteModal] = useState({ open: false, type: null, data: null });
  const [isDeleting, setIsDeleting] = useState(false);

  const {
    loading,
    fetchOverview,
    fetchTableData,
    updateRecord,
    deleteRecord,
    bulkDeleteRecords,
    exportTable
  } = useDatabaseApi();

  // Load overview
  const loadOverview = useCallback(async () => {
    const data = await fetchOverview();
    if (data) setOverview(data);
  }, [fetchOverview]);

  // Load table data
  const loadTableData = useCallback(async () => {
    const result = await fetchTableData(selectedTable, {
      page,
      perPage: 50,
      search: searchQuery,
      sortBy: 'id',
      sortOrder: 'DESC'
    });

    setTableData(result.data);
    setColumns(result.columns);
    setPagination(result.pagination);
  }, [fetchTableData, selectedTable, page, searchQuery]);

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    loadTableData();
    setSelectedRows([]);
    setEditingRow(null);
  }, [selectedTable, page, searchQuery, loadTableData]);

  const handleEdit = (row) => {
    setEditingRow(row.id);
    setEditValues({ ...row });
  };

  const handleSaveEdit = async () => {
    const result = await updateRecord(selectedTable, editingRow, editValues);
    if (result.success) {
      onToast?.('Record updated successfully', 'success');
      setEditingRow(null);
      loadTableData();
    } else {
      onToast?.(result.error, 'error');
    }
  };

  const handleCancelEdit = () => {
    setEditingRow(null);
    setEditValues({});
  };

  const handleDelete = (id) => {
    setDeleteModal({
      open: true,
      type: 'single',
      data: { id }
    });
  };

  const handleBulkDelete = () => {
    if (selectedRows.length === 0) return;
    setDeleteModal({
      open: true,
      type: 'bulk',
      data: { ids: selectedRows }
    });
  };

  const confirmDelete = async () => {
    setIsDeleting(true);
    const { type, data } = deleteModal;

    let result;
    if (type === 'single') {
      result = await deleteRecord(selectedTable, data.id);
    } else {
      result = await bulkDeleteRecords(selectedTable, data.ids);
    }

    setIsDeleting(false);
    setDeleteModal({ open: false, type: null, data: null });

    if (result.success) {
      onToast?.(result.message || 'Deleted successfully', 'success');
      setSelectedRows([]);
      loadTableData();
      loadOverview();
    } else {
      onToast?.(result.error, 'error');
    }
  };

  const handleExport = async () => {
    const result = await exportTable(selectedTable);
    if (result.success) {
      onToast?.('Table exported successfully', 'success');
    } else {
      onToast?.(result.error || 'Export failed', 'error');
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
    <>
      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(overview.tables).map(([table, count]) => (
            <button
              key={table}
              onClick={() => { setSelectedTable(table); setPage(1); setSearchQuery(''); }}
              className={`p-4 rounded-xl text-left transition-all border-2 ${
                selectedTable === table
                  ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20 shadow-lg shadow-orange-500/10'
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-orange-300'
              }`}
            >
              <div className="text-2xl mb-1">
                {TABLES.find(t => t.name === table)?.icon || '📊'}
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {count.toLocaleString()}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400 capitalize">
                {table}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 flex-1 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search records..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 outline-none text-sm"
            />
          </div>

          {/* Bulk Delete */}
          {selectedRows.length > 0 && (
            <button
              onClick={handleBulkDelete}
              className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 text-sm flex items-center gap-2 whitespace-nowrap"
            >
              <Trash2 className="w-4 h-4" />
              Delete ({selectedRows.length})
            </button>
          )}
        </div>

        <button
          onClick={handleExport}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2 text-sm whitespace-nowrap"
        >
          <FileDown className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left w-12">
                      <input
                        type="checkbox"
                        checked={selectedRows.length === tableData.length && tableData.length > 0}
                        onChange={toggleAllRows}
                        className="rounded border-gray-300"
                      />
                    </th>
                    {columns.map((col) => (
                      <th
                        key={col.name}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
                      >
                        {col.name}
                        {col.primary_key && <span className="ml-1 text-orange-500">🔑</span>}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {tableData.length === 0 ? (
                    <tr>
                      <td colSpan={columns.length + 2} className="px-4 py-12 text-center text-gray-500">
                        No records found
                      </td>
                    </tr>
                  ) : (
                    tableData.map((row) => (
                      <tr
                        key={row.id}
                        className={`hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${
                          selectedRows.includes(row.id) ? 'bg-orange-50 dark:bg-orange-900/10' : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selectedRows.includes(row.id)}
                            onChange={() => toggleRowSelection(row.id)}
                            className="rounded border-gray-300"
                          />
                        </td>
                        {columns.map((col) => (
                          <td
                            key={col.name}
                            className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate"
                          >
                            {editingRow === row.id ? (
                              <input
                                type="text"
                                value={editValues[col.name] ?? ''}
                                onChange={(e) => setEditValues(prev => ({ ...prev, [col.name]: e.target.value }))}
                                className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-900"
                              />
                            ) : (
                              <span title={row[col.name]}>
                                {row[col.name] ?? <span className="text-gray-400 italic">NULL</span>}
                              </span>
                            )}
                          </td>
                        ))}
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            {editingRow === row.id ? (
                              <>
                                <button
                                  onClick={handleSaveEdit}
                                  className="p-1.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 rounded transition-colors"
                                  title="Save"
                                >
                                  <Check className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={handleCancelEdit}
                                  className="p-1.5 text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                                  title="Cancel"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleEdit(row)}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                                  title="Edit"
                                >
                                  <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDelete(row.id)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row items-center justify-between gap-3 bg-gray-50 dark:bg-gray-900/50">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Showing <span className="font-medium">{Math.min(((page - 1) * pagination.per_page) + 1, pagination.total)}</span> to{' '}
                <span className="font-medium">{Math.min(page * pagination.per_page, pagination.total)}</span> of{' '}
                <span className="font-medium">{pagination.total}</span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <span className="px-4 py-2 text-sm font-medium">
                  {page} / {pagination.pages || 1}
                </span>

                <button
                  onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
                  disabled={page >= pagination.pages}
                  className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={deleteModal.open}
        onClose={() => setDeleteModal({ open: false, type: null, data: null })}
        onConfirm={confirmDelete}
        isLoading={isDeleting}
        title={deleteModal.type === 'bulk' ? `Delete ${deleteModal.data?.ids?.length} Records?` : 'Delete Record?'}
        message={
          deleteModal.type === 'bulk'
            ? `Are you sure you want to delete ${deleteModal.data?.ids?.length} selected records?`
            : 'Are you sure you want to delete this record?'
        }
      />
    </>
  );
};

export default DatabaseTableView;