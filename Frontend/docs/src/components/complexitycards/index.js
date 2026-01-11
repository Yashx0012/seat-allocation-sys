import React from 'react';

export default function App() {
    return (
        <div id="ca-isolated-wrapper" className="ca-wrapper">
            <style>{`
        /* --- HIGH SPECIFICITY ISOLATION --- 
           Using #ca-isolated-wrapper ensures these styles override Docusaurus/Infima 
        */

        #ca-isolated-wrapper {
          width: 100%;
          background-color: transparent; /* Changed from #f8fafc to transparent */
          color: #0f172a; /* slate-900 */
          font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
          /* Reset common Docusaurus container styles */
          padding: 1rem;
          margin: 0;
          line-height: 1.5;
          box-sizing: border-box;
          border-radius: 8px;
        }

        #ca-isolated-wrapper * {
          box-sizing: border-box;
        }

        @media (min-width: 768px) {
          #ca-isolated-wrapper {
            padding: 2rem;
          }
        }

        #ca-isolated-wrapper .ca-content {
          width: 100%;
          max-width: 72rem; /* max-w-6xl */
          margin: 0 auto;
        }

        #ca-isolated-wrapper .ca-title {
          font-size: 1.5rem; /* text-2xl */
          line-height: 2rem;
          font-weight: 700;
          margin-bottom: 1rem;
          color: #1e293b; /* slate-800 */
          margin-top: 0;
          border: none; /* Reset potential Docusaurus headings borders */
        }

        /* --- Grid Layout --- */
        #ca-isolated-wrapper .ca-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem; /* gap-6 */
          margin-top: 2rem;
          margin-bottom: 2rem;
        }

        @media (min-width: 768px) {
          #ca-isolated-wrapper .ca-grid {
            grid-template-columns: repeat(2, 1fr); 
          }
        }

        /* --- Card Styles --- */
        #ca-isolated-wrapper .ca-card {
          background-color: white;
          border-radius: 0.75rem; /* rounded-xl */
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* shadow-sm */
          border: 1px solid #e2e8f0; /* slate-200 */
          overflow: hidden;
          display: flex;
          flex-direction: column;
          margin: 0; /* Reset margins */
        }

        /* --- Header Styles --- */
        #ca-isolated-wrapper .ca-header {
          padding: 1rem 1.25rem;
          border-bottom-width: 1px;
          border-bottom-style: solid;
          background-image: none; /* Reset gradients */
        }

        #ca-isolated-wrapper .ca-header h3 {
          margin: 0;
          font-size: 1.125rem; /* text-lg */
          font-weight: 700;
          line-height: 1.5;
          border: none;
          padding: 0;
        }

        /* --- Theme Specifics --- */
        /* Indigo */
        #ca-isolated-wrapper .ca-theme-indigo .ca-header {
          background-color: #eef2ff;
          border-bottom-color: #e0e7ff;
        }
        #ca-isolated-wrapper .ca-theme-indigo .ca-header h3 { color: #312e81; }
        
        /* Emerald */
        #ca-isolated-wrapper .ca-theme-emerald .ca-header {
          background-color: #ecfdf5;
          border-bottom-color: #d1fae5;
        }
        #ca-isolated-wrapper .ca-theme-emerald .ca-header h3 { color: #064e3b; }

        /* Amber */
        #ca-isolated-wrapper .ca-theme-amber .ca-header {
          background-color: #fffbeb;
          border-bottom-color: #fef3c7;
        }
        #ca-isolated-wrapper .ca-theme-amber .ca-header h3 { color: #78350f; }

        /* --- Table Resets (Critical for Docusaurus) --- */
        #ca-isolated-wrapper .ca-table-responsive {
          padding: 0;
          overflow-x: auto;
          width: 100%;
          border: none;
          margin: 0;
        }

        #ca-isolated-wrapper table.ca-table {
          width: 100%;
          font-size: 0.875rem; /* text-sm */
          text-align: left;
          border-collapse: collapse !important; /* Force collapse */
          margin: 0 !important;
          display: table !important; /* Override potential block display */
          border: none !important;
          background: transparent !important;
        }

        #ca-isolated-wrapper table.ca-table thead {
          background-color: #1e293b; /* slate-800 */
          color: #cbd5e1; /* slate-300 */
          text-transform: uppercase;
          font-size: 0.75rem; /* text-xs */
          font-weight: 700;
          border: none;
        }

        #ca-isolated-wrapper table.ca-table th {
          padding: 0.75rem 1rem;
          font-weight: 600;
          border-bottom: 1px solid #334155;
          border-top: none;
          border-left: none;
          border-right: none;
          background: transparent;
        }

        #ca-isolated-wrapper table.ca-table td {
          padding: 0.75rem 1rem;
          border-bottom: 1px solid #e2e8f0;
          vertical-align: middle;
          border-top: none;
          border-left: none;
          border-right: none;
          background: transparent;
        }

        #ca-isolated-wrapper table.ca-table tr {
          background-color: transparent !important;
          border: none;
        }

        #ca-isolated-wrapper table.ca-table tr:last-child td {
          border-bottom: none;
        }

        /* --- Row Highlights & Text Helpers --- */
        #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight { background-color: #eef2ff !important; font-weight: 700; }
        #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight td { color: #4338ca; }

        #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight { background-color: #ecfdf5 !important; font-weight: 700; }
        #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight td { color: #047857; }

        #ca-isolated-wrapper .ca-font-mono {
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        }
        #ca-isolated-wrapper .ca-font-semibold { font-weight: 600; }
        #ca-isolated-wrapper .ca-font-bold { font-weight: 700; }
        #ca-isolated-wrapper .ca-text-xs { font-size: 0.75rem; }

        #ca-isolated-wrapper .ca-text-details { color: #64748b; }
        #ca-isolated-wrapper .ca-text-pink { color: #db2777; }
        #ca-isolated-wrapper .ca-text-emerald { color: #059669; }
        #ca-isolated-wrapper .ca-text-amber { color: #d97706; }

        /* --- Dark Mode Support --- */
        @media (prefers-color-scheme: dark) {
          #ca-isolated-wrapper { background-color: transparent; color: #f1f5f9; border: none; } /* Set bg to transparent */
          #ca-isolated-wrapper .ca-title { color: #e2e8f0; }
          #ca-isolated-wrapper .ca-card { background-color: #0f172a; border-color: #334155; }
          #ca-isolated-wrapper table.ca-table td { border-bottom-color: #334155; }
          #ca-isolated-wrapper .ca-text-details { color: #94a3b8; }

          /* Indigo Dark */
          #ca-isolated-wrapper .ca-theme-indigo .ca-header { background-color: rgba(49, 46, 129, 0.2); border-bottom-color: #3730a3; }
          #ca-isolated-wrapper .ca-theme-indigo .ca-header h3 { color: #a5b4fc; }
          #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight { background-color: rgba(49, 46, 129, 0.1) !important; }
          #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight td { color: #a5b4fc; }
          
          /* Emerald Dark */
          #ca-isolated-wrapper .ca-theme-emerald .ca-header { background-color: rgba(6, 78, 59, 0.2); border-bottom-color: #065f46; }
          #ca-isolated-wrapper .ca-theme-emerald .ca-header h3 { color: #6ee7b7; }
          #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight { background-color: rgba(6, 78, 59, 0.1) !important; }
          #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight td { color: #6ee7b7; }

          /* Amber Dark */
          #ca-isolated-wrapper .ca-theme-amber .ca-header { background-color: rgba(120, 53, 15, 0.2); border-bottom-color: #92400e; }
          #ca-isolated-wrapper .ca-theme-amber .ca-header h3 { color: #fcd34d; }

          #ca-isolated-wrapper .ca-text-pink { color: #f472b6; }
          #ca-isolated-wrapper .ca-text-emerald { color: #34d399; }
          #ca-isolated-wrapper .ca-text-amber { color: #fbbf24; }
        }
        
        /* --- Docusaurus Dark Mode Explicit Override --- */
        [data-theme='dark'] #ca-isolated-wrapper { background-color: transparent; color: #f1f5f9; border: none; } /* Set bg to transparent */
        [data-theme='dark'] #ca-isolated-wrapper .ca-title { color: #e2e8f0; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-card { background-color: #0f172a; border-color: #334155; }
        [data-theme='dark'] #ca-isolated-wrapper table.ca-table td { border-bottom-color: #334155; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-text-details { color: #94a3b8; }
        
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-indigo .ca-header { background-color: rgba(49, 46, 129, 0.2); border-bottom-color: #3730a3; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-indigo .ca-header h3 { color: #a5b4fc; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight { background-color: rgba(49, 46, 129, 0.1) !important; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-indigo .ca-row-highlight td { color: #a5b4fc; }

        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-emerald .ca-header { background-color: rgba(6, 78, 59, 0.2); border-bottom-color: #065f46; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-emerald .ca-header h3 { color: #6ee7b7; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight { background-color: rgba(6, 78, 59, 0.1) !important; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-emerald .ca-row-highlight td { color: #6ee7b7; }

        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-amber .ca-header { background-color: rgba(120, 53, 15, 0.2); border-bottom-color: #92400e; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-theme-amber .ca-header h3 { color: #fcd34d; }

        [data-theme='dark'] #ca-isolated-wrapper .ca-text-pink { color: #f472b6; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-text-emerald { color: #34d399; }
        [data-theme='dark'] #ca-isolated-wrapper .ca-text-amber { color: #fbbf24; }
      `}</style>

            <div className="ca-content">

                <div className="ca-grid">

                    {/* Card 1: Time Complexity */}
                    <div className="ca-card ca-theme-indigo">
                        <div className="ca-header">
                            <h3>Time Complexity</h3>
                        </div>
                        <div className="ca-table-responsive">
                            <table className="ca-table">
                                <thead>
                                    <tr>
                                        <th>Operation</th>
                                        <th>Complexity</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Initialization</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(R × C)</td>
                                        <td className="ca-text-details">Grid creation</td>
                                    </tr>
                                    <tr>
                                        <td>Batch Assign</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(C)</td>
                                        <td className="ca-text-details">Col dist.</td>
                                    </tr>
                                    <tr>
                                        <td>Allocation</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(R × C)</td>
                                        <td className="ca-text-details">Fill seats</td>
                                    </tr>
                                    <tr>
                                        <td>Validation</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(R × C)</td>
                                        <td className="ca-text-details">Constraints</td>
                                    </tr>
                                    <tr className="ca-row-highlight">
                                        <td>Overall</td>
                                        <td className="ca-font-mono">O(R × C)</td>
                                        <td>Linear</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Card 2: Space Complexity */}
                    <div className="ca-card ca-theme-emerald">
                        <div className="ca-header">
                            <h3>Space Complexity</h3>
                        </div>
                        <div className="ca-table-responsive">
                            <table className="ca-table">
                                <thead>
                                    <tr>
                                        <th>Component</th>
                                        <th>Complexity</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Seating Grid</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(R × C)</td>
                                        <td className="ca-text-details">2D array</td>
                                    </tr>
                                    <tr>
                                        <td>Mapping</td>
                                        <td className="ca-font-mono ca-text-pink ca-font-semibold">O(N)</td>
                                        <td className="ca-text-details">Tracking</td>
                                    </tr>
                                    <tr className="ca-row-highlight">
                                        <td>Overall</td>
                                        <td className="ca-font-mono">O(R × C)</td>
                                        <td>Dominated</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Card 3: Benchmarks */}
                    <div className="ca-card ca-theme-amber">
                        <div className="ca-header">
                            <h3>Benchmarks</h3>
                        </div>
                        <div className="ca-table-responsive">
                            <table className="ca-table">
                                <thead>
                                    <tr>
                                        <th>Size</th>
                                        <th>Time</th>
                                        <th>Memory</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td className="ca-font-mono ca-text-xs">10×10</td>
                                        <td className="ca-text-emerald ca-font-bold">&lt; 10ms</td>
                                        <td className="ca-text-details">&lt; 1MB</td>
                                    </tr>
                                    <tr>
                                        <td className="ca-font-mono ca-text-xs">50×50</td>
                                        <td className="ca-text-emerald ca-font-bold">&lt; 50ms</td>
                                        <td className="ca-text-details">&lt; 5MB</td>
                                    </tr>
                                    <tr>
                                        <td className="ca-font-mono ca-text-xs">100×100</td>
                                        <td className="ca-text-amber ca-font-bold">&lt; 100ms</td>
                                        <td className="ca-text-details">&lt; 15MB</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}