import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useForm } from 'react-hook-form';
import { MapPin, ChevronDown, Loader2 } from 'lucide-react';

const API_BASE_URL = 'https://provinces.open-api.vn/api';

const ManualAddressSelector = ({ onSubmitAddress }) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      province: '',
      district: '',
      ward: '',
      streetAddress: '',
      fullName: '',
      phoneNumber: ''
    }
  });

  const [provinces, setProvinces] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [wards, setWards] = useState([]);
  const [loading, setLoading] = useState({ p: false, d: false, w: false });

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
        console.error("Failed to fetch provinces", err);
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
          console.error("Failed to fetch districts", err);
        } finally {
          setLoading(prev => ({ ...prev, d: false }));
        }
      };
      fetchDistricts();
    } else {
      setDistricts([]);
      setWards([]);
      setValue('district', '');
      setValue('ward', '');
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
          console.error("Failed to fetch wards", err);
        } finally {
          setLoading(prev => ({ ...prev, w: false }));
        }
      };
      fetchWards();
    } else {
      setWards([]);
      setValue('ward', '');
    }
  }, [selectedDistrictCode, setValue]);

  const onFormSubmit = (data) => {
    const provinceObj = provinces.find(p => p.code === parseInt(data.province));
    const districtObj = districts.find(d => d.code === parseInt(data.district));
    const wardObj = wards.find(w => w.code === parseInt(data.ward));

    const finalData = {
      full_name: data.fullName,
      phone_number: data.phoneNumber,
      province_name: provinceObj?.name,
      province_code: provinceObj?.code,
      district_name: districtObj?.name,
      district_code: districtObj?.code,
      ward_name: wardObj?.name,
      ward_code: wardObj?.code,
      street_address: data.streetAddress,
      formatted_address: `${data.streetAddress}, ${wardObj?.name}, ${districtObj?.name}, ${provinceObj?.name}`
    };

    onSubmitAddress(finalData);
  };

  const selectStyles = "w-full appearance-none bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 shadow-sm";
  const labelStyles = "block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1";

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6 max-w-2xl bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-blue-50 rounded-xl text-blue-600">
          <MapPin size={22} />
        </div>
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight">Shipping Address</h2>
          <p className="text-xs font-medium text-slate-400">Enter your delivery details below</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className={labelStyles}>Full Name</label>
          <input
            {...register('fullName', { required: 'Name is required' })}
            placeholder="e.g. Nguyen Van A"
            className={selectStyles}
          />
          {errors.fullName && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.fullName.message}</p>}
        </div>

        <div>
          <label className={labelStyles}>Phone Number</label>
          <input
            {...register('phoneNumber', { 
              required: 'Phone is required',
              pattern: { value: /^[0-9]{10}$/, message: 'Invalid phone number (10 digits)' }
            })}
            placeholder="0987xxxxxx"
            className={selectStyles}
          />
          {errors.phoneNumber && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.phoneNumber.message}</p>}
        </div>
      </div>

      <div className="space-y-5">
        {/* Province */}
        <div className="relative">
          <label className={labelStyles}>Province / City</label>
          <div className="relative">
            <select
              {...register('province', { required: 'Please select a province' })}
              className={selectStyles}
              disabled={loading.p}
            >
              <option value="">Select Province</option>
              {provinces.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
              {loading.p ? <Loader2 className="animate-spin" size={18} /> : <ChevronDown size={18} />}
            </div>
          </div>
          {errors.province && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.province.message}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* District */}
          <div className="relative">
            <label className={labelStyles}>District</label>
            <div className="relative">
              <select
                {...register('district', { required: 'Please select a district' })}
                className={`${selectStyles} ${!selectedProvinceCode ? 'bg-slate-50 cursor-not-allowed opacity-60' : ''}`}
                disabled={!selectedProvinceCode || loading.d}
              >
                <option value="">Select District</option>
                {districts.map(d => <option key={d.code} value={d.code}>{d.name}</option>)}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                {loading.d ? <Loader2 className="animate-spin" size={18} /> : <ChevronDown size={18} />}
              </div>
            </div>
            {errors.district && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.district.message}</p>}
          </div>

          {/* Ward */}
          <div className="relative">
            <label className={labelStyles}>Ward / Commune</label>
            <div className="relative">
              <select
                {...register('ward', { required: 'Please select a ward' })}
                className={`${selectStyles} ${!selectedDistrictCode ? 'bg-slate-50 cursor-not-allowed opacity-60' : ''}`}
                disabled={!selectedDistrictCode || loading.w}
              >
                <option value="">Select Ward</option>
                {wards.map(w => <option key={w.code} value={w.code}>{w.name}</option>)}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                {loading.w ? <Loader2 className="animate-spin" size={18} /> : <ChevronDown size={18} />}
              </div>
            </div>
            {errors.ward && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.ward.message}</p>}
          </div>
        </div>

        {/* Detailed Address */}
        <div>
          <label className={labelStyles}>Detailed Address</label>
          <textarea
            {...register('streetAddress', { required: 'Please enter your street address' })}
            placeholder="House number, street name, building, floor..."
            rows={3}
            className={`${selectStyles} resize-none`}
          />
          {errors.streetAddress && <p className="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-tight ml-1">{errors.streetAddress.message}</p>}
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-slate-900 hover:bg-blue-600 text-white font-black uppercase tracking-widest py-5 rounded-2xl transition-all duration-300 shadow-xl shadow-slate-200 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
      >
        {isSubmitting && <Loader2 className="animate-spin" size={20} />}
        Confirm Delivery Address
      </button>
    </form>
  );
};

export default ManualAddressSelector;
