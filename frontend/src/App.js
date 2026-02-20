import React, { useState } from 'react';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [hovering, setHovering] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${API}/api/download`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'iiSU_White_UI.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Download failed', e);
    }
    setDownloading(false);
  };

  return (
    <div className="page" data-testid="preview-page">
      {/* Dot texture overlay */}
      <div className="dot-texture" />

      {/* Header */}
      <header className="header" data-testid="header">
        <div className="logo-mark">
          <span className="dot d1" />
          <span className="dot d2" />
        </div>
        <h1 className="title">iiSU <span className="title-light">White UI</span></h1>
        <p className="subtitle">Nintendo 3DS Custom Theme &middot; v1.0</p>
      </header>

      {/* Dual-screen preview */}
      <section className="screens" data-testid="screens-section">
        {/* Top screen */}
        <div className="screen-frame top-frame" data-testid="top-screen-frame">
          <span className="screen-label">Top Screen &middot; 412&times;240</span>
          <div className="screen-bezel">
            <img
              src="/top.png"
              alt="iiSU White UI top screen"
              className="screen-img"
              data-testid="top-screen-img"
              width="412"
              height="240"
            />
          </div>
        </div>

        {/* Bottom screen */}
        <div className="screen-frame bottom-frame" data-testid="bottom-screen-frame">
          <span className="screen-label">Bottom Screen &middot; 320&times;240</span>
          <div className="screen-bezel bezel-sm">
            <img
              src="/bottom.png"
              alt="iiSU White UI bottom screen"
              className="screen-img"
              data-testid="bottom-screen-img"
              width="320"
              height="240"
            />
          </div>
        </div>
      </section>

      {/* Combined preview */}
      <section className="combined" data-testid="combined-section">
        <span className="screen-label">Combined Preview</span>
        <div className="combined-bezel">
          <img
            src="/preview.png"
            alt="iiSU White UI combined preview"
            className="combined-img"
            data-testid="combined-preview-img"
          />
        </div>
      </section>

      {/* Download button */}
      <section className="download-section" data-testid="download-section">
        <button
          className={`download-btn${hovering ? ' glow' : ''}${downloading ? ' busy' : ''}`}
          data-testid="download-zip-button"
          onClick={handleDownload}
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={() => setHovering(false)}
          disabled={downloading}
        >
          <svg className="dl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          {downloading ? 'Downloading...' : 'Download Theme (.zip)'}
        </button>
        <p className="download-note">Contains top.png, bottom.png, preview.png, body_LZ.bin, info.smdh</p>
      </section>

      {/* Metadata card */}
      <section className="meta-card" data-testid="meta-card">
        <div className="meta-row">
          <span className="meta-key">Theme</span>
          <span className="meta-val">iiSU White UI</span>
        </div>
        <div className="meta-row">
          <span className="meta-key">Version</span>
          <span className="meta-val">1.0 White Edition</span>
        </div>
        <div className="meta-row">
          <span className="meta-key">Compatible</span>
          <span className="meta-val">Anemone3DS &middot; Theme Plaza</span>
        </div>
        <div className="meta-row">
          <span className="meta-key">Author</span>
          <span className="meta-val">none</span>
        </div>
        <div className="meta-row">
          <span className="meta-key">Palette</span>
          <span className="meta-val colors">
            <span className="swatch" style={{background:'#FFFFFF',border:'1px solid #e0e0e0'}} />
            <span className="swatch" style={{background:'#F8F8F8',border:'1px solid #e0e0e0'}} />
            <span className="swatch" style={{background:'#7C8CFF'}} />
            <span className="swatch" style={{background:'#9FAAFF'}} />
            <span className="swatch" style={{background:'#B8C0FF'}} />
          </span>
        </div>
      </section>

      <footer className="footer" data-testid="footer">
        Inspired by iiSU Network &middot; All artwork original &middot; Not affiliated with Nintendo
      </footer>
    </div>
  );
}

export default App;
