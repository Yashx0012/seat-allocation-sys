// frontend/src/components/ErrorBoundary.jsx
import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🔥 ErrorBoundary caught:', error);
    console.error('🔥 Error info:', errorInfo);
    console.error('🔥 Component stack:', errorInfo.componentStack);
    
    this.setState(prev => ({
      error,
      errorInfo,
      errorCount: prev.errorCount + 1
    }));

    // If error keeps happening, clear everything
    if (this.state.errorCount > 2) {
      console.error('🔥 Too many errors, clearing localStorage');
      localStorage.clear();
      sessionStorage.clear();
    }
  }

  handleReset = () => {
    // Clear all state
    localStorage.clear();
    sessionStorage.clear();
    
    // Reset error state
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorCount: 0 
    });
    
    // Force reload
    window.location.href = '/upload';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border-2 border-red-500 p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Application Error
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Something went wrong
                </p>
              </div>
            </div>

            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
              <h3 className="font-bold text-red-900 dark:text-red-100 mb-2">Error Details:</h3>
              <p className="text-sm font-mono text-red-800 dark:text-red-200 break-all">
                {this.state.error?.toString()}
              </p>
              
              {this.state.error?.message?.includes('length') && (
                <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    <strong>Likely cause:</strong> Backend returned invalid data structure. 
                    The session data contains null values where arrays are expected.
                  </p>
                </div>
              )}
            </div>

            <button
              onClick={this.handleReset}
              className="w-full h-14 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold rounded-xl transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              <span>Clear Cache & Restart</span>
            </button>

            <details className="mt-6">
              <summary className="cursor-pointer text-sm font-bold text-gray-700 dark:text-gray-300 hover:text-orange-600 dark:hover:text-orange-400">
                Show Stack Trace
              </summary>
              <pre className="mt-3 p-4 bg-gray-100 dark:bg-gray-900 rounded-lg text-xs overflow-auto max-h-64">
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;