import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Lock, Home, ShoppingBag } from 'lucide-react';

const AccessDenied = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Top accent line */}
        <div className="h-1 w-16 bg-red-500 rounded-full mb-8 mx-auto"></div>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-24 h-24 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <Lock className="w-12 h-12 text-red-500" strokeWidth={1.5} />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-bold">403</span>
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-center text-slate-900 dark:text-white mb-3">
          {t('access_denied.title')}
        </h1>

        {/* Description */}
        <p className="text-center text-slate-600 dark:text-slate-400 mb-2">
          {t('access_denied.desc')}
        </p>
        <p className="text-center text-slate-500 dark:text-slate-500 text-sm mb-8">
          {t('access_denied.hint')}
        </p>

        {/* CTA Buttons */}
        <div className="space-y-3">
          <Link
            to="/"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <Home className="w-5 h-5" />
            {t('not_found.back_home')}
          </Link>

          <Link
            to="/products"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-white dark:bg-slate-800 text-orange-600 dark:text-orange-400 border-2 border-orange-500 rounded-lg font-semibold hover:bg-orange-50 dark:hover:bg-slate-700 transition-all duration-200"
          >
            <ShoppingBag className="w-5 h-5" />
            {t('wishlist.browse_products')}
          </Link>
        </div>

        {/* Support info */}
        <div className="mt-8 p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-700 dark:text-slate-300 font-semibold mb-2">
            Need Help?
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Contact our support team at{' '}
            <a href="mailto:support@eshop.local" className="text-orange-600 dark:text-orange-400 hover:underline">
              support@eshop.local
            </a>
          </p>
        </div>

        {/* Footer hint */}
        <p className="text-center text-slate-500 dark:text-slate-400 text-xs mt-8">
          Error Code: 403 | Forbidden
        </p>
      </div>
    </div>
  );
};

export default AccessDenied;
