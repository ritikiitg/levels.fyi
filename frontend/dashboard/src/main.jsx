import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

// StrictMode intentionally OFF: it double-mounts effects in dev, which races
// the WebSocket open/close lifecycle and leaves the indicator stuck on
// "connecting…". Production builds don't have StrictMode regardless.
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
