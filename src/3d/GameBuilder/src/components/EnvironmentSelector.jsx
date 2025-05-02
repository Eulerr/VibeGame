// Placeholder for EnvironmentSelector component
import React, { useEffect } from 'react';
// Removed: import { Command } from '@tauri-apps/api/shell';

function EnvironmentSelector({ onSelect }) {
  // Function to request the backend server to open the scene file
  const handleOpenGameWindow = async (environmentName) => {
    console.log(`Requesting backend to open scene: ${environmentName}`);

    // Call onSelect early to update parent state if needed for other logic
    onSelect(environmentName);

    try {
      const response = await fetch('http://localhost:3001/open-scene', { // Ensure port matches server.js
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ environmentName }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Backend response:', result.message);

    } catch (error) {
      console.error("Error requesting backend to open scene:", error);
      // Optionally, display an error message to the user here
    }
  };

  // Add useEffect for rendering lifecycle logging
  useEffect(() => {
    console.log("EnvironmentSelector mounted");
    return () => {
      console.log("EnvironmentSelector unmounted");
    };
  }, []);

  // TODO: Implement environment selection grid with better styling
  return (
    <div className="p-4 space-y-4">
      <h2 className="text-lg font-semibold mb-3">Select Environment</h2>
      {/* Placeholder tiles - replace with actual grid/cards */}
      <button
        onClick={() => handleOpenGameWindow('shooter')}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Shooter
      </button>
      <button
        onClick={() => handleOpenGameWindow('parkour')}
        className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Parkour
      </button>
      <button
        onClick={() => handleOpenGameWindow('adventure')}
        className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Adventure
      </button>
      <button
        onClick={() => handleOpenGameWindow('puzzle')}
        className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Puzzle
      </button>
       <button
        onClick={() => handleOpenGameWindow('rpg')}
        className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        RPG
      </button>
       <button
        onClick={() => handleOpenGameWindow('racing')}
        className="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Racing
      </button>
       <button
        onClick={() => handleOpenGameWindow('sandbox')}
        className="w-full bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Sandbox
      </button>
      <button
        onClick={() => handleOpenGameWindow('survival')}
        className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
      >
        Survival
      </button>
    </div>
  );
}

export default EnvironmentSelector;