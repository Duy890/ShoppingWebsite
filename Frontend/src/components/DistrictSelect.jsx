import { useEffect, useState } from 'react';
import { locationService } from '../services/locationService';
import Combobox from './Combobox';

/**
 * District selector component
 * Dependent on province selection
 */
const DistrictSelect = ({ provinceCode, value, onChange, label = 'District' }) => {
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!provinceCode) {
      setDistricts([]);
      return;
    }

    const loadDistricts = async () => {
      setLoading(true);
      try {
        const data = await locationService.getDistricts(provinceCode);
        setDistricts(data);
      } catch (error) {
        console.error('Error loading districts:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDistricts();
  }, [provinceCode]);

  // Reset selected value when province changes
  useEffect(() => {
    if (provinceCode && value && !districts.some(d => d.code === value.code)) {
      onChange(null);
    }
  }, [provinceCode, districts]);

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
      options={districts}
      value={value}
      onChange={onChange}
      label={label}
      placeholder="Select a district..."
      disabled={!provinceCode}
      getOptionLabel={(opt) => opt.name}
      getOptionValue={(opt) => opt.code}
    />
  );
};

export default DistrictSelect;
