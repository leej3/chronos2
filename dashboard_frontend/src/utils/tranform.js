export const formatNumber = (
  number,
  minimumFractionDigits = 1,
  maximumFractionDigits = 1,
) => {
  if (number === null || number === undefined || number === 'N/A') return 'N/A';
  return new Intl.NumberFormat([], {
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(number);
};

export const formatTemperature = (temp) => {
  if (temp === null || temp === undefined || temp === 'N/A') return 'N/A';
  return `${formatNumber(temp)}°F`;
};
