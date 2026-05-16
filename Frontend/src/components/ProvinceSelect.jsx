import { useEffect, useState } from 'react';
import { locationService } from '../services/locationService';
import Combobox from './Combobox';

/**
 * Province/City selector component
 */
const ProvinceSelect = ({ value, onChange, label = 'Province/City' }) => {
  const [provinces, setProvinces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProvinces = async () => {
      try {
        const data = await locationService.getProvinces();
        setProvinces(data);
      } catch (error) {
        console.error('Error loading provinces:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProvinces();
  }, []);

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
      options={provinces}
      value={value}
      onChange={onChange}
      label={label}
      placeholder="Select a province or city..."
      getOptionLabel={(opt) => opt.name}
      getOptionValue={(opt) => opt.code}
    />
  );
};

export default ProvinceSelect;
