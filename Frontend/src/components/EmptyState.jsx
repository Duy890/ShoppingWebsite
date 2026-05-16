import { Link } from 'react-router-dom';
import { ShoppingBag, Package, Heart, MapPin, Search, AlertCircle } from 'lucide-react';

const iconMap = {
  cart: ShoppingBag,
  products: Package,
  favorites: Heart,
  addresses: MapPin,
  search: Search,
  default: AlertCircle,
};

const EmptyState = ({
  icon = 'default',
  title = 'Nothing Here',
  description = 'There are no items to display.',
  actionLabel = null,
  actionHref = null,
  actionCallback = null,
  secondary = false,
}) => {
  const Icon = iconMap[icon] || iconMap.default;

  const handleAction = (e) => {
    if (actionCallback) {
      e.preventDefault();
      actionCallback();
    }
  };

  const ActionComponent = actionHref ? Link : 'button';
  const actionProps = actionHref
    ? { to: actionHref }
    : { onClick: handleAction, type: 'button' };

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {/* Icon */}
      <div className="mb-6">
        <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center">
          <Icon className="w-10 h-10 text-slate-400 dark:text-slate-600" strokeWidth={1.5} />
        </div>
      </div>

      {/* Title */}
      <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2 text-center">
        {title}
      </h3>

      {/* Description */}
      <p className="text-slate-600 dark:text-slate-400 text-center mb-6 max-w-sm">
        {description}
      </p>

      {/* Action Button */}
      {actionLabel && (
        <ActionComponent
          {...actionProps}
          className={`inline-flex items-center justify-center px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
            secondary
              ? 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white hover:bg-slate-300 dark:hover:bg-slate-600'
              : 'bg-orange-500 text-white hover:bg-orange-600 shadow-md hover:shadow-lg'
          }`}
        >
          {actionLabel}
        </ActionComponent>
      )}
    </div>
  );
};

export default EmptyState;
