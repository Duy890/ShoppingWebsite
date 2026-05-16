import { useEffect, useState } from 'react';
import { X, AlertCircle } from 'lucide-react';
import ProvinceSelect from './ProvinceSelect';
import DistrictSelect from './DistrictSelect';
import WardSelect from './WardSelect';
import { validateAddressForm, validateVietnamPhone } from '../utils/addressValidation';

/**
 * Enhanced address form modal with hierarchical location selectors
 */
const AddressFormModal = ({ 
  open, 
  onClose, 
  onSubmit, 
  initialData = null,
  title = 'Add Address',
  submitLabel = 'Save Address',
}) => {
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    street: '',
    province: null,
    district: null,
    ward: null,
    country: 'Vietnam',
    is_default: false,
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setForm({
        full_name: initialData.full_name || '',
        phone: initialData.phone || '',
        street: initialData.street || '',
        province: initialData.province_obj || null,
        district: initialData.district_obj || null,
        ward: initialData.ward_obj || null,
        country: initialData.country || 'Vietnam',
        is_default: initialData.is_default || false,
      });
    } else {
      setForm({
        full_name: '',
        phone: '',
        street: '',
        province: null,
        district: null,
        ward: null,
        country: 'Vietnam',
        is_default: false,
      });
    }
    setErrors({});
  }, [open, initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleProvinceChange = (province) => {
    setForm(prev => ({
      ...prev,
      province,
      district: null,
      ward: null,
    }));
    if (errors.province) {
      setErrors(prev => ({ ...prev, province: '' }));
    }
  };

  const handleDistrictChange = (district) => {
    setForm(prev => ({
      ...prev,
      district,
      ward: null,
    }));
    if (errors.district) {
      setErrors(prev => ({ ...prev, district: '' }));
    }
  };

  const handleWardChange = (ward) => {
    setForm(prev => ({ ...prev, ward }));
    if (errors.ward) {
      setErrors(prev => ({ ...prev, ward: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    const newErrors = validateAddressForm(form);
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setSubmitting(true);
    try {
      // Format data for API
      const addressData = {
        full_name: form.full_name.trim(),
        phone: form.phone.replace(/[\s\-()]/g, ''),
        street: form.street.trim(),
        province: form.province.name,
        district: form.district.name,
        ward: form.ward.name,
        country: form.country,
        is_default: form.is_default,
      };

      await onSubmit(addressData);
      
      // Reset form on success
      setForm({
        full_name: '',
        phone: '',
        street: '',
        province: null,
        district: null,
        ward: null,
        country: 'Vietnam',
        is_default: false,
      });
    } catch (error) {
      console.error('Error submitting address form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl ring-1 ring-black/5 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">Complete address details</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
            aria-label="Close modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Full Name & Phone */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                placeholder="Enter your full name"
                className={`w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2 transition ${
                  errors.full_name
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-200 focus:ring-orange-500 focus:border-transparent'
                }`}
              />
              {errors.full_name && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.full_name}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={handleChange}
                placeholder="0912 345 678"
                className={`w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2 transition ${
                  errors.phone
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-200 focus:ring-orange-500 focus:border-transparent'
                }`}
              />
              {errors.phone && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.phone}
                </p>
              )}
            </div>
          </div>

          {/* Location Selectors */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <ProvinceSelect 
                value={form.province}
                onChange={handleProvinceChange}
                label={<span>Province/City <span className="text-red-500">*</span></span>}
              />
              {errors.province && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.province}
                </p>
              )}
            </div>

            <div>
              <DistrictSelect
                provinceCode={form.province?.code}
                value={form.district}
                onChange={handleDistrictChange}
                label={<span>District <span className="text-red-500">*</span></span>}
              />
              {errors.district && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.district}
                </p>
              )}
            </div>

            <div>
              <WardSelect
                districtCode={form.district?.code}
                value={form.ward}
                onChange={handleWardChange}
                label={<span>Ward <span className="text-red-500">*</span></span>}
              />
              {errors.ward && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.ward}
                </p>
              )}
            </div>
          </div>

          {/* Street Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Street Address <span className="text-red-500">*</span>
            </label>
            <textarea
              name="street"
              value={form.street}
              onChange={handleChange}
              placeholder="Enter house number, street name, etc."
              rows="3"
              className={`w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2 transition resize-none ${
                errors.street
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-gray-200 focus:ring-orange-500 focus:border-transparent'
              }`}
            />
            {errors.street && (
              <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.street}
              </p>
            )}
          </div>

          {/* Default Address Checkbox */}
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name="is_default"
              checked={form.is_default}
              onChange={handleChange}
              className="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
            />
            <span className="text-sm text-gray-700">Set as default address</span>
          </label>

          {/* Form Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 text-gray-700 font-medium hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-4 py-3 rounded-xl bg-orange-500 text-white font-medium hover:bg-orange-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Saving...' : submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddressFormModal;
