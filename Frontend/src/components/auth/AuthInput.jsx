const AuthInput = ({ label, name, type = 'text', value, onChange, placeholder, error, ...props }) => {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="block text-sm font-semibold text-slate-700 dark:text-slate-200">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-2xl border px-4 py-4 text-sm text-slate-900 shadow-sm transition duration-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500 ${error ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-200' : 'border-slate-200 dark:border-slate-700'}`}
        {...props}
      />
      {error && <p className="text-sm text-rose-500">{error}</p>}
    </div>
  );
};

export default AuthInput;
