import { useEffect, useRef } from 'react';
import { MoreVertical } from 'lucide-react';

const dropdownItems = [
  { id: 'rename', label: 'Rename Profile' },
  { id: 'avatar', label: 'Change Avatar' },
  { id: 'address', label: 'Add Address' },
];

const ProfileDropdown = ({ open, onToggle, onSelect }) => {
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        onToggle(false);
      }
    };

    if (open) {
      window.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      window.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open, onToggle]);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => onToggle(!open)}
        className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
        aria-label="Profile actions"
      >
        <MoreVertical className="w-5 h-5" />
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-2 w-48 overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-xl">
          {dropdownItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onSelect(item.id)}
              className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProfileDropdown;
