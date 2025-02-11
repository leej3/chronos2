import axiosApi from './axios';

export const switchSeason = async (seasonValue) => {
  return await axiosApi.post('/switch-season', { season_value: seasonValue });
};
