import React, { useState } from "react";
import "./ScreentimeDropdown.css";

/**
 * 放映时间下拉菜单组件
 * @param {Object} props
 * @param {Array} props.screenings - 电影放映场次数据
 * @param {string} props.className - 额外的CSS类名
 * @returns {JSX.Element}
 */
function ScreentimeDropdown({ screenings, className = "" }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  // 切换下拉菜单状态
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  // 检查电影是否有放映场次信息
  const hasScreenings = screenings && screenings.length > 0;

  // 检查第一个放映场次是否已售罄
  const isFirstScreeningSoldOut = hasScreenings && 
    screenings[0].showtimes && 
    screenings[0].showtimes[0] && 
    screenings[0].showtimes[0].status === "Sold Out";

  return (
    <div className={`screentime-dropdown ${className}`}>
      <div 
        className={`screentime-dropdown-header ${isFirstScreeningSoldOut ? 'sold-out' : ''}`}
        onClick={toggleDropdown}
      >
        {hasScreenings ? (
          <>
            {screenings[0].date} - {screenings[0].showtimes[0].time}
            {isFirstScreeningSoldOut && <span className="sold-out-badge">Sold Out</span>}
          </>
        ) : (
          "No screenings available"
        )}
        <span className={`dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}>▼</span>
      </div>
      
      {isDropdownOpen && hasScreenings && (
        <div className="screentime-dropdown-content">
          {screenings.map((screening, dateIndex) => (
            <div key={dateIndex} className="screening-date">
              <div className="date-header">{screening.date}</div>
              <div className="showtimes-container">
                {screening.showtimes.map((showtime, timeIndex) => (
                  <div 
                    key={timeIndex} 
                    className={`showtime-item ${showtime.status === "Sold Out" ? "sold-out" : ""}`}
                  >
                    <span className="showtime">{showtime.time}</span>
                    <span className="status">{showtime.status}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ScreentimeDropdown; 