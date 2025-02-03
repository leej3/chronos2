import moment from 'moment-timezone';

const localTime = Intl.DateTimeFormat().resolvedOptions().timeZone;

export const getFormattedTime = (
  format = `h:mm:ss A [${localTime}] , ddd, MMM DD YYYY`,
  date = null,
) => {
  return moment(date || undefined)
    .tz(localTime)
    .format(format);
};
