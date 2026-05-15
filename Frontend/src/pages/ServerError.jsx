import { Link } from 'react-router-dom';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

const ServerError = () => {
  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Top accent line */}
        <div className="h-1 w-16 bg-red-500 rounded-full mb-8 mx-auto"></div>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-24 h-24 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-12 h-12 text-red-500" strokeWidth={1.5} />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-bold">500</span>
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-center text-slate-900 dark:text-white mb-3">
          Something Went Wrong
        </h1>

        {/* Description */}
        <p className="text-center text-slate-600 dark:text-slate-400 mb-2">
          We encountered an unexpected error while processing your request.
        </p>
        <p className="text-center text-slate-500 dark:text-slate-500 text-sm mb-8">
          Our team has been notified and is working on fixing the issue.
        </p>

        {/* CTA Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleRetry}
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <RefreshCw className="w-5 h-5" />
            Try Again
          </button>

          <Link
            to="/"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-white dark:bg-slate-800 text-orange-600 dark:text-orange-400 border-2 border-orange-500 rounded-lg font-semibold hover:bg-orange-50 dark:hover:bg-slate-700 transition-all duration-200"
          >
            <Home className="w-5 h-5" />
            Back to Home
          </Link>
        </div>

        {/* Support info */}
        <div className="mt-8 p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-700 dark:text-slate-300">
            <span className="font-semibold">Need help?</span> Contact our support team at{' '}
            <a href="mailto:support@eshop.local" className="text-orange-600 dark:text-orange-400 hover:underline">
              support@eshop.local
            </a>
          </p>
        </div>

        {/* Footer hint */}
        <p className="text-center text-slate-500 dark:text-slate-400 text-xs mt-8">
          Error Code: 500 | Internal Server Error
        </p>
      </div>
    </div>
  );
};

export default ServerError;
