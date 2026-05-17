const AuthCard = ({ children, className = '' }) => {
  return (
    <div className={`overflow-hidden rounded-[28px] border border-slate-200/80 bg-white p-8 shadow-2xl shadow-orange-300/20 transition-all duration-300 dark:border-slate-800 dark:bg-slate-900 dark:shadow-black/20 ${className}`}>
      {children}
    </div>
  );
};

export default AuthCard;
