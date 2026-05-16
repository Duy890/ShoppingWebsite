import { Link } from 'react-router-dom';
import { Home, ChevronRight } from 'lucide-react';
import { useMemo } from 'react';

const Breadcrumbs = ({
  breadcrumbs = [],
  homeLabel = "Trang chủ",
  separator = "/",
  className = '',
  maxLevels = 4,
  showCollapsed = false
}) => {
  const processedBreadcrumbs = useMemo(() => {
    if (!breadcrumbs || breadcrumbs.length === 0) {
      return [];
    }
    return breadcrumbs;
  }, [breadcrumbs]);
  
  const shouldCollapse = showCollapsed && processedBreadcrumbs.length > maxLevels;
  
  const displayCrumbs = useMemo(() => {
    if (shouldCollapse) {
      return [
        processedBreadcrumbs[0],
        { name: '...', url: null, isEllipsis: true },
        ...processedBreadcrumbs.slice(-2)
      ].filter(Boolean);
    }
    return processedBreadcrumbs;
  }, [processedBreadcrumbs, shouldCollapse, maxLevels]);
  
  if (displayCrumbs.length === 0) {
    return null;
  }
  
  return (
    <nav
      className={`flex items-center py-3 px-4 bg-gray-50 rounded-lg ${className}`}
      aria-label="Breadcrumb"
    >
      <ol className="flex items-center flex-wrap gap-x-1 list-none m-0 p-0">
        {homeLabel && (
          <li className="flex items-center">
            <Link
              to="/"
              className="text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1 text-sm font-medium"
              aria-label={homeLabel}
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">{homeLabel}</span>
            </Link>
          </li>
        )}
        {displayCrumbs.map((crumb, index) => {
          if (crumb.isEllipsis) {
            return (
              <li key="ellipsis" className="flex items-center">
                <ChevronRight className="w-4 h-4 text-gray-400 mx-1" />
                <span className="text-gray-400 text-sm">...</span>
              </li>
            );
          }
          
          const isLast = index === displayCrumbs.length - 1;
          const isClickable = crumb.url && !isLast;
          
          return (
            <li key={crumb.url || index} className="flex items-center">
              <ChevronRight className="w-4 h-4 text-gray-400 mx-1 flex-shrink-0" />
              {isClickable ? (
                <Link
                  to={crumb.url}
                  className="text-blue-600 hover:text-blue-800 hover:underline text-sm font-medium transition-colors truncate max-w-[180px] sm:max-w-[220px]"
                >
                  {crumb.name}
                </Link>
              ) : (
                <span
                  className={`text-sm font-medium ${
                    isLast
                      ? 'text-gray-900 font-semibold'
                      : 'text-gray-500'
                  } truncate max-w-[180px] sm:max-w-[220px]'`}
                >
                  {crumb.name}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
export { Breadcrumbs };