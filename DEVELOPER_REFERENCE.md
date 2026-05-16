# Quick Developer Reference - Address Management System

## Component Usage Examples

### 1. Using AddressSelector in Checkout

```jsx
import AddressSelector from '../components/AddressSelector';

function CheckoutPage() {
  const [selectedAddress, setSelectedAddress] = useState(null);

  return (
    <div>
      <AddressSelector 
        selectedAddressId={selectedAddress?.id}
        onAddressSelect={(address) => setSelectedAddress(address)}
      />
    </div>
  );
}
```

### 2. Using ProvinceSelect in Address Form

```jsx
import ProvinceSelect from '../components/ProvinceSelect';
import DistrictSelect from '../components/DistrictSelect';
import WardSelect from '../components/WardSelect';

function AddressForm() {
  const [province, setProvince] = useState(null);
  const [district, setDistrict] = useState(null);
  const [ward, setWard] = useState(null);

  return (
    <div className="grid grid-cols-3 gap-4">
      <ProvinceSelect 
        value={province}
        onChange={setProvince}
        label="Province/City"
      />
      <DistrictSelect
        provinceCode={province?.code}
        value={district}
        onChange={setDistrict}
        label="District"
      />
      <WardSelect
        districtCode={district?.code}
        value={ward}
        onChange={setWard}
        label="Ward"
      />
    </div>
  );
}
```

### 3. Using Combobox Directly

```jsx
import Combobox from '../components/Combobox';

function CustomSelector() {
  const [selected, setSelected] = useState(null);
  const options = [
    { code: '1', name: 'Option 1' },
    { code: '2', name: 'Option 2' },
  ];

  return (
    <Combobox
      options={options}
      value={selected}
      onChange={setSelected}
      label="Select an option"
      placeholder="Choose..."
      getOptionLabel={(opt) => opt.name}
      getOptionValue={(opt) => opt.code}
    />
  );
}
```

### 4. Using AddressFormModal

```jsx
import AddressFormModal from '../components/AddressFormModal';

function ProfilePage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);

  const handleSubmit = async (formData) => {
    if (editingAddress) {
      await addressService.updateAddress(editingAddress.id, formData);
    } else {
      await addressService.createAddress(formData);
    }
    setModalOpen(false);
  };

  return (
    <>
      <button onClick={() => setModalOpen(true)}>Add Address</button>
      
      <AddressFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingAddress(null);
        }}
        onSubmit={handleSubmit}
        initialData={editingAddress}
        title={editingAddress ? 'Edit Address' : 'Add Address'}
      />
    </>
  );
}
```

### 5. Using AddressCard with Actions

```jsx
import AddressCard from '../components/AddressCard';

function AddressList({ addresses }) {
  return (
    <div className="space-y-3">
      {addresses.map(address => (
        <AddressCard
          key={address.id}
          address={address}
          selected={selectedId === address.id}
          onSelect={() => handleSelect(address)}
          onEdit={() => handleEdit(address)}
          onDelete={() => handleDelete(address.id)}
          onSetDefault={() => handleSetDefault(address.id)}
        />
      ))}
    </div>
  );
}
```

---

## Validation Utilities

```jsx
import {
  validateVietnamPhone,
  formatVietnamPhone,
  formatAddress,
  validateAddressForm,
} from '../utils/addressValidation';

// Phone validation
const isValid = validateVietnamPhone('0912345678'); // true

// Phone formatting
const formatted = formatVietnamPhone('0912345678'); // "0912 345 678"

// Address formatting
const fullAddress = formatAddress({
  street: '123 Main St',
  ward: 'Hàng Bạc',
  district: 'Hoàn Kiếm',
  province: 'Hà Nội',
  country: 'Vietnam',
}); // "123 Main St, Hàng Bạc, Hoàn Kiếm, Hà Nội, Vietnam"

// Form validation
const errors = validateAddressForm(formData);
if (Object.keys(errors).length > 0) {
  // Show errors
}
```

---

## Location Service

