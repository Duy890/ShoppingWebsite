import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { MapPin, Home, Phone, User, Loader2 } from 'lucide-react';

const API_BASE_URL = 'https://provinces.open-api.vn/api';

const AddressSelectionForm = ({ onSubmitAddress }) => {
  const { register, handleSubmit, watch, setValue, formState: { errors, isValid } } = useForm({
    mode: 'onChange',
    defaultValues: {
      fullName: '',
      phoneNumber: '',
      province: '',
      district: '',
      ward: '',
      streetAddress: ''
    }
  });

  const [provinces, setProvinces] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [wards, setWards] = useState([]);
  const [loading, setLoading] = useState({ p: false, d: false, w: false });

  // Watch values for cascading logic
  const selectedProvinceCode = watch('province');
  const selectedDistrictCode = watch('district');

  // 1. Fetch Provinces
  useEffect(() => {
    const fetchProvinces = async () => {
      setLoading(prev => ({ ...prev, p: true }));
      try {
        const res = await axios.get(`${API_BASE_URL}/p/`);
        setProvinces(res.data);
      } catch (err) {
        console.error("Error fetching provinces", err);
      } finally {
        setLoading(prev => ({ ...prev, p: false }));
      }
    };
    fetchProvinces();
  }, []);

  // 2. Fetch Districts when Province changes
  useEffect(() => {
    if (selectedProvinceCode) {
      const fetchDistricts = async () => {
        setLoading(prev => ({ ...prev, d: true }));
        try {
          const res = await axios.get(`${API_BASE_URL}/p/${selectedProvinceCode}?depth=2`);
          setDistricts(res.data.districts);
          // Reset children
          setValue('district', '');
          setValue('ward', '');
          setWards([]);
        } catch (err) {
          console.error("Error fetching districts", err);
        } finally {
          setLoading(prev => ({ ...prev, d: false }));
        }
      };
      fetchDistricts();
    }
  }, [selectedProvinceCode, setValue]);

  // 3. Fetch Wards when District changes
  useEffect(() => {
    if (selectedDistrictCode) {
      const fetchWards = async () => {
        setLoading(prev => ({ ...prev, w: true }));
        try {
          const res = await axios.get(`${API_BASE_URL}/d/${selectedDistrictCode}?depth=2`);
          setWards(res.data.wards);
          setValue('ward', '');
        } catch (err) {
          console.error("Error fetching wards", err);
        } finally {
          setLoading(prev => ({ ...prev, w: false }));
        }
      };
      fetchWards();
    }
  }, [selectedDistrictCode, setValue]);

  const onInternalSubmit = (data) => {
    // Find names to match your FastAPI backend requirement
    const p = provinces.find(i => i.code == data.province);
    const d = districts.find(i => i.code == data.district);
    const w = wards.find(i => i.code == data.ward);

    const finalData = {
      full_name: data.fullName,
      phone_number: data.phoneNumber,
      province_name: p?.name,
      province_code: p?.code,
      district_name: d?.name,
      district_code: d?.code,
      ward_name: w?.name,
      ward_code: w?.code,
      street_address: data.streetAddress,
      formatted_address: `${data.streetAddress}, ${w?.name}, ${d?.name}, ${p?.name}`
    };

    onSubmitAddress(finalData);
  };

  const inputClasses = (error) => `
    w-full bg-white border ${error ? 'border-red-500' : 'border-gray-200'} 
    px-4 py-3 rounded-xl text-sm font-semibold text-gray-700 
    focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary 
    transition-all disabled:bg-gray-50 disabled:cursor-not-allowed
  `;

  return (
    <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 max-w-2xl mx-auto">
      <div className="flex items-center space-x-3 mb-8">
        <div className="bg-primary/10 p-3 rounded-2xl text-primary">
          <MapPin className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-black text-gray-900 tracking-tight uppercase">Shipping Destination</h2>
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Premium Delivery Service</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onInternalSubmit)} className="space-y-6">
        {/* Contact Info Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1 flex items-center">
              <User className="w-3 h-3 mr-1" /> Recipient Name
            </label>
            <input
              {...register('fullName', { required: 'Name is required' })}
              placeholder="John Doe"
              className={inputClasses(errors.fullName)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1 flex items-center">
              <Phone className="w-3 h-3 mr-1" /> Phone Number
            </label>
            <input
              {...register('phoneNumber', { 
                required: 'Phone is required',
                pattern: { value: /^[0-9]{10,11}$/, message: 'Invalid phone format' }
              })}
              placeholder="0901234567"
              className={inputClasses(errors.phoneNumber)}
            />
          </div>
        </div>

        {/* Administrative Dropdowns */}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Province / City</label>
            <div className="relative">
              <select
                {...register('province', { required: true })}
                className={inputClasses(errors.province)}
              >
                <option value="">Select Province</option>
                {provinces.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
              </select>
              {loading.p && <Loader2 className="absolute right-4 top-3 w-5 h-5 animate-spin text-primary" />}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">District</label>
              <div className="relative">
                <select
                  {...register('district', { required: true })}
                  disabled={!selectedProvinceCode}
                  className={inputClasses(errors.district)}
                >
                  <option value="">Select District</option>
                  {districts.map(d => <option key={d.code} value={d.code}>{d.name}</option>)}
                </select>
                {loading.d && <Loader2 className="absolute right-4 top-3 w-5 h-5 animate-spin text-primary" />}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Ward / Commune</label>
              <div className="relative">
                <select
                  {...register('ward', { required: true })}
                  disabled={!selectedDistrictCode}
                  className={inputClasses(errors.ward)}
                >
                  <option value="">Select Ward</option>
                  {wards.map(w => <option key={w.code} value={w.code}>{w.name}</option>)}
                </select>
                {loading.w && <Loader2 className="absolute right-4 top-3 w-5 h-5 animate-spin text-primary" />}
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Address */}
        <div className="space-y-2">
          <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1 flex items-center">
            <Home className="w-3 h-3 mr-1" /> Detailed Address
          </label>
          <textarea
            {...register('streetAddress', { required: 'Detail address is required' })}
            placeholder="House number, Street name, Building..."
            rows={3}
            className={inputClasses(errors.streetAddress)}
          />
        </div>

        <button
          type="submit"
          disabled={!isValid}
          className="w-full bg-gray-900 text-white py-5 rounded-2xl text-sm font-black uppercase tracking-widest hover:bg-primary transition-all duration-300 disabled:bg-gray-100 disabled:text-gray-400 shadow-xl shadow-gray-900/10"
        >
          Confirm Shipping Address
        </button>
      </form>
    </div>
  );
};

export default AddressSelectionForm;
