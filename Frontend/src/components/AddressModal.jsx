import { useEffect, useState } from 'react';

const initialState = {
  full_name: '',
  phone: '',
  street: '',
  district: '',
  city: '',
  country: '',
};

const AddressModal = ({ open, onClose, onSubmit }) => {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (open) {
      setForm(initialState);
    }
  }, [open]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl ring-1 ring-black/5">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-gray-900">Add Address</h3>
            <p className="text-sm text-gray-500">Enter the address details and save.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium text-gray-700">
              Full Name
              <input
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                required
                className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              Phone
              <input
                name="phone"
                value={form.phone}
                onChange={handleChange}
                required
                className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
          </div>

          <label className="block text-sm font-medium text-gray-700">
            Street
            <input
              name="street"
              value={form.street}
              onChange={handleChange}
              required
              className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium text-gray-700">
              District
              <input
                name="district"
                value={form.district}
                onChange={handleChange}
                className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              City
              <input
                name="city"
                value={form.city}
                onChange={handleChange}
                required
                className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
          </div>

          <label className="block text-sm font-medium text-gray-700">
            Country
            <input
              name="country"
              value={form.country}
              onChange={handleChange}
              required
              className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </label>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-2xl border border-gray-200 bg-gray-50 px-5 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-orange-600"
            >
              Save Address
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddressModal;
