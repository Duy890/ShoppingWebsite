import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Home, ShoppingBag, ArrowLeft } from 'lucide-react';

const NotFound = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Top accent line */}
        <div className="h-1 w-16 bg-orange-500 rounded-full mb-8 mx-auto"></div>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-24 h-24 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
              <AlertCircle className="w-12 h-12 text-orange-500" strokeWidth={1.5} />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-bold">404</span>
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-center text-slate-900 dark:text-white mb-3">
          {t('not_found.title')}
        </h1>

        {/* Description */}
        <p className="text-center text-slate-600 dark:text-slate-400 mb-2">
          {t('not_found.desc')}
        </p>
        <p className="text-center text-slate-500 dark:text-slate-500 text-sm mb-8">
          It might have been moved or deleted. Let's get you back on track.
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

          <button
            onClick={() => window.history.back()}
            className="flex items-center justify-center gap-2 w-full px-6 py-3 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg font-medium transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            {t('edit_profile.back')}
          </button>
        </div>

        {/* Footer hint */}
        <p className="text-center text-slate-500 dark:text-slate-400 text-xs mt-8">
          Error Code: 404 | {t('not_found.title')}
        </p>
      </div>
    </div>
  );
};

export default NotFound;
