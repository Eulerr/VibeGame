import express from 'express';
import sqlite3Import from 'sqlite3'; // Import default export
import fetch from 'node-fetch'; // Ensure node-fetch v2 is installed
import fs from 'fs-extra'; // fs-extra supports both CJS and ESM
import path from 'path';
import { fileURLToPath } from 'url'; // To handle __dirname equivalent
import { exec } from 'child_process'; // Import exec for running shell commands
import cors from 'cors'; // Import the cors middleware
import { createPatch } from 'diff'; // Import diff library for creating patches

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sqlite3 = sqlite3Import.verbose(); // Get the verbose version

const app = express();
const PORT = 3001; // Define the port

app.use(express.json()); // Middleware to parse JSON bodies
app.use(cors({ origin: 'http://localhost:1420' })); // Enable CORS specifically for the frontend origin

// --- AI Configuration ---
const AI_API_KEY = "dababy60"; // As provided
const AI_BASE_URL = "http://localhost:4269/api/v1"; // As provided
const AI_MODEL_NAME = "models/gemini-2.5-pro-exp-03-25"; // As provided
const AI_SYSTEM_PROMPT = `You are an expert web developer specializing in Three.js and HTML. You will be given the full HTML content of a game scene file. Your task is to modify the JavaScript code within the <script type="module"> tag based on the user's request.
IMPORTANT: Respond ONLY with the complete, modified HTML file content. Wrap the entire response within triple backticks like this:
\`\`\`html
[Your modified HTML content here]
\`\`\`
Do NOT include any other text, explanations, or apologies outside the backticks. Ensure the final HTML is valid and the JavaScript logic is correct.`;

// --- State for Pending Modifications ---
let pendingModification = {
  originalPath: null,
  // newContent: null, // Content is written directly, no need to store here
  diffPatch: null, // Still needed for frontend display
};

// --- Database Setup ---
const dbPath = path.join(__dirname, 'database.db');
let db; // Declare db variable

try {
  db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
      console.error("Error opening database:", err.message);
      // Exit or handle critical error if DB can't open
      process.exit(1);
    } else {
      console.log("Connected to the SQLite database.");
      // Create the games table if it doesn't exist
      db.run(`CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        environment TEXT NOT NULL,
        config TEXT NOT NULL, -- Store config as JSON string
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`, (err) => {
        if (err) {
          console.error("Error creating table:", err.message);
          // Consider handling this error more gracefully
        } else {
          console.log("Table 'games' is ready.");
        }
      });
    }
  });
} catch (error) {
    console.error("Failed to initialize database connection:", error);
    process.exit(1);
}


// --- Directory Setup ---
const exportsDir = path.join(__dirname, 'exports');
const assetsDir = path.join(__dirname, 'assets'); // Assuming assets will be here

try {
    fs.ensureDirSync(exportsDir);
    fs.ensureDirSync(assetsDir);
    console.log(`Ensured directories exist: ${exportsDir}, ${assetsDir}`);
} catch (dirError) {
    console.error("Failed to ensure directories:", dirError);
    process.exit(1); // Exit if essential directories can't be created
}


// --- API Endpoints ---

