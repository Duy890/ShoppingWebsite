import { useEffect, useState } from 'react';
import { locationService } from '../services/locationService';
import Combobox from './Combobox';

/**
 * Ward selector component
 * Dependent on district selection
 */
const WardSelect = ({ districtCode, value, onChange, label = 'Ward' }) => {
  const [wards, setWards] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!districtCode) {
      setWards([]);
      return;
    }

    const loadWards = async () => {
      setLoading(true);
      try {
        const data = await locationService.getWards(districtCode);
        setWards(data);
      } catch (error) {
        console.error('Error loading wards:', error);
      } finally {
        setLoading(false);
      }
    };

    loadWards();
  }, [districtCode]);

  // Reset selected value when district changes
  useEffect(() => {
    if (districtCode && value && !wards.some(w => w.code === value.code)) {
      onChange(null);
    }
  }, [districtCode, wards]);

  if (loading) {
    return (
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
        <div className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 animate-pulse" />
      </div>
    );
  }

  return (
    <Combobox
      options={wards}
      value={value}
      onChange={onChange}
      label={label}
      placeholder="Select a ward..."
      disabled={!districtCode}
      getOptionLabel={(opt) => opt.name}
      getOptionValue={(opt) => opt.code}
    />
  );
};

export default WardSelect;
