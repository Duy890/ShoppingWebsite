export const formatStorage = (storageStr) => {
  if (!storageStr) return storageStr;

  return storageStr.replace(/(\d+)GB(\s+(SSD|HDD))?/gi, (match, gb, typeGroup, type) => {
    const num = parseInt(gb, 10);
    if (num >= 1000 && num % 1000 === 0) {
      const tb = num / 1000;
      const tbLabel = tb === Math.floor(tb) ? `${Math.floor(tb)}TB` : `${tb.toFixed(1)}TB`;
      return type ? `${tbLabel} ${type.toUpperCase()}` : tbLabel;
    }
    return match;
  });
};
