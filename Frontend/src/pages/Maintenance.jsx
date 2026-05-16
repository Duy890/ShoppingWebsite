import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Wrench, Home, RefreshCw } from 'lucide-react';

const Maintenance = () => {
  const [timeElapsed, setTimeElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    window.location.reload();
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Top accent line */}
        <div className="h-1 w-16 bg-orange-500 rounded-full mb-8 mx-auto"></div>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-24 h-24 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center animate-pulse">
              <Wrench className="w-12 h-12 text-orange-500" strokeWidth={1.5} />
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-center text-slate-900 dark:text-white mb-3">
          Under Maintenance
        </h1>

        {/* Description */}
        <p className="text-center text-slate-600 dark:text-slate-400 mb-2">
          We're making improvements to serve you better.
        </p>
        <p className="text-center text-slate-500 dark:text-slate-500 text-sm mb-8">
          Our system will be back online soon. We apologize for the inconvenience.
        </p>

        {/* Status Info Box */}
        <div className="bg-white dark:bg-slate-800 rounded-lg border-2 border-orange-200 dark:border-orange-900/30 p-6 mb-8">
          <div className="text-center">
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Time elapsed</p>
            <p className="text-3xl font-mono font-bold text-orange-600 dark:text-orange-400">
              {formatTime(timeElapsed)}
            </p>
            <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/10 rounded-lg">
              <p className="text-sm text-slate-700 dark:text-slate-300">
                ✓ We're making important upgrades
              </p>
              <p className="text-sm text-slate-700 dark:text-slate-300 mt-1">
                ✓ Expected downtime: 30-60 minutes
              </p>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleRefresh}
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <RefreshCw className="w-5 h-5" />
            Check Status
          </button>

          <Link
            to="/"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-2 border-slate-300 dark:border-slate-600 rounded-lg font-semibold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200"
          >
            <Home className="w-5 h-5" />
            Try Home Page
          </Link>
        </div>

        {/* Support notification */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-900/30 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-300">
            <span className="font-semibold">Questions?</span> Check our{' '}
            <a href="#" className="underline hover:no-underline font-semibold">
              status page
            </a>
            {' '}for updates.
          </p>
        </div>

        {/* Footer hint */}
        <p className="text-center text-slate-500 dark:text-slate-400 text-xs mt-8">
          Status: 503 | Service Temporarily Unavailable
        </p>
      </div>
    </div>
  );
};

export default Maintenance;
