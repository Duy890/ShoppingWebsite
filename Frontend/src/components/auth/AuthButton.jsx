import { Loader2 } from 'lucide-react';

const AuthButton = ({ loading, children, className = '', ...props }) => {
  return (
    <button
      type={props.type ?? 'button'}
      className={`relative inline-flex w-full items-center justify-center rounded-2xl bg-primary px-6 py-4 text-sm font-semibold text-white shadow-sm shadow-primary/25 transition duration-200 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="inline-flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-white" />
          <span>{children}</span>
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default AuthButton;
