import { ShoppingBag } from 'lucide-react';

const AuthLayout = ({ title, subtitle, children }) => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4 py-12">
      <div className="absolute inset-x-0 top-0 h-48 bg-gradient-to-r from-primary/15 via-orange-100 to-white opacity-90 dark:from-orange-500/10 dark:via-slate-950 dark:to-slate-950" />
      <div className="relative w-full max-w-xl">
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center gap-3 rounded-full border border-orange-200 bg-white/90 px-5 py-3 text-sm font-semibold text-orange-700 shadow-sm shadow-orange-200/40 backdrop-blur-sm dark:border-orange-500/20 dark:bg-slate-900/80 dark:text-orange-300">
            <ShoppingBag className="h-5 w-5 text-primary" />
            <span>Electronics Store</span>
          </div>
          {title && (
            <h1 className="mt-8 text-3xl font-black tracking-tight text-slate-950 dark:text-slate-100 sm:text-4xl">
              {title}
            </h1>
          )}
          {subtitle && (
            <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-600 dark:text-slate-400">
              {subtitle}
            </p>
          )}
        </div>
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
