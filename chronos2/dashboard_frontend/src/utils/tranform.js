export const formatNumber = (number, minimumFractionDigits = 2) =>
    new Intl.NumberFormat([], {
      minimumFractionDigits,
    }).format(number);