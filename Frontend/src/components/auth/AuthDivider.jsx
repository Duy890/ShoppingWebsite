const AuthDivider = ({ label = 'or' }) => {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-400 dark:text-slate-500">
      <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
      <span>{label}</span>
      <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
    </div>
  );
};

export default AuthDivider;
