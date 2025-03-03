import axiosApi from './axios';

export const switchSeason = async (seasonMode) => {
  return await axiosApi.post('/switch-season', { season_mode: seasonMode });
};
