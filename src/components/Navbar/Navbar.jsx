import React from "react";
import "./Navbar.css";

const navbar = () => {
  return (
    <>
      <div className="Nav-container">
        <div className="Navbar">
          <div className="logo">
            <p>What's good in Metrograph?</p>
          </div>

          <div className="month">
            <p>April_2025</p>
          </div>
        </div>

        <div className="search">
          <input className="search-input" type="text" placeholder="🔍 search" />
          <button className="search-text">Search</button>
        </div>
      </div>
    </>
  );
};

export default navbar;
