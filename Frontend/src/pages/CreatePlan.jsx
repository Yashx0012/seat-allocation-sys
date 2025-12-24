import React, { useEffect, useState } from 'react';
import { Upload, Layout } from 'lucide-react';

const CreatePlan = ({ setCurrentPage }) => {
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('plans');
      const parsed = raw ? JSON.parse(raw) : [];
      setPlans(parsed.reverse());
    } catch (e) {
      setPlans([]);
    }
  }, []);

  const goAllocate = () => setCurrentPage('allocation');
  const goUpload = () => setCurrentPage('upload');

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <div className="mb-8">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-center mb-12 uppercase text-gray-900 dark:text-white transition-colors duration-300">CREATE PLAN</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <button
            onClick={goAllocate}
            className="flex flex-col items-center gap-3 p-6 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all duration-300 bg-white dark:bg-gray-800"
          >
            <div className="bg-green-500 dark:bg-green-600 p-3 rounded-lg">
              <Layout className="text-white" size={20} />
            </div>
            <span className="font-medium text-gray-700 dark:text-gray-300">Allocate Manually</span>
          </button>

          <button
            onClick={goUpload}
            className="flex flex-col items-center gap-3 p-6 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all duration-300 bg-white dark:bg-gray-800"
          >
            <div className="bg-blue-500 dark:bg-blue-600 p-3 rounded-lg">
              <Upload className="text-white" size={20} />
            </div>
            <span className="font-medium text-gray-700 dark:text-gray-300">Upload</span>
          </button>
        </div>
      </div>

      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-4">Recently Created Plans</h2>
        {plans.length === 0 ? (
          <p className="text-sm text-gray-500">No plans created yet. Create a new plan using the buttons above.</p>
        ) : (
          <ul className="space-y-3">
            {plans.map((p, idx) => (
              <li key={idx} className="flex items-center justify-between p-3 rounded-md bg-gray-50 dark:bg-gray-700">
                <div>
                  <div className="font-semibold text-gray-800 dark:text-gray-100">{p.name || `Plan ${plans.length - idx}`}</div>
                  <div className="text-sm text-gray-500">{p.createdAt ? new Date(p.createdAt).toLocaleString() : '—'}</div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">{p.type || 'Manual'}</div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

export default CreatePlan;
