// Placeholder for ChatWindow component
import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Using axios for simplicity

// Simple component to render diff with basic styling
const DiffViewer = ({ diff }) => {
  if (!diff) return null;
  // Basic styling for added/removed lines
  const lines = diff.split('\n').map((line, index) => {
    let style = {};
    if (line.startsWith('+') && !line.startsWith('+++')) {
      style = { backgroundColor: '#e6ffed', color: '#22863a' }; // Green background for additions
    } else if (line.startsWith('-') && !line.startsWith('---')) {
      style = { backgroundColor: '#ffeef0', color: '#b31d28' }; // Red background for deletions
    } else if (line.startsWith('@@')) {
        style = { color: '#6f42c1', fontWeight: 'bold' }; // Purple for hunk headers
    }
    return <div key={index} style={style}>{line || ' '}</div>; // Render empty lines too
  });

  // Add max-height and overflow-y-auto for scrollability
  return (
    <pre className="whitespace-pre-wrap text-xs p-2 border bg-gray-50 overflow-x-auto overflow-y-auto max-h-60"> {/* Added max-h-60 and overflow-y-auto */}
      <code>
        {lines}
      </code>
    </pre>
  );
};


function ChatWindow({ userId, currentEnvironment }) { // Accept currentEnvironment prop
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingDiff, setPendingDiff] = useState(null); // State to hold the diff patch
  const [aiProvider, setAiProvider] = useState('openai'); // Add state for AI provider, default to 'openai'

  // Log when currentEnvironment changes
  useEffect(() => {
    console.log("ChatWindow received currentEnvironment:", currentEnvironment);
    // Clear pending diff if environment changes
    setPendingDiff(null);
  }, [currentEnvironment]);

  const handleSend = async () => {
    if (!input.trim() || !currentEnvironment) {
        if (!currentEnvironment) {
            alert("Please select an environment first.");
        }
        return;
    }
    if (pendingDiff) {
        alert("Please accept or reject the current changes before sending a new request.");
        return;
    }

    const userMessage = { sender: 'user', text: input };
    setMessages([...messages, userMessage]);
    const currentInput = input; // Capture input before clearing
    setInput('');
    setIsLoading(true);

    try {
      console.log(`Sending AI request for env: ${currentEnvironment}, message: ${currentInput}`);
      console.log(`Sending AI request using ${aiProvider} for env: ${currentEnvironment}, message: ${currentInput}`); // Log provider
      const response = await axios.post('http://localhost:3001/ai-modify-scene', {
          message: currentInput,
          environmentName: currentEnvironment,
          aiProvider: aiProvider // Send selected provider to backend
      });

      if (response.data.success && response.data.diff) {
        console.log("Received diff from backend.");
        setPendingDiff(response.data.diff);
        // Add a system message indicating changes are ready for review
        const reviewMessage = { sender: 'ai', text: 'AI has proposed changes. Please review the diff below and choose an action.' };
        setMessages(prev => [...prev, reviewMessage]);
      } else {
        throw new Error(response.data.error || "Received unexpected response from backend.");
      }

    } catch (error) {
      console.error("Error calling AI modification API:", error);
      const errorMessageText = error.response?.data?.details || error.message || 'Error processing request.';
      const errorMessage = { sender: 'ai', text: `Error: ${errorMessageText}` };
      setMessages(prev => [...prev, errorMessage]);
      setPendingDiff(null); // Clear diff on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccept = async () => {
    if (!pendingDiff) return;
    setIsLoading(true); // Indicate processing
    try {
        const response = await axios.post('http://localhost:3001/ai-accept-changes');
        if (response.data.success) {
            const successMessage = { sender: 'ai', text: 'Changes accepted and applied successfully!' };
            setMessages(prev => [...prev, successMessage]);
            setPendingDiff(null); // Clear diff
        } else {
            throw new Error(response.data.error || "Failed to accept changes.");
        }
    } catch (error) {
        console.error("Error accepting changes:", error);
        const errorMessageText = error.response?.data?.details || error.message || 'Error accepting changes.';
        const errorMessage = { sender: 'ai', text: `Error: ${errorMessageText}` };
        setMessages(prev => [...prev, errorMessage]);
        // Keep diff visible for potential retry or rejection
    } finally {
        setIsLoading(false);
    }
  };

  const handleReject = async () => {
    if (!pendingDiff) return;
    setIsLoading(true); // Indicate processing
     try {
        const response = await axios.post('http://localhost:3001/ai-reject-changes');
        if (response.data.success) {
            const rejectMessage = { sender: 'ai', text: 'Changes rejected.' };
            setMessages(prev => [...prev, rejectMessage]);
            setPendingDiff(null); // Clear diff
        } else {
            throw new Error(response.data.error || "Failed to reject changes.");
        }
    } catch (error) {
        console.error("Error rejecting changes:", error);
        const errorMessageText = error.response?.data?.details || error.message || 'Error rejecting changes.';
        const errorMessage = { sender: 'ai', text: `Error: ${errorMessageText}` };
        setMessages(prev => [...prev, errorMessage]);
        // Keep diff visible? Or clear anyway? Let's clear.
        setPendingDiff(null);
    } finally {
        setIsLoading(false);
    }
  };


  return (
    <div className="w-full bg-gray-100 p-4 flex flex-col h-full"> {/* Use full width */}
      <h2 className="text-lg font-semibold mb-4">Chat Customization ({currentEnvironment || 'No Env Selected'})</h2>
      <div className="flex-1 overflow-y-auto mb-4 border p-2 bg-white">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-2 rounded max-w-[80%] break-words ${msg.sender === 'user' ? 'bg-blue-200' : 'bg-gray-200'}`}>
              {msg.text}
            </span>
          </div>
        ))}
        {/* Display Diff Viewer and Action Buttons if diff exists */}
        {pendingDiff && (
          <div className="mt-4 p-2 border rounded bg-yellow-50">
            <h3 className="font-semibold mb-2 text-center">Proposed Changes:</h3>
            {/* Moved Buttons Above DiffViewer */}
            <div className="flex justify-center space-x-4 mb-2"> {/* Added mb-2 */}
              <button
                onClick={handleAccept}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-1 px-3 rounded disabled:opacity-50"
                disabled={isLoading}
              >
                Accept
              </button>
              <button
                onClick={handleReject}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded disabled:opacity-50"
                disabled={isLoading}
              >
                Reject
              </button>
            </div>
            {/* DiffViewer now below buttons */}
            <DiffViewer diff={pendingDiff} />
          </div>
        )}
        {isLoading && !pendingDiff && <div className="text-center text-gray-500 mt-2">AI is thinking...</div>}
        {isLoading && pendingDiff && <div className="text-center text-gray-500 mt-2">Processing confirmation...</div>}
      </div>
      {/* AI Provider Selection */}
      <div className="mb-2 flex items-center justify-center space-x-4">
        <span className="text-sm font-medium text-gray-700">AI Provider:</span>
        <label className={`flex items-center space-x-1 cursor-pointer p-1 rounded ${aiProvider === 'openai' ? 'bg-blue-100 ring-1 ring-blue-400' : ''}`}>
          <input
            type="radio"
            name="aiProvider"
            value="openai"
            checked={aiProvider === 'openai'}
            onChange={() => setAiProvider('openai')}
            className="form-radio h-4 w-4 text-blue-600"
            disabled={isLoading || !!pendingDiff} // Disable during loading or diff review
          />
          <span className="text-sm">OpenAI</span>
        </label>
        <label className={`flex items-center space-x-1 cursor-pointer p-1 rounded ${aiProvider === 'groq' ? 'bg-green-100 ring-1 ring-green-400' : ''}`}>
          <input
            type="radio"
            name="aiProvider"
            value="groq"
            checked={aiProvider === 'groq'}
            onChange={() => setAiProvider('groq')}
            className="form-radio h-4 w-4 text-green-600"
            disabled={isLoading || !!pendingDiff} // Disable during loading or diff review
          />
          <span className="text-sm">Groq (deepseek-r1)</span>
        </label>
      </div>
      {/* Input Area */}
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()} // Prevent send on enter if loading
          className="flex-1 border p-2 rounded-l"
          placeholder={currentEnvironment ? "e.g., add a blue cube at 0,1,0" : "Select environment first"}
          disabled={isLoading || !currentEnvironment || !!pendingDiff} // Disable if loading, no env, or diff pending
        />
        <button
          onClick={handleSend}
          className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-r disabled:opacity-50"
          disabled={isLoading || !currentEnvironment || !!pendingDiff} // Disable if loading, no env, or diff pending
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;