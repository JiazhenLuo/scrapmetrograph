/**
 * 格式化电影放映场次工具函数
 */

/**
 * 获取第一个放映场次的日期和时间
 * @param {Array} screenings - 放映场次数组
 * @returns {string} 格式化后的日期和时间，如果没有放映场次则返回"Coming Soon"
 */
export const getFirstScreeningTime = (screenings) => {
  if (!screenings || !Array.isArray(screenings) || screenings.length === 0) {
    return "Coming Soon";
  }

  const firstScreening = screenings[0];
  if (!firstScreening.showtimes || firstScreening.showtimes.length === 0) {
    return firstScreening.date || "Coming Soon";
  }

  return `${firstScreening.date} - ${firstScreening.showtimes[0].time}`;
};

/**
 * 检查电影是否有可用的放映场次
 * @param {Array} screenings - 放映场次数组
 * @returns {boolean} 是否有可用的放映场次
 */
export const hasAvailableScreenings = (screenings) => {
  if (!screenings || !Array.isArray(screenings) || screenings.length === 0) {
    return false;
  }

  // 检查是否至少有一个非售罄的放映场次
  return screenings.some(screening => 
    screening.showtimes && 
    screening.showtimes.some(showtime => showtime.status !== "Sold Out")
  );
};

/**
 * 检查电影是否全部售罄
 * @param {Array} screenings - 放映场次数组
 * @returns {boolean} 是否全部售罄
 */
export const isAllSoldOut = (screenings) => {
  if (!screenings || !Array.isArray(screenings) || screenings.length === 0) {
    return false; // 如果没有场次，返回false（表示为"Coming Soon"状态）
  }

  // 检查是否所有场次都已售罄
  return screenings.every(screening => 
    screening.showtimes && 
    screening.showtimes.every(showtime => showtime.status === "Sold Out")
  );
};

/**
 * 获取电影的所有可用放映日期
 * @param {Array} screenings - 放映场次数组
 * @returns {Array} 日期字符串数组
 */
export const getScreeningDates = (screenings) => {
  if (!screenings || !Array.isArray(screenings)) {
    return [];
  }
  
  return screenings.map(screening => screening.date);
};

export default {
  getFirstScreeningTime,
  hasAvailableScreenings,
  isAllSoldOut,
  getScreeningDates
}; 