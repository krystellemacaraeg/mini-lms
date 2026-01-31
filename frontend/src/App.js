import React from 'react';
import './styles/global.css';
import './components/Button.css';
import './components/Card.css';
import './components/Form.css';
import './components/Sidebar.css';

function App() {
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">Mini-LMS</div>
        <ul className="sidebar-nav">
          <li><a href="#" className="sidebar-link active">Dashboard</a></li>
          <li><a href="#" className="sidebar-link">My Courses</a></li>
          <li><a href="#" className="sidebar-link">Assignments</a></li>
          <li><a href="#" className="sidebar-link">Profile</a></li>
        </ul>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <h1>Welcome to Mini-LMS</h1>
        <p>The learning management system is taking shape!</p>

        {/* Demo Card */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Design System Preview</h3>
          </div>
          <div className="card-body">
            <p>This card demonstrates reusable component system.</p>
            
            {/* Demo Buttons */}
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button className="btn btn-primary">Primary Button</button>
              <button className="btn btn-secondary">Secondary Button</button>
              <button className="btn btn-danger">Danger Button</button>
            </div>

            {/* Demo Form */}
            <div className="form-group" style={{ marginTop: '2rem' }}>
              <label className="form-label">Example Input</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Type something..."
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;