// Endpoint for AI Scene Modification (Replaces /customize)
app.post('/ai-modify-scene', async (req, res) => {
  const { message, environmentName } = req.body;

  if (!message || !environmentName) {
    return res.status(400).json({ error: "Missing required fields: message, environmentName" });
  }

  console.log(`Received AI modification request for environment '${environmentName}': "${message}"`);

  // Construct scene file path
  const sceneFileName = `${environmentName.charAt(0).toUpperCase() + environmentName.slice(1)}Scene.html`;
  const sceneFilePath = path.join(__dirname, '..', 'src', 'scenes', sceneFileName);

  try {
    // 1. Read current scene file content
    const originalContent = await fs.readFile(sceneFilePath, 'utf-8');
    console.log(`Read original content from: ${sceneFilePath}`);

    // 2. Call OpenAI-compatible API
    const aiApiUrl = `${AI_BASE_URL}/chat/completions`;
    const apiPayload = {
      model: AI_MODEL_NAME,
      messages: [
        { role: "system", content: AI_SYSTEM_PROMPT },
        { role: "user", content: `File Content:\n\`\`\`html\n${originalContent}\n\`\`\`\n\nUser Request: ${message}` }
      ],
      // Add other parameters like temperature if needed
      // temperature: 0.7,
    };

    console.log(`Sending request to AI API: ${aiApiUrl}`);
    const aiResponse = await fetch(aiApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AI_API_KEY}` // Assuming Bearer token auth
      },
      body: JSON.stringify(apiPayload)
    });

    if (!aiResponse.ok) {
      const errorBody = await aiResponse.text();
      console.error(`AI API request failed with status ${aiResponse.status}: ${errorBody}`);
      throw new Error(`AI API request failed: ${aiResponse.statusText}`);
    }

    const aiResult = await aiResponse.json();
    console.log("Received raw AI response."); // Avoid logging potentially large content

    // 3. Extract modified code (assuming it's wrapped as requested)
    let modifiedContent = aiResult.choices?.[0]?.message?.content?.trim();
    if (!modifiedContent) {
        console.error("AI response did not contain expected content structure:", aiResult);
        throw new Error("Invalid AI response format: Missing content.");
    }

    // Extract content within ```html ... ```
    const match = modifiedContent.match(/```html\s*([\s\S]*?)\s*```/);
    if (!match || !match[1]) {
        console.error("AI response content was not wrapped in ```html blocks:", modifiedContent);
        throw new Error("Invalid AI response format: Content not wrapped correctly.");
    }
    modifiedContent = match[1].trim(); // Get the actual HTML content

    // 4. Create temporary backup and write modified content
    const tempBackupPath = path.join(path.dirname(sceneFilePath), `temp_${path.basename(sceneFilePath)}`);
    try {
      await fs.copyFile(sceneFilePath, tempBackupPath);
      console.log(`Created temporary backup: ${tempBackupPath}`);
      await fs.writeFile(sceneFilePath, modifiedContent, 'utf-8');
      console.log(`Overwrote original file with modified content: ${sceneFilePath}`);
    } catch (fileError) {
      console.error("Error during file backup/write:", fileError);
      // Attempt to restore original if backup exists and write failed? Or just error out? Error out for now.
      pendingModification = { originalPath: null, diffPatch: null }; // Clear state
      return res.status(500).json({ error: "Failed to backup or write scene file.", details: fileError.message });
    }

    // 5. Generate Diff Patch (after successful write)
    const diffPatch = createPatch(sceneFileName, originalContent, modifiedContent);
    console.log(`Generated diff patch for ${sceneFileName}`);

    // 6. Store minimal pending state (path for accept/reject reference)
    pendingModification = {
      originalPath: sceneFilePath,
      // newContent: null, // Not needed anymore
      diffPatch: diffPatch, // Keep for potential future use or logging? Or remove? Keep for now.
    };
    console.log(`Stored pending modification reference for ${sceneFilePath}`);

    // 7. Return diff to frontend
    res.json({ success: true, diff: diffPatch });

  } catch (error) {
    console.error("Error during AI scene modification:", error);
    // Clear pending state on error
    pendingModification = { originalPath: null, diffPatch: null };
    res.status(500).json({ error: "Failed to process AI modification request.", details: error.message });
  }
});

