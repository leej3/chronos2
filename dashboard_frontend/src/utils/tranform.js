const formatTime = {
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

export const formatDate = (date, format = 'HH:mm:ss') => {
  if (date === null || date === undefined || date === 'N/A') return 'N/A';
  if (format === 'HH:mm:ss') {
    return new Date(date).toLocaleString('en-US', {
      timeZone: 'America/Chicago',
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  }
  return new Date(date).toLocaleString('en-US', {
    ...formatTime,
  });
};

export const formatTimeChicagoByTimestamp = (timestamp) => {
  return new Intl.DateTimeFormat('en-US', {
    ...formatTime,
  }).format(new Date(timestamp * 1000));
};

export const convertUCTtoUnixTimestamp = (dateStr) =>
  Math.floor(new Date(dateStr).getTime() / 1000);
