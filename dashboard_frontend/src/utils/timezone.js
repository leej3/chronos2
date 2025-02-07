import moment from 'moment-timezone';

export const convertUtcToLocal = (
  utcTime,
  timeZone = 'America/Chicago',
  format = 'YYYY-MM-DD HH:mm:ss',
) => {
  return moment.utc(utcTime).tz(timeZone).format(format);
};
