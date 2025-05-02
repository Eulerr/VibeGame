import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
// import GameWindow from './components/GameWindow'; // Removed unused import
import './styles.css'; // Import Tailwind CSS base styles

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        {/* <Route path="/game/:environmentName" element={<GameWindow />} /> Removed unused route */}
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