// Endpoint to accept pending AI changes
app.post('/ai-accept-changes', async (req, res) => {
  if (!pendingModification.originalPath) { // Check only for path now
    console.log("Accept request received, but no pending modification reference found.");
    return res.status(400).json({ error: "No pending modification reference to accept." });
  }

  const filePath = pendingModification.originalPath;
  const tempBackupPath = path.join(path.dirname(filePath), `temp_${path.basename(filePath)}`);

  console.log(`Accepting changes for: ${filePath}`);
  console.log(`Attempting to delete backup: ${tempBackupPath}`);

  try {
    // Main action is to delete the temporary backup
    await fs.remove(tempBackupPath); // fs-extra remove handles files safely
    console.log(`Successfully deleted temporary backup ${tempBackupPath}`);

    // Clear pending state
    pendingModification = { originalPath: null, diffPatch: null };

    res.json({ success: true, message: "Changes accepted. Backup deleted." });
  } catch (error) {
    console.error(`Error deleting temporary backup ${tempBackupPath}:`, error);
    // Don't clear pending state on error? Maybe the user needs to manually resolve. Let's clear for simplicity.
    pendingModification = { originalPath: null, diffPatch: null };
    res.status(500).json({ error: "Failed to delete temporary backup file.", details: error.message });
  }
});

// Endpoint to reject pending AI changes
app.post('/ai-reject-changes', async (req, res) => { // Make async
  if (!pendingModification.originalPath) {
    console.log("Reject request received, but no pending modification reference found.");
    // Still clear state just in case? Yes.
    pendingModification = { originalPath: null, diffPatch: null };
    return res.json({ success: true, message: "No pending changes found to reject." }); // Return success but indicate nothing happened
  }

  const filePath = pendingModification.originalPath;
  const tempBackupPath = path.join(path.dirname(filePath), `temp_${path.basename(filePath)}`);

  console.log(`Rejecting changes for: ${filePath}`);
  console.log(`Attempting to restore from backup: ${tempBackupPath}`);

  try {
    // 1. Delete the current (modified) file
    await fs.remove(filePath);
    console.log(`Deleted modified file: ${filePath}`);

    // 2. Rename the backup file back to the original name
    await fs.rename(tempBackupPath, filePath);
    console.log(`Restored original file from backup: ${tempBackupPath} -> ${filePath}`);

    // 3. Clear pending state
    pendingModification = { originalPath: null, diffPatch: null };

    res.json({ success: true, message: "Pending changes rejected and original file restored." });
  } catch (error) {
      console.error(`Error rejecting changes (deleting ${filePath} or renaming ${tempBackupPath}):`, error);
      // State might be inconsistent here. Clear pending state anyway.
      pendingModification = { originalPath: null, diffPatch: null };
      res.status(500).json({ error: "Failed to reject changes and restore original file.", details: error.message });
  }
});


// Endpoint to save game configuration
app.post('/save-game', (req, res) => {
  const { name, environment, config } = req.body;

  if (!name || !environment || !config) {
    return res.status(400).json({ error: "Missing required fields: name, environment, config" });
  }

  let configString;
  try {
      configString = JSON.stringify(config); // Store config as JSON string
  } catch (stringifyError) {
      console.error("Error stringifying config:", stringifyError);
      return res.status(400).json({ error: "Invalid configuration format." });
  }


  db.run(`INSERT INTO games (name, environment, config) VALUES (?, ?, ?)`,
    [name, environment, configString],
    function(err) { // Use function() to access this.lastID
      if (err) {
        console.error("Error saving game:", err.message);
        return res.status(500).json({ error: "Database error while saving game.", details: err.message });
      }
      console.log(`Game saved successfully with ID: ${this.lastID}`);
      res.json({ success: true, id: this.lastID });
    });
});

// Endpoint to retrieve all saved games (basic info)
app.get('/games', (req, res) => {
  db.all(`SELECT id, name, environment, created_at FROM games ORDER BY created_at DESC`, [], (err, rows) => {
    if (err) {
      console.error("Error fetching games:", err.message);
      return res.status(500).json({ error: "Database error while fetching games.", details: err.message });
    }
    res.json(rows);
  });
});

