import { useState, useEffect } from "react";
import "./App.css";
import Navbar from "./components/Navbar/Navbar.jsx";
import MovieDetails from "./components/DetailPage/MovieDetails.jsx";
import Filmlist from "./Filmlist.jsx";

function App() {
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [isMobileLayout, setIsMobileLayout] = useState(window.innerWidth < 1000);

  useEffect(() => {
    const handleResize = () => {
      setIsMobileLayout(window.innerWidth < 1000);
    };

    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="app-container">
      <div className="Navbar-Container">
        <Navbar />
      </div>

      {isMobileLayout ? (
        <div className="filmlist-container">
          <Filmlist setSelectedMovie={setSelectedMovie} />
        </div>
      ) : (
        <div className="content-container">
          <div className="filmlist-container">
            <Filmlist setSelectedMovie={setSelectedMovie} />
          </div>

          <div className="movie-details-container">
            {selectedMovie ? (
              <MovieDetails movie={selectedMovie} />
            ) : (
              <p id="placeholder">Select a movie to see the details here.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