```jsx
import { locationService } from '../services/locationService';

// Get all provinces
const provinces = await locationService.getProvinces();
// [{ code: '01', name: 'Hà Nội', type: 'Thành phố' }, ...]

// Get districts by province
const districts = await locationService.getDistricts('01');
// [{ code: '001', name: 'Hoàn Kiếm', type: 'Quận' }, ...]

// Get wards by district
const wards = await locationService.getWards('001');
// [{ code: '00101', name: 'Hàng Bạc', type: 'Phường' }, ...]

// Search
const results = await locationService.searchLocation('Hoàn', 'province');
// { provinces: [...], districts: [...], wards: [...] }
```

---

## API Endpoints

### Location Endpoints

```bash
# Get all provinces
GET /api/locations/provinces
# Response: { data: [...] }

# Get districts for a province
GET /api/locations/districts/01
# Response: { data: [...] }

# Get wards for a district
GET /api/locations/wards/001
# Response: { data: [...] }

# Search locations
GET /api/locations/search?q=Hoàn&type=all
# Response: { data: { provinces: [...], districts: [...], wards: [...] } }
```

### Address Endpoints (Existing)

```bash
# Get user's addresses
GET /addresses
# Response: [{ id, user_id, full_name, phone, street, province, district, ward, country, is_default, created_at }]

# Create address
POST /addresses
# Body: { full_name, phone, street, province, district, ward, country, is_default }

# Update address
PUT /addresses/{id}
# Body: { full_name?, phone?, street?, province?, district?, ward?, country?, is_default? }

# Delete address
DELETE /addresses/{id}

# Set default
PATCH /addresses/{id}/set-default
```

---

## Component Props Reference

### ProvinceSelect
```jsx
<ProvinceSelect
  value={null}                    // Selected province object
  onChange={(province) => {}}     // Callback on selection
  label="Province/City"           // Field label
/>
```

### DistrictSelect
```jsx
<DistrictSelect
  provinceCode="01"               // Required: Province code
  value={null}                    // Selected district object
  onChange={(district) => {}}     // Callback on selection
  label="District"                // Field label
/>
```

### WardSelect
```jsx
<WardSelect
  districtCode="001"              // Required: District code
  value={null}                    // Selected ward object
  onChange={(ward) => {}}         // Callback on selection
  label="Ward"                    // Field label
/>
```

### Combobox
```jsx
<Combobox
  options={[]}                    // Array of options
  value={null}                    // Selected option
  onChange={(opt) => {}}          // Selection callback
  label="Label"                   // Field label
  placeholder="Select..."         // Placeholder text
  disabled={false}                // Disable dropdown
  searchable={true}               // Show search input
  getOptionLabel={(opt) => opt.name}        // Display text function
  getOptionValue={(opt) => opt.code}        // Value function
/>
```

### AddressFormModal
```jsx
<AddressFormModal
  open={true}                     // Modal visibility
  onClose={() => {}}              // Close callback
  onSubmit={(data) => {}}         // Form submit callback
  initialData={null}              // Initial values for edit mode
  title="Add Address"             // Modal title
  submitLabel="Save Address"      // Submit button text
/>
```

### AddressSelector
```jsx
<AddressSelector
  selectedAddressId="uuid"        // Current selected address ID
  onAddressSelect={(addr) => {}}  // Selection callback
/>
```

### AddressCard
```jsx
<AddressCard
  address={addressObj}            // Address data
  selected={false}                // Is selected
  onSelect={() => {}}             // Click callback
  onEdit={() => {}}               // Edit action
  onDelete={() => {}}             // Delete action
  onSetDefault={() => {}}         // Set default action
  loading={false}                 // Loading state
/>
```

---

## Data Structures

### Province Object
```js
{
  code: "01",
  name: "Hà Nội",
  type: "Thành phố"
}
```

### District Object
```js
{
  code: "001",
  name: "Hoàn Kiếm",
  type: "Quận"
}
```

### Ward Object
```js
{
  code: "00101",
  name: "Hàng Bạc",
  type: "Phường"
}
```

### Address Object
```js
{
  id: "uuid",
  user_id: "uuid",
  full_name: "John Doe",
  phone: "0912345678",
  street: "123 Main Street",
  province: "Hà Nội",
  district: "Hoàn Kiếm",
  ward: "Hàng Bạc",
  country: "Vietnam",
  is_default: true,
  created_at: "2026-05-15T..."
}
```