// Endpoint to export a game as a script
app.get('/export-game/:id', (req, res) => {
  const gameId = req.params.id;

  db.get(`SELECT name, config FROM games WHERE id = ?`, [gameId], (err, row) => {
    if (err) {
      console.error(`Error fetching game ${gameId} for export:`, err.message);
      return res.status(500).json({ error: "Database error while fetching game.", details: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: `Game with ID ${gameId} not found.` });
    }

    try {
      const config = JSON.parse(row.config);
      const scriptContent = `
// --- GameBuilder Exported Game ---
// Game Name: ${row.name || 'Untitled'}
// Exported: ${new Date().toISOString()}

// Basic Three.js setup (requires Three.js library)
// This is a simplified example and needs a proper runtime/loader

const gameConfig = ${JSON.stringify(config, null, 2)};

console.log("Game Configuration Loaded:");
console.log(gameConfig);

function setupScene() {
  // TODO: Implement scene reconstruction logic based on gameConfig
  console.log("Scene setup logic needs to be implemented here.");
}

// Basic execution check
if (typeof window !== 'undefined') {
  console.log("Running in browser context (requires Three.js)");
  // setupScene();
} else if (typeof process !== 'undefined') {
  console.log("Running in Node.js context (requires Three.js and potentially a headless GL context)");
  // setupScene();
}

console.log("--- End of Exported Script ---");
      `;

      const safeGameName = (row.name || 'game').replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filename = `game-${safeGameName}-${gameId}.js`;
      const exportPath = path.join(exportsDir, filename);

      fs.writeFileSync(exportPath, scriptContent);
      console.log(`Game script exported to: ${exportPath}`);

      res.json({ success: true, message: `Game exported successfully.`, filePath: `exports/${filename}` });

    } catch (parseError) {
      console.error(`Error processing config for game ${gameId}:`, parseError);
      return res.status(500).json({ error: "Error processing game configuration.", details: parseError.message });
    }
  });
});

// Endpoint to open a scene file in Brave browser (macOS specific)
app.post('/open-scene', (req, res) => {
  const { environmentName } = req.body;

  if (!environmentName) {
    return res.status(400).json({ error: "Missing required field: environmentName" });
  }

  // Construct the full path to the scene file relative to this server script
  const sceneFileName = `${environmentName.charAt(0).toUpperCase() + environmentName.slice(1)}Scene.html`;
  const sceneFilePath = path.join(__dirname, '..', 'src', 'scenes', sceneFileName); // Go up one level from src-tauri, then into src/scenes

  console.log(`Received request to open scene: ${environmentName}`);
  console.log(`Constructed file path: ${sceneFilePath}`);

  // Check if file exists before attempting to open
  fs.pathExists(sceneFilePath, (err, exists) => {
    if (err) {
        console.error(`Error checking file existence for ${sceneFilePath}:`, err);
        return res.status(500).json({ error: "Error checking file existence.", details: err.message });
    }
    if (!exists) {
        console.error(`Scene file not found: ${sceneFilePath}`);
        return res.status(404).json({ error: `Scene file not found: ${sceneFileName}` });
    }

    // Construct the command to open the file with Brave on macOS
    // Quote the path to handle spaces or special characters
    const command = `open -a "Brave Browser" "${sceneFilePath}"`;

    console.log(`Executing command: ${command}`);

    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing open command: ${error.message}`);
        console.error(`stderr: ${stderr}`);
        return res.status(500).json({ error: "Failed to open file.", details: error.message, stderr: stderr });
      }
      if (stderr) {
          console.warn(`Open command stderr: ${stderr}`);
          // Might not be a fatal error, but good to log
      }
      console.log(`Successfully executed open command for ${sceneFileName}. stdout: ${stdout}`);
      res.json({ success: true, message: `Attempted to open ${sceneFileName} in Brave Browser.` });
    });
  });
});


// --- Server Start ---
const server = app.listen(PORT, () => {
  console.log(`GameBuilder backend server running on http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing HTTP server and DB connection.');
  server.close(() => {
      console.log('HTTP server closed.');
      if (db) {
          db.close((err) => {
              if (err) {
                  console.error('Error closing database:', err.message);
              } else {
                  console.log('Database connection closed.');
              }
              process.exit(err ? 1 : 0);
          });
      } else {
          process.exit(0);
      }
  });
});