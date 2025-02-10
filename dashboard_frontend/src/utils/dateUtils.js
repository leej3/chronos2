import { formatInTimeZone } from 'date-fns-tz';

export const getFormattedChicagoTime = () => {
  const now = new Date();
  try {
    const timeInChicago = formatInTimeZone(
      now,
      'America/Chicago',
      "h:mm:ss a 'CST'",
    );
    const dateInChicago = formatInTimeZone(
      now,
      'America/Chicago',
      'EEE, MMM d',
    );
    return `${timeInChicago}, ${dateInChicago}`;
  } catch (error) {
    console.error('Error formatting time:', error);
    return '';
  }
};
