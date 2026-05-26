const normalizeGroupedSpecifications = (specifications) => {
  if (!specifications) return [];

  if (Array.isArray(specifications)) {
    const grouped = specifications.reduce((acc, spec) => {
      const groupName = spec.group_name || 'Thông số khác';
      if (!acc[groupName]) acc[groupName] = [];
      acc[groupName].push(spec);
      return acc;
    }, {});
    return Object.entries(grouped);
  }

  return Object.entries(specifications);
};

const ProductSpecifications = ({ specifications, emptyMessage = 'Chưa có thông số kỹ thuật.' }) => {
  const groups = normalizeGroupedSpecifications(specifications);

  if (!groups.length) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-200 bg-gray-50 p-8 text-center text-sm font-semibold text-gray-400">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white">
      {groups.map(([groupName, specs]) => (
        <div key={groupName} className="border-b border-gray-100 last:border-b-0">
          <div className="bg-gray-50 px-5 py-3 text-sm font-black text-gray-900">
            {groupName}
          </div>
          <table className="w-full table-fixed">
            <tbody>
              {specs.map((spec, index) => (
                <tr key={spec.id || `${groupName}-${spec.key || spec.spec_key}-${index}`} className="border-t border-gray-100 first:border-t-0">
                  <td className="w-2/5 align-top bg-gray-50/50 px-5 py-4 text-sm font-bold text-gray-500">
                    {spec.key || spec.spec_key}
                  </td>
                  <td className="align-top px-5 py-4 text-sm font-semibold leading-6 text-gray-900 whitespace-pre-line">
                    {spec._variantHighlight ? (
                      <span className="inline-flex items-center gap-1.5">
                        <span className="font-bold text-primary">{spec.value || spec.spec_value || '-'}</span>
                        <span className="text-[9px] font-black uppercase tracking-widest bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">
                          Phiên bản này
                        </span>
                      </span>
                    ) : (
                      spec.value || spec.spec_value || '-'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};

export default ProductSpecifications;
