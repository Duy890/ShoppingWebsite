import React, { useState, useRef } from 'react';
import { Autocomplete, useJsApiLoader } from '@react-google-maps/api';

const LIBRARIES = ['places'];

/**
 * AddressAutocomplete component for checkout forms.
 * Extracts: house number, street, ward, district, province, and coordinates.
 * 
 * @param {Object} props
 * @param {Function} props.onAddressSelected - Callback returning the structured address data
 * @param {string} props.apiKey - Google Maps API Key
 */
const AddressAutocomplete = ({ onAddressSelected, apiKey }) => {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: apiKey,
    libraries: LIBRARIES,
  });

  const [autocomplete, setAutocomplete] = useState(null);
  const inputRef = useRef(null);

  const onLoad = (autocompleteInstance) => {
    setAutocomplete(autocompleteInstance);
  };

  const onPlaceChanged = () => {
    if (autocomplete !== null) {
      const place = autocomplete.getPlace();
      
      if (!place.geometry) {
        console.error("No details available for input: '" + place.name + "'");
        return;
      }

      const addressComponents = place.address_components;
      const result = {
        fullNameAddress: place.formatted_address,
        houseNumber: '',
        street: '',
        ward: '',
        district: '',
        province: '',
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
      };

      // Mapping Google Address Components to our fields
      // Common mapping for Vietnam:
      // street_number -> House number
      // route -> Street name
      // sublocality_level_1 OR administrative_area_level_3 -> Ward/Commune
      // administrative_area_level_2 -> District
      // administrative_area_level_1 -> Province/City
      
      addressComponents.forEach(component => {
        const types = component.types;
        const value = component.long_name;

        if (types.includes('street_number')) {
          result.houseNumber = value;
        }
        if (types.includes('route')) {
          result.street = value;
        }
        // In Vietnam, Ward is often sublocality_level_1 or administrative_area_level_3
        if (types.includes('sublocality_level_1') || types.includes('administrative_area_level_3')) {
          result.ward = value;
        }
        if (types.includes('administrative_area_level_2')) {
          result.district = value;
        }
        if (types.includes('administrative_area_level_1')) {
          result.province = value;
        }
      });

      if (onAddressSelected) {
        onAddressSelected(result);
      }
    }
  };

  if (loadError) {
    return <div className="text-red-500">Error loading Google Maps API</div>;
  }

  return isLoaded ? (
    <div className="w-full">
      <Autocomplete
        onLoad={onLoad}
        onPlaceChanged={onPlaceChanged}
        options={{
          fields: ['address_components', 'geometry', 'formatted_address'],
          componentRestrictions: { country: 'VN' } // Optional: restrict to Vietnam
        }}
      >
        <input
          type="text"
          placeholder="Search for your address..."
          ref={inputRef}
          className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </Autocomplete>
    </div>
  ) : (
    <div className="animate-pulse bg-gray-200 h-10 w-full rounded-md"></div>
  );
};

export default AddressAutocomplete;
