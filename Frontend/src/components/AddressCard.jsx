import { CheckCircle, MoreVertical } from 'lucide-react';
import { useState } from 'react';

/**
 * Address card component - displays address with optional selection and actions
 */
const AddressCard = ({ 
  address, 
  selected = false,
  onSelect = null,
  onEdit = null,
  onDelete = null,
  onSetDefault = null,
  loading = false,
}) => {
  const [showMenu, setShowMenu] = useState(false);

  if (!address) return null;

  const lineOne = `${address.full_name} • ${address.phone}`;
  const lineTwo = [address.street, address.ward, address.district, address.province, address.country]
    .filter(Boolean)
    .join(', ');

  const isSelectable = !!onSelect;

  return (
    <div
      onClick={() => isSelectable && onSelect?.()}
      className={`rounded-xl border-2 p-5 shadow-sm transition-all cursor-pointer ${
        selected
          ? 'border-orange-500 bg-orange-50/50'
          : 'border-gray-200 bg-white hover:border-gray-300'
      } ${isSelectable && !selected ? 'hover:bg-gray-50' : ''} ${
        loading ? 'opacity-60 pointer-events-none' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Selection Indicator */}
        {isSelectable && (
          <div className="flex-shrink-0 mt-1">
            <div
              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition ${
                selected
                  ? 'border-orange-500 bg-orange-500'
                  : 'border-gray-300 bg-white'
              }`}
            >
              {selected && <div className="w-2 h-2 bg-white rounded-full" />}
            </div>
          </div>
        )}

        {/* Address Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold text-gray-900 truncate">{lineOne}</p>
            {address.is_default && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white/90 px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-orange-600 shadow-sm flex-shrink-0">
                <CheckCircle className="w-3 h-3" />
                Default
              </span>
            )}
          </div>
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{lineTwo}</p>
        </div>

        {/* Actions Menu */}
        {(onEdit || onDelete || onSetDefault) && (
          <div className="relative">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
              disabled={loading}
            >
              <MoreVertical className="w-5 h-5" />
            </button>

            {showMenu && (
              <div className="absolute right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-40">
                {onSetDefault && !address.is_default && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSetDefault?.();
                      setShowMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                  >
                    Set as default
                  </button>
                )}
                {onEdit && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit?.();
                      setShowMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    Edit
                  </button>
                )}
                {onDelete && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete?.();
                      setShowMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 last:rounded-b-lg"
                  >
                    Delete
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AddressCard;
