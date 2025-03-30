import './Card.css';
import React from 'react';
import { isAllSoldOut } from '../../utils/formatScreenings';

/**
 * 电影卡片组件
 * @param {Object} props 组件属性
 * @param {string} props.img 电影海报图片URL
 * @param {string} props.title 电影标题
 * @param {string} props.screenTime 放映时间
 * @param {string} props.director 导演信息
 * @param {string} props.time 电影时长
 * @param {string} props.link 购票链接
 * @param {string} props.Description 电影简介
 * @param {Array} props.screenings 电影放映场次数据
 * @param {Function} props.onClick 点击卡片事件处理函数
 * @returns {JSX.Element}
 */
function Card(props) {
    // 检查电影是否全部售罄
    const allSoldOut = props.screenings ? isAllSoldOut(props.screenings) : false;
    
    return (
        <div className="card" onClick={props.onClick}>
            <img className="card-image" src={props.img} alt={props.title} />
            
            <div className="card-content">
                <h2 className="card-title">{props.title}</h2>
                
                <div className="card-details">
                    <h3 className="card-screentime">{props.screenTime || "Coming Soon"}</h3>
                    <h3 className="card-director">{props.director}</h3>
                </div>
                <div className='card-duration-container'>
                    
                    <p className='card-duration'> {props.time}</p>
                    <p className="card-description">{props.Description}</p>

                </div>
                
                <button className={`card-button ${allSoldOut ? 'sold-out' : ''}`}>
                    <a 
                        href={allSoldOut ? '#' : (props.link || '#')} 
                        target={allSoldOut ? '_self' : '_blank'} 
                        rel={allSoldOut ? '' : 'noopener noreferrer'}
                        onClick={allSoldOut ? (e) => e.preventDefault() : undefined}
                        className={allSoldOut ? 'sold-out' : ''}
                    >
                        {allSoldOut ? 'Sold Out' : 'Buy Ticket'}
                    </a>
                </button>
            </div>
        </div>
    );
}

export default Card;