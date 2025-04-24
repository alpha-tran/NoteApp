import React from "react";
import { Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to DevSecOps App</h1>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<div>Home Page</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

