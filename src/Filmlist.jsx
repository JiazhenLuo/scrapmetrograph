import Card from "./components/Cards/Card.jsx";
import "./App.css";
import "./App.jsx";
import React, { useEffect } from "react";
import { useState } from "react";

function Filmlist({ films, onFilmClick, setSelectedMovie }) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 如果已经从父组件接收到电影数据，直接使用
    if (films && films.length > 0) {
      setMovies(films);
      setLoading(false);
      return;
    }

    // 否则尝试加载数据
    const loadMovies = async () => {
      try {
        // 首先尝试从本地加载
        const localResponse = await fetch('./data/films.json');
        
        if (localResponse.ok) {
          // 本地数据加载成功
          const localData = await localResponse.json();
          console.log("从本地加载的电影数据", localData);
          setMovies(localData);
          setLoading(false);
          return;
        }

        // 如果本地加载失败，尝试绝对路径
        console.log("相对路径加载失败，尝试绝对路径...");
        const absoluteResponse = await fetch('/data/films.json');
        
        if (absoluteResponse.ok) {
          const absoluteData = await absoluteResponse.json();
          console.log("从绝对路径加载的电影数据", absoluteData);
          setMovies(absoluteData);
          setLoading(false);
          return;
        }

        // 尝试备份路径
        console.log("尝试备份路径...");
        const backupResponse = await fetch('./scraper/metrograph_movies.json');
        
        if (backupResponse.ok) {
          const backupData = await backupResponse.json();
          console.log("从备份路径加载的电影数据", backupData);
          setMovies(backupData);
          setLoading(false);
          return;
        }

        // 如果本地加载失败，尝试从远程服务器加载
        console.log("未找到本地数据，从远程服务器加载...");
        const remoteResponse = await fetch("https://movieserver-g46f.onrender.com");
        
        if (remoteResponse.ok) {
          const remoteData = await remoteResponse.json();
          console.log("从远程服务器加载的电影数据", remoteData);
          setMovies(remoteData);
        } else {
          throw new Error("无法从远程服务器加载数据");
        }
      } catch (error) {
        console.error("加载电影数据失败:", error);
        setError("无法加载电影数据，请稍后再试");
      } finally {
        setLoading(false);
      }
    };

    loadMovies();
  }, [films]);

  if (loading) {
    return <div className="loading">loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="box-container">
      {movies.length ? (
        movies.map((movie, index) => (
          <Card
            key={movie.id || index}
            img={movie.poster_url || ""}
            title={movie.title || ""}
            director={`Director: ${movie.director || ""}`}
            screenTime={
              movie.screenings && movie.screenings.length > 0
                ? `${movie.screenings[0].date} - ${movie.screenings[0].showtimes[0].time}`
                : "Coming Soon"
            }
            link={movie.link || movie.detail_url || ""}
            time={movie.year + "/" + movie.runtime}
            Description={movie.synopsis || ""}
            poster={movie.poster_url || ""}
            screenings={movie.screenings || []}
            onClick={() => {
              console.log("电影已选择:", movie.title);
              if (onFilmClick) {
                onFilmClick(movie);
              } else if (setSelectedMovie) {
                setSelectedMovie(movie);
              }
            }}
          />
        ))
      ) : (
        <div className="loading">没有找到电影数据</div>
      )}
    </div>
  );
}

export default Filmlist;
