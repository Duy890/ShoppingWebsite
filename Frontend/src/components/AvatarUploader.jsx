import { Camera, User } from 'lucide-react';

const AvatarUploader = ({ avatarUrl, previewUrl, onClick, inputRef, onFileChange }) => {
  const displayUrl = previewUrl || avatarUrl;

  return (
    <div className="relative inline-flex">
      <button
        type="button"
        onClick={onClick}
        className="group relative w-28 h-28 rounded-full overflow-hidden border-2 border-primary/20 bg-white shadow-sm transition-transform duration-200 hover:scale-[1.03] focus:outline-none focus:ring-2 focus:ring-primary/50"
      >
        {displayUrl ? (
          <img
            src={displayUrl}
            alt="Avatar"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-primary/5 text-primary">
            <User className="w-10 h-10" />
          </div>
        )}

        <div className="absolute inset-0 bg-black/0 transition duration-200 group-hover:bg-black/15" />
        <div className="absolute inset-x-0 bottom-2 flex justify-center opacity-0 transition duration-200 group-hover:opacity-100">
          <span className="inline-flex items-center gap-2 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-gray-700 shadow-sm">
            <Camera className="w-3.5 h-3.5" />
            Change
          </span>
        </div>
      </button>

      <input
        type="file"
        accept="image/*"
        ref={inputRef}
        className="hidden"
        onChange={onFileChange}
      />
    </div>
  );
};

export default AvatarUploader;
