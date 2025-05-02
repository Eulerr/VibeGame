import React, { useState, useCallback } from 'react';
import EnvironmentSelector from './components/EnvironmentSelector';
// GameCanvas removed
import ChatWindow from './components/ChatWindow';
// Ensure Tailwind styles are imported (usually in main.jsx or index.css)
// import './index.css'; // Or wherever your Tailwind base styles are imported

function App() {
  // selectedEnv is still needed for saving the correct environment type
  const [selectedEnv, setSelectedEnv] = useState(null);
  // gameConfig state and handleSceneUpdate removed as scenes are now static HTML files.
  // const [gameConfig, setGameConfig] = useState({ objects: [] }); // Removed
  // isChatVisible state removed, ChatWindow will always be visible

  // Callback to update game config from ChatWindow (AI responses) - Removed
  // const handleSceneUpdate = useCallback((updates) => { ... }, []); // Removed
















  // Callback to handle saving the game selection
  const handleSave = async () => {
    if (!selectedEnv) {
      alert("Please select an environment first.");
      return;
    }
    const gameName = prompt("Enter a name for your game:", "MyGame");
    if (!gameName) return; // User cancelled

    console.log("Saving game selection:", gameName, selectedEnv); // Removed gameConfig from log
    try {
      const response = await fetch('http://localhost:3001/save-game', { // Ensure server is running
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: gameName, environment: selectedEnv }) // Removed config from body
      });
      const result = await response.json();
      if (result.success) {
        alert("Game saved successfully!");
      } else {
        alert(`Error saving game: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error saving game:", error);
      alert(`Failed to connect to server. Is it running? Error: ${error.message}`);
    }
  };

  return (
    // Main container: Use a cooler slate background
    <div className="h-screen w-screen flex flex-col bg-slate-100">
      {/* Header: Darker slate, slightly more padding */}
      <header className="p-4 bg-slate-800 text-slate-100 flex justify-between items-center shadow-lg">
        <h1 className="text-xl font-semibold">GameBuilder</h1>
        <div className="flex items-center space-x-3">
          {/* Chat toggle button removed */}
          {selectedEnv && ( // Only show save button if an environment is selected
            <button
              onClick={handleSave}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-md shadow-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-800"
            >
              Save Game
            </button>
          )}
        </div>
      </header>
      {/* Main content area: Add padding and a gap for visual separation */}
      <div className="flex flex-1 overflow-hidden p-4 gap-4">
        {/* Environment Selector: White background, rounded, shadow, softer border */}
        <div className="w-1/4 p-4 overflow-y-auto bg-white rounded-lg shadow border border-slate-200">
           <EnvironmentSelector onSelect={setSelectedEnv} /> {/* Pass setSelectedEnv for saving */}
        </div>

        {/* Chat Window: White background, rounded, shadow, softer border */}
        <div className="flex-1 p-4 overflow-y-auto bg-white rounded-lg shadow border border-slate-200">
          <ChatWindow userId="debug-user-001" currentEnvironment={selectedEnv} /> {/* Pass selectedEnv */}
        </div>
      </div>
    </div>
  );
}

export default App;
