import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://provinces.open-api.vn/api';

const ManualAddressForm = ({ onAddressChange, initialData = {} }) => {
  const [provinces, setProvinces] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [wards, setWards] = useState([]);

  const [selectedProvince, setSelectedProvince] = useState(initialData.provinceCode || '');
  const [selectedDistrict, setSelectedDistrict] = useState(initialData.districtCode || '');
  const [selectedWard, setSelectedWard] = useState(initialData.wardCode || '');

  const [formData, setFormData] = useState({
    fullName: initialData.fullName || '',
    phoneNumber: initialData.phoneNumber || '',
    province: initialData.province || '',
    district: initialData.district || '',
    ward: initialData.ward || '',
    streetAddress: initialData.streetAddress || '',
    addressType: 'manual'
  });

  // 1. Fetch Provinces on mount
  useEffect(() => {
    const fetchProvinces = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/p/`);
        setProvinces(response.data);
      } catch (error) {
        console.error("Error fetching provinces:", error);
      }
    };
    fetchProvinces();
  }, []);

  // 2. Fetch Districts when Province changes
  useEffect(() => {
    if (selectedProvince) {
      const fetchDistricts = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/p/${selectedProvince}?depth=2`);
          setDistricts(response.data.districts);
          setWards([]); // Reset wards when province changes
          setSelectedDistrict('');
          setSelectedWard('');
        } catch (error) {
          console.error("Error fetching districts:", error);
        }
      };
      fetchDistricts();
    } else {
      setDistricts([]);
      setWards([]);
    }
  }, [selectedProvince]);

  // 3. Fetch Wards when District changes
  useEffect(() => {
    if (selectedDistrict) {
      const fetchWards = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/d/${selectedDistrict}?depth=2`);
          setWards(response.data.wards);
          setSelectedWard('');
        } catch (error) {
          console.error("Error fetching wards:", error);
        }
      };
      fetchWards();
    } else {
      setWards([]);
    }
  }, [selectedDistrict]);

  // Handle simple input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const newFormData = { ...formData, [name]: value };
    setFormData(newFormData);
    onAddressChange?.(newFormData);
  };

  // Handle Dropdown Selection
  const handleProvinceSelect = (e) => {
    const code = e.target.value;
    const name = provinces.find(p => p.code === parseInt(code))?.name || '';
    setSelectedProvince(code);
    
    const newFormData = { ...formData, province: name, district: '', ward: '' };
    setFormData(newFormData);
    onAddressChange?.(newFormData);
  };

  const handleDistrictSelect = (e) => {
    const code = e.target.value;
    const name = districts.find(d => d.code === parseInt(code))?.name || '';
    setSelectedDistrict(code);
    
    const newFormData = { ...formData, district: name, ward: '' };
    setFormData(newFormData);
    onAddressChange?.(newFormData);
  };

  const handleWardSelect = (e) => {
    const code = e.target.value;
    const name = wards.find(w => w.code === parseInt(code))?.name || '';
    setSelectedWard(code);
    
    const newFormData = { ...formData, ward: name };
    setFormData(newFormData);
    onAddressChange?.(newFormData);
  };

  return (
    <div className="space-y-4 bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Manual Address Entry</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input
            type="text"
            name="fullName"
            value={formData.fullName}
            onChange={handleInputChange}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            placeholder="John Doe"
          />
        </div>

        {/* Phone Number */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input
            type="tel"
            name="phoneNumber"
            value={formData.phoneNumber}
            onChange={handleInputChange}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            placeholder="0123 456 789"
          />
        </div>
      </div>

      {/* Province Dropdown */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Province / City</label>
        <select
          value={selectedProvince}
          onChange={handleProvinceSelect}
          className="w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
        >
          <option value="">Select Province</option>
          {provinces.map((p) => (
            <option key={p.code} value={p.code}>{p.name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* District Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">District</label>
          <select
            value={selectedDistrict}
            onChange={handleDistrictSelect}
            disabled={!selectedProvince}
            className={`w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all ${!selectedProvince ? 'bg-gray-50 cursor-not-allowed' : ''}`}
          >
            <option value="">Select District</option>
            {districts.map((d) => (
              <option key={d.code} value={d.code}>{d.name}</option>
            ))}
          </select>
        </div>

        {/* Ward Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ward / Commune</label>
          <select
            value={selectedWard}
            onChange={handleWardSelect}
            disabled={!selectedDistrict}
            className={`w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all ${!selectedDistrict ? 'bg-gray-50 cursor-not-allowed' : ''}`}
          >
            <option value="">Select Ward</option>
            {wards.map((w) => (
              <option key={w.code} value={w.code}>{w.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Street Address */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Street Address</label>
        <textarea
          name="streetAddress"
          rows="2"
          value={formData.streetAddress}
          onChange={handleInputChange}
          className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          placeholder="Building name, Floor, House number, Street name..."
        ></textarea>
      </div>
    </div>
  );
};

export default ManualAddressForm;
