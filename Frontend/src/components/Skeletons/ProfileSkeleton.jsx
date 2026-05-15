const ProfileSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    {/* Avatar section skeleton */}
    <div className="bg-white dark:bg-slate-800 rounded-lg p-6">
      <div className="flex items-center gap-6">
        <div className="w-24 h-24 bg-slate-300 dark:bg-slate-700 rounded-full"></div>
        <div className="flex-1">
          <div className="h-6 bg-slate-300 dark:bg-slate-700 rounded w-48 mb-3"></div>
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-32 mb-4"></div>
          <div className="h-10 bg-slate-300 dark:bg-slate-700 rounded w-32"></div>
        </div>
      </div>
    </div>

    {/* Addresses section skeleton */}
    <div className="bg-white dark:bg-slate-800 rounded-lg p-6">
      <div className="h-6 bg-slate-300 dark:bg-slate-700 rounded w-40 mb-4"></div>

      {/* Address cards skeleton */}
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
            <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-48 mb-2"></div>
            <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-64 mb-2"></div>
            <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-56"></div>
          </div>
        ))}
      </div>

      <div className="mt-4 h-10 bg-slate-300 dark:bg-slate-700 rounded w-full"></div>
    </div>
  </div>
);

export default ProfileSkeleton;
