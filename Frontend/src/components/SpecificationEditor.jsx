import { useEffect, useMemo, useRef } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import ProductSpecifications from './ProductSpecifications';
import { productService } from '../services/productService';

const productTypeOptions = [
  { value: '', label: 'Custom' },
  { value: 'phone', label: 'Phone' },
  { value: 'laptop', label: 'Laptop' },
  { value: 'audio', label: 'Audio / Headphone' },
  { value: 'watch', label: 'Smartwatch' },
  { value: 'tablet', label: 'Tablet' },
  { value: 'accessory', label: 'Accessory' },
];

const makeRow = (overrides = {}) => ({
  local_id: crypto.randomUUID(),
  group_name: '',
  spec_key: '',
  spec_value: '',
  display_order: 0,
  ...overrides,
});

const groupRows = (rows) =>
  rows.reduce((acc, row) => {
    const groupName = row.group_name || 'Thông số khác';
    if (!acc[groupName]) acc[groupName] = [];
    acc[groupName].push(row);
    return acc;
  }, {});

const SpecificationEditor = ({ productType, onProductTypeChange, specifications, onChange }) => {
  const loadedTemplateType = useRef(null);

  useEffect(() => {
    const loadTemplate = async () => {
      if (!productType || loadedTemplateType.current === productType) return;

      const hasFilledValues = specifications.some((spec) => spec.spec_value);
      if (hasFilledValues) return;

      const templates = await productService.getSpecTemplates(productType);
      const rows = templates.map((template, index) =>
        makeRow({
          group_name: template.group_name,
          spec_key: template.spec_key,
          display_order: template.default_order ?? index,
        })
      );
      loadedTemplateType.current = productType;
      onChange(rows.length ? rows : [makeRow()]);
    };

    loadTemplate().catch((error) => {
      console.error('Error loading specification template:', error);
    });
  }, [productType, specifications, onChange]);

  const groupedRows = useMemo(() => groupRows(specifications), [specifications]);

  const updateRow = (localId, field, value) => {
    onChange(
      specifications.map((row) =>
        row.local_id === localId ? { ...row, [field]: value } : row
      )
    );
  };

  const addRow = (groupName = '') => {
    onChange([
      ...specifications,
      makeRow({
        group_name: groupName,
        display_order: specifications.length,
      }),
    ]);
  };

  const removeRow = (localId) => {
    const nextRows = specifications.filter((row) => row.local_id !== localId);
    onChange(nextRows.length ? nextRows : [makeRow()]);
  };

  return (
    <section className="space-y-6 rounded-xl border border-gray-200 bg-gray-50/50 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Specifications</h2>
          <p className="mt-1 text-sm text-gray-500">
            Structured technical details grouped like an electronics catalog.
          </p>
        </div>
        <div className="w-full lg:w-56">
          <label className="mb-2 block text-sm font-medium text-gray-700">Product Type</label>
          <select
            value={productType}
            onChange={(event) => onProductTypeChange(event.target.value)}
            className="w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {productTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(groupedRows).map(([groupName, rows]) => (
          <div key={groupName} className="overflow-hidden rounded-lg border border-gray-200 bg-white">
            <div className="flex items-center justify-between bg-gray-100 px-4 py-3">
              <input
                value={groupName === 'Thông số khác' ? '' : groupName}
                onChange={(event) => {
                  const nextGroupName = event.target.value;
                  onChange(
                    specifications.map((row) =>
                      rows.some((groupRow) => groupRow.local_id === row.local_id)
                        ? { ...row, group_name: nextGroupName }
                        : row
                    )
                  );
                }}
                placeholder="Group name"
                className="w-full bg-transparent text-sm font-bold text-gray-900 outline-none"
              />
              <button
                type="button"
                onClick={() => addRow(groupName === 'Thông số khác' ? '' : groupName)}
                className="ml-3 inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 text-xs font-bold text-blue-600 shadow-sm hover:bg-blue-50"
              >
                <Plus className="h-4 w-4" />
                Add Row
              </button>
            </div>

            <table className="w-full table-fixed">
              <thead>
                <tr className="border-t border-gray-200 text-left text-xs font-bold uppercase tracking-wider text-gray-500">
                  <th className="w-5/12 px-4 py-3">Spec Name</th>
                  <th className="px-4 py-3">Value</th>
                  <th className="w-16 px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.local_id} className="border-t border-gray-100 align-top">
                    <td className="px-4 py-3">
                      <input
                        value={row.spec_key}
                        onChange={(event) => updateRow(row.local_id, 'spec_key', event.target.value)}
                        placeholder="Kích thước màn hình"
                        className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <textarea
                        value={row.spec_value}
                        onChange={(event) => updateRow(row.local_id, 'spec_value', event.target.value)}
                        placeholder="6.7 inch&#10;OLED&#10;120Hz"
                        rows={2}
                        className="w-full resize-y rounded-md border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => removeRow(row.local_id)}
                        className="rounded-md p-2 text-red-500 hover:bg-red-50"
                        aria-label="Remove specification row"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => addRow()}
        className="inline-flex items-center gap-2 rounded-lg border border-dashed border-blue-300 px-4 py-3 text-sm font-bold text-blue-600 hover:bg-blue-50"
      >
        <Plus className="h-4 w-4" />
        Add Specification Group or Row
      </button>

      <div className="space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500">Preview</h3>
        <ProductSpecifications specifications={groupRows(specifications.filter((row) => row.spec_key))} />
      </div>
    </section>
  );
};

export default SpecificationEditor;
