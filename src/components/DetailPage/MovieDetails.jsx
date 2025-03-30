import React from "react";
import "./MovieDetails.css";
import ScreentimeDropdown from "../ScreentimeDropdown";
import { isAllSoldOut } from "../../utils/formatScreenings";

function MovieDetails({ movie }) {
  console.log("Selected Movie in Details:", movie);
  if (!movie) {
    return <p id="placeholder">Please select a movie to see the details.</p>;
  }

  // 检查电影是否全部售罄
  const allSoldOut = isAllSoldOut(movie.screenings || []);

  return (
    <>
      <div className="movie-details">
        <div className="movieInfo-Container">

          <div className="title">
            <div className="empty"></div>
            <div className="title-Info">
              {movie.title}
            </div>
          </div>

          <div className="time">
            <div className="empty"></div>
            <div className="time-Info">{movie.year + "/" + movie.runtime}
            </div>
          </div>

          <div className="director">
            <div className="Director-text">Director:</div>
            <div className="director-Info">{movie.director}</div>
          </div>

          <div className="description">
            <div className="description-Text">Description:</div>
            <div className="description-Info">{movie.synopsis}</div>
          </div>

          <div className="screentime">
            <div className="screentime-Text">Screen Time:</div>
            <ScreentimeDropdown screenings={movie.screenings || []} />
          </div>

        </div>
        <div className="poster-Container">
          <img src={movie.poster_url} alt={movie.title} className="details-image" />
          <button className={`buy-button ${allSoldOut ? 'sold-out' : ''}`}>
            <a 
              href={allSoldOut ? '#' : (movie.link || movie.detail_url || '#')}
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
    </>
  );
}

export default MovieDetails;
