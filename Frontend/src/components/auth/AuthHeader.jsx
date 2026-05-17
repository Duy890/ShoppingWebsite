const AuthHeader = ({ title, description }) => {
  return (
    <div className="space-y-4 text-center">
      <div className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-primary/10 text-primary">
        <span className="text-lg font-black">A</span>
      </div>
      <div>
        <h2 className="text-2xl font-black tracking-tight text-slate-950 dark:text-slate-100 sm:text-3xl">
          {title}
        </h2>
        {description && <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{description}</p>}
      </div>
    </div>
  );
};

export default AuthHeader;
