import { useEffect, useState } from 'react';
import { WifiOff, Wifi, X } from 'lucide-react';

const OfflineBanner = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Auto-hide after 3 seconds
      setTimeout(() => setIsVisible(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsVisible(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isVisible && !isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-red-500 dark:bg-red-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <WifiOff className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-sm">No Internet Connection</p>
              <p className="text-xs opacity-90">Some features may not be available</p>
            </div>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="ml-4 p-1 hover:bg-red-600 dark:hover:bg-red-700 rounded transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  if (isVisible && isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-green-500 dark:bg-green-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Wifi className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-sm">You're Back Online</p>
              <p className="text-xs opacity-90">Connection restored</p>
            </div>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="ml-4 p-1 hover:bg-green-600 dark:hover:bg-green-700 rounded transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default OfflineBanner;
