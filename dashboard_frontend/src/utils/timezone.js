import moment from 'moment-timezone';

export const getFormattedTime = () => {
  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return moment()
    .tz(userTimeZone)
    .format(`h:mm:ss A [${userTimeZone}] , ddd, MMM DD YYYY`);
};
