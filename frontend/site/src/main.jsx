import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './styles.css';
import { startBeacon } from './defender/beacon.js';
import { fetchAndSolveChallenge } from './defender/pow.js';

startBeacon();

// Invisible proof-of-work — fires on first page load. Real browsers solve
// a small SHA-256 puzzle in ~50ms (humans never notice). Naive scrapers
// that don't run JS will never produce the proof, and their absence of a
// solved-PoW marker becomes one of the bot-detection signals.
// Fire-and-forget — failure must NOT block React render.
fetchAndSolveChallenge().catch((e) => {
  console.warn('[this1] PoW skipped:', e?.message || e);
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
