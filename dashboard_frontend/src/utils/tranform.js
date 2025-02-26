const format = {
  timeZone: 'America/Chicago',
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
  hour12: false,
};

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

export const formatDate = (date) => {
  if (date === null || date === undefined || date === 'N/A') return 'N/A';
  return new Date(date).toLocaleString('en-US', format);
};

export const formatTimeChicagoByTimestamp = (timestamp) => {
  return new Intl.DateTimeFormat('en-US', {
    ...format,
  }).format(new Date(timestamp * 1000));
};

export const convertUCTtoUnixTimestamp = (dateStr) =>
  Math.floor(new Date(dateStr).getTime() / 1000);
