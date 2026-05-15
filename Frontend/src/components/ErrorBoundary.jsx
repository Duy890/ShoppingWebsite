import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }

    this.setState((prevState) => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Log to error tracking service (e.g., Sentry) in production
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center px-4">
          <div className="max-w-md w-full">
            {/* Top accent line */}
            <div className="h-1 w-16 bg-red-500 rounded-full mb-8 mx-auto"></div>

            {/* Icon */}
            <div className="flex justify-center mb-6">
              <div className="w-24 h-24 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-12 h-12 text-red-500" strokeWidth={1.5} />
              </div>
            </div>

            {/* Title */}
            <h1 className="text-4xl font-bold text-center text-slate-900 dark:text-white mb-3">
              Oops! Something Broke
            </h1>

            {/* Description */}
            <p className="text-center text-slate-600 dark:text-slate-400 mb-2">
              An unexpected error occurred in the application.
            </p>
            <p className="text-center text-slate-500 dark:text-slate-500 text-sm mb-8">
              We're sorry for the inconvenience. Please try refreshing the page.
            </p>

            {/* Error Details (Development Only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-900/50 rounded-lg">
                <p className="text-xs font-mono text-red-800 dark:text-red-300 break-words">
                  <strong>Error:</strong> {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <p className="text-xs font-mono text-red-700 dark:text-red-400 mt-2 break-words">
                    <strong>Details:</strong> {this.state.errorInfo.componentStack.substring(0, 200)}...
                  </p>
                )}
              </div>
            )}

            {/* CTA Buttons */}
            <div className="space-y-3">
              <button
                onClick={this.handleReset}
                className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <RefreshCw className="w-5 h-5" />
                Try Again
              </button>

              <button
                onClick={this.handleReload}
                className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-2 border-slate-300 dark:border-slate-600 rounded-lg font-semibold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200"
              >
                <RefreshCw className="w-5 h-5" />
                Reload Page
              </button>

              <a
                href="/"
                className="flex items-center justify-center gap-2 w-full px-6 py-3 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg font-medium transition-all duration-200"
              >
                <Home className="w-5 h-5" />
                Go to Home
              </a>
            </div>

            {/* Footer hint */}
            <p className="text-center text-slate-500 dark:text-slate-400 text-xs mt-8">
              Error occurrences: {this.state.errorCount}
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
