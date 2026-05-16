/**
 * Phone validation for Vietnam
 * Supports: 10-digit mobile numbers, landlines, etc.
 */
export const validateVietnamPhone = (phone) => {
  if (!phone) return false;
  
  // Remove spaces and common separators
  const cleaned = phone.replace(/[\s\-()]/g, '');
  
  // Check if it's a valid Vietnam phone number
  // Vietnam phone numbers: 10-11 digits, starting with valid operators
  const vietnamPhoneRegex = /^(?:\+84|0)[1-9]\d{8,10}$/;
  
  return vietnamPhoneRegex.test(cleaned);
};

/**
 * Format Vietnam phone number
 */
export const formatVietnamPhone = (phone) => {
  if (!phone) return '';
  
  const cleaned = phone.replace(/[\s\-()]/g, '');
  
  if (cleaned.startsWith('0')) {
    // Format: 0123 456 789
    return cleaned.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3');
  } else if (cleaned.startsWith('+84')) {
    // Format: +84 123 456 789
    return cleaned.replace(/(\+\d{2})(\d{2})(\d{3})(\d{4})/, '$1 $2 $3 $4');
  }
  
  return cleaned;
};

/**
 * Format address for display
 */
export const formatAddress = (address) => {
  if (!address) return '';
  
  const parts = [
    address.street,
    address.ward,
    address.district,
    address.province,
    address.country,
  ].filter(Boolean);
  
  return parts.join(', ');
};

/**
 * Validate address form data
 */
export const validateAddressForm = (formData) => {
  const errors = {};
  
  if (!formData.full_name?.trim()) {
    errors.full_name = 'Full name is required';
  }
  
  if (!formData.phone?.trim()) {
    errors.phone = 'Phone number is required';
  } else if (!validateVietnamPhone(formData.phone)) {
    errors.phone = 'Invalid Vietnam phone number';
  }
  
  if (!formData.street?.trim()) {
    errors.street = 'Street address is required';
  }
  
  if (!formData.province?.code) {
    errors.province = 'Province/City is required';
  }
  
  if (!formData.district?.code) {
    errors.district = 'District is required';
  }
  
  if (!formData.ward?.code) {
    errors.ward = 'Ward is required';
  }
  
  return errors;
};