### Form Data Structure
```js
{
  full_name: "John Doe",
  phone: "0912345678",
  street: "123 Main Street",
  province: { code: "01", name: "Hà Nội", type: "Thành phố" },
  district: { code: "001", name: "Hoàn Kiếm", type: "Quận" },
  ward: { code: "00101", name: "Hàng Bạc", type: "Phường" },
  country: "Vietnam",
  is_default: false
}
```

---

## Common Patterns

### Add/Edit Address Pattern
```jsx
const [editingAddress, setEditingAddress] = useState(null);
const [modalOpen, setModalOpen] = useState(false);

const handleSubmit = async (formData) => {
  try {
    if (editingAddress) {
      await addressService.updateAddress(editingAddress.id, formData);
      // Reload or update state
    } else {
      await addressService.createAddress(formData);
      // Reload or update state
    }
    setModalOpen(false);
    setEditingAddress(null);
  } catch (error) {
    alert(error.message);
  }
};

// Usage
<button onClick={() => { setEditingAddress(null); setModalOpen(true); }}>
  Add
</button>

<button onClick={() => { setEditingAddress(addr); setModalOpen(true); }}>
  Edit
</button>

<AddressFormModal 
  open={modalOpen}
  initialData={editingAddress}
  onSubmit={handleSubmit}
/>
```

### Default Address Pattern
```jsx
const handleSetDefault = async (addressId) => {
  try {
    await addressService.setDefaultAddress(addressId);
    setAddresses(prev =>
      prev.map(addr =>
        addr.id === addressId
          ? { ...addr, is_default: true }
          : { ...addr, is_default: false }
      )
    );
  } catch (error) {
    alert(error.message);
  }
};
```

### Hierarchical Selection Pattern
```jsx
const [province, setProvince] = useState(null);
const [district, setDistrict] = useState(null);
const [ward, setWard] = useState(null);

// When province changes
const handleProvinceChange = (prov) => {
  setProvince(prov);
  setDistrict(null);  // Reset dependent fields
  setWard(null);
};

// When district changes
const handleDistrictChange = (dist) => {
  setDistrict(dist);
  setWard(null);  // Reset dependent field
};
```

---

## Error Handling

```jsx
import { validateAddressForm } from '../utils/addressValidation';

const handleSubmit = (e) => {
  e.preventDefault();
  
  // Validate
  const errors = validateAddressForm(form);
  if (Object.keys(errors).length > 0) {
    setErrors(errors);
    return;
  }
  
  // Submit
  try {
    await addressService.createAddress(form);
  } catch (error) {
    if (error.response?.status === 400) {
      alert('Invalid address data');
    } else {
      alert('Failed to save address');
    }
  }
};
```

---

## Debugging Tips

1. **Check Location Data**
   - Verify JSON files exist
   - Test endpoints directly: `curl http://localhost:8000/api/locations/provinces`

2. **Dropdown Not Appearing**
   - Check console for errors
   - Verify province/district selection for dependent dropdowns
   - Check z-index if dropdown is hidden behind other elements

3. **Phone Validation Issues**
   - Format: `0912345678` (no spaces)
   - Check regex: `^(?:\+84|0)[1-9]\d{8,10}$`

4. **Address Not Saving**
   - Verify all required fields
   - Check hierarchical selection (province → district → ward)
   - Check network tab for API errors

5. **Performance Optimization**
   - Location data is cached on component mount
   - Use React.memo for AddressCard in lists
   - Debounce search input if adding search feature

---

## Best Practices

✅ **DO**:
- Validate form before submission
- Show loading states during async operations
- Handle errors gracefully with user feedback
- Reset form on successful submission
- Use Address Card's built-in actions menu
- Hierarchically depend selectors (province → district → ward)
- Default select first province on load for UX

❌ **DON'T**:
- Force user to enter location manually
- Skip phone validation
- Make all fields optional
- Show dropdowns while loading
- Mix old TextInput and new Combobox for locations
- Require page reload after address operations

---

For more details, see `ADDRESS_MANAGEMENT_IMPLEMENTATION.md`
