import { useState, useRef, useEffect } from 'react';
import { ChevronDown, X } from 'lucide-react';

/**
 * Reusable searchable combobox component
 * Used for province, district, ward selections
 */
const Combobox = ({
  options = [],
  value = null,
  onChange,
  placeholder = 'Select...',
  label,
  disabled = false,
  searchable = true,
  getOptionLabel = (opt) => opt.name,
  getOptionValue = (opt) => opt.code,
}) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef(null);
  const inputRef = useRef(null);

  // Filter options based on search
  const filteredOptions = search.trim()
    ? options.filter(opt =>
        getOptionLabel(opt).toLowerCase().includes(search.toLowerCase())
      )
    : options;

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!open) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev =>
          prev < filteredOptions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0) {
          selectOption(filteredOptions[highlightedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setOpen(false);
        setSearch('');
        break;
      default:
        break;
    }
  };

  const selectOption = (option) => {
    onChange(option);
    setOpen(false);
    setSearch('');
    setHighlightedIndex(-1);
  };

  const selectedLabel = value ? getOptionLabel(value) : '';

  return (
    <div ref={containerRef} className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}

      <div className="relative">
        <button
          type="button"
          disabled={disabled}
          onClick={() => {
            if (!disabled) {
              setOpen(!open);
              if (!open) inputRef.current?.focus();
            }
          }}
          className={`w-full px-4 py-3 rounded-xl border text-left flex items-center justify-between transition-all ${
            disabled
              ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
              : 'bg-white border-gray-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent'
          } ${open ? 'ring-2 ring-orange-500 border-orange-500' : ''}`}
        >
          <span className={selectedLabel ? 'text-gray-900' : 'text-gray-500'}>
            {selectedLabel || placeholder}
          </span>
          <ChevronDown
            className={`w-5 h-5 transition-transform ${
              open ? 'transform rotate-180' : ''
            } ${disabled ? 'text-gray-400' : 'text-gray-600'}`}
          />
        </button>

        {open && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg z-50">
            {searchable && (
              <div className="p-3 border-b border-gray-100">
                <input
                  ref={inputRef}
                  type="text"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setHighlightedIndex(-1);
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="Search..."
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  autoFocus
                />
              </div>
            )}

            <div className="max-h-60 overflow-y-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((option, idx) => (
                  <button
                    key={getOptionValue(option)}
                    type="button"
                    onClick={() => selectOption(option)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                    className={`w-full px-4 py-3 text-left text-sm transition-colors ${
                      highlightedIndex === idx
                        ? 'bg-orange-50 text-orange-900'
                        : value && getOptionValue(value) === getOptionValue(option)
                        ? 'bg-orange-100 text-orange-900 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{getOptionLabel(option)}</span>
                      {option.type && (
                        <span className="text-xs text-gray-500 ml-2">
                          {option.type}
                        </span>
                      )}
                    </div>
                  </button>
                ))
              ) : (
                <div className="px-4 py-8 text-center text-sm text-gray-500">
                  No results found
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Combobox;
