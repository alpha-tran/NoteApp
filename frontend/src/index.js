import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import log from 'loglevel';

// Configure loglevel
// Use 'debug' in development, 'info' in production
if (process.env.NODE_ENV === 'development') {
  log.setLevel('debug');
} else {
  log.setLevel('info');
}

log.info(`App starting in ${process.env.NODE_ENV} mode`);

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Failed to find the root element');

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);