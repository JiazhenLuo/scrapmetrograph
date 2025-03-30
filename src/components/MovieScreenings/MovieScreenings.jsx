import React from 'react';
import './MovieScreenings.css';
import { getFirstScreeningTime } from '../../utils/formatScreenings';

/**
 * 电影放映场次信息组件 - 简化版本，适用于电影列表
 * @param {Object} props
 * @param {Array} props.screenings - 放映场次数据
 * @returns {JSX.Element}
 */
function MovieScreenings({ screenings }) {
  // 获取第一个场次时间
  const screeningInfo = getFirstScreeningTime(screenings);
  
  // 简单显示场次信息
  return (
    <div className="movie-screenings">
      <div className="screening-time">{screeningInfo}</div>
    </div>
  );
}

export default MovieScreenings; 