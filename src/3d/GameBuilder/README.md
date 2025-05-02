# GameBuilder - AI-Driven 3D Game Creation Tool

GameBuilder is a desktop application built with Tauri, React, and Three.js that allows users to create simple 3D games by selecting predefined environments and customizing them using an AI-powered chat interface.

## Features

-   **Environment Selection**: Choose from 8 predefined 3D game environments (Shooter, Parkour, Sandbox, etc.).
-   **AI Customization**: Use a chat window to add or modify game elements (e.g., "add a tree", "make the player faster").
-   **Live Rendering**: See changes reflected instantly in the 3D game view powered by Three.js and @react-three/fiber.
-   **Save & Export**: Save game configurations to a local SQLite database and export them as runnable JavaScript scripts.
-   **Cross-Platform**: Built with Tauri for macOS, Windows, and Linux support.

## Project Structure

```
GameBuilder/
├── dist/                     # Frontend build output (generated)
├── node_modules/             # Node.js dependencies (generated)
├── public/                   # Static assets for Vite
├── src/                      # React frontend source
│   ├── components/           # React UI components
│   ��   ├── EnvironmentSelector.jsx
│   │   ├── GameCanvas.jsx
│   │   └── ChatWindow.jsx
│   ├── scenes/               # Three.js scene components
│   │   ├── ShooterScene.js
│   │   ├── ParkourScene.js
│   │   └── ... (6 more)
│   ├── App.jsx               # Main application component
│   ├── main.jsx              # React entry point
│   ��── styles.css            # Tailwind CSS styles
├── src-tauri/                # Tauri Rust backend and Node.js server
│   ├── assets/               # Placeholder for game assets (models, textures)
│   │   └── placeholder.txt
│   ├── exports/              # Exported game scripts (generated)
│   ├── src/                  # Rust source (default Tauri)
│   │   └── main.rs
│   ├── target/               # Rust build output (generated)
│   ├── build.rs              # Rust build script (default Tauri)
│   ��── Cargo.lock            # Rust dependencies lock file
│   ├── Cargo.toml            # Rust dependencies manifest
│   ├── database.db           # SQLite database file
│   ├── server.js             # Node.js backend server
│   └── tauri.conf.json       # Tauri configuration
├── .gitignore
├── index.html                # Main HTML file for Vite
├── package-lock.json         # npm dependencies lock file
├── package.json              # npm project manifest
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.js        # Tailwind CSS configuration
��── vite.config.js            # Vite configuration
```

## Prerequisites

-   Node.js (v16 or later recommended)
-   npm (usually comes with Node.js)
-   Rust and Tauri prerequisites (see [Tauri prerequisites guide](https://tauri.app/v1/guides/getting-started/prerequisites))

## Setup and Installation

1.  **Clone the repository (if applicable) or navigate into the `GameBuilder` directory.**
2.  **Install Dependencies**:
    *   **IMPORTANT**: The automatic dependency installation was interrupted during setup. Please run the following command manually:
        ```bash
        npm install three @react-three/fiber@^8.0.0 @react-three/drei@^9.0.0 axios tailwindcss postcss autoprefixer express sqlite3 node-fetch@^2 fs-extra
        ```
    *   If the above fails due to peer dependency issues, you might need to try:
        ```bash
        npm install three @react-three/fiber@^8.0.0 @react-three/drei@^9.0.0 axios tailwindcss postcss autoprefixer express sqlite3 node-fetch@^2 fs-extra --legacy-peer-deps
        ```
    *   Install Tauri CLI (if not already installed globally):
        ```bash
        npm install -g @tauri-apps/cli
        ```
    *   **Rename Scene Files**: The scene files in `src/scenes/` were created with `.js` extensions but contain JSX. You **must** rename them to use the `.jsx` extension:
        ```bash
        # Example for one file (repeat for all 8 scenes):
        mv src/scenes/ShooterScene.js src/scenes/ShooterScene.jsx
        mv src/scenes/ParkourScene.js src/scenes/ParkourScene.jsx
        # ... and so on for Sandbox, Puzzle, Racing, Adventure, Survival, RPG
        ```

## Running the Application

1.  **Start the Backend Server**:
    *   Open a terminal in the `GameBuilder` directory.
    *   Run the Node.js server:
        ```bash
        node src-tauri/server.js
        ```
    *   You should see output indicating the server is running on port 3001 and the database is connected. Keep this terminal running.

2.  **Start the Tauri Development App**:
    *   Open a *second* terminal in the `GameBuilder` directory.
    *   Run the Tauri development command:
        ```bash
        npm run tauri dev
        ```
    *   This will build the frontend, compile the Rust backend (first time might take longer), and launch the desktop application.

## Building the Application

1.  **Ensure the backend server (`server.js`) is NOT running.** The build process bundles the application.
2.  **Run the build command**:
    ```bash
    npm run tauri build
    ```
3.  The distributable application (e.g., `.app`, `.exe`, `.deb`) will be located in `GameBuilder/src-tauri/target/release/bundle/`.

## Usage

1.  Launch the application (`npm run tauri dev` or the built executable).
2.  Select one of the 8 environment tiles.
3.  The 3D scene for the selected environment will load in the center panel.
4.  Use the chat window on the right to type commands (e.g., "add tree").
5.  Observe the scene update based on the (mock) AI response.
6.  Click the "Save Game" button in the header, enter a name, and the configuration will be saved to the database via the backend server.
7.  (Export functionality is basic - it saves a script file in `src-tauri/exports/` but requires manual retrieval and a proper runtime).

## Troubleshooting

-   **Dependency Errors**: Ensure you ran `npm install` successfully (see Setup section). Try deleting `node_modules` and `package-lock.json` and running `npm install` again.
-   **Server Connection Error**: Make sure the Node.js server (`node src-tauri/server.js`) is running in a separate terminal before starting the Tauri app (`npm run tauri dev`). Check the console for errors from `server.js`.
-   **Tauri Build Issues**: Ensure all Tauri prerequisites for your OS are installed correctly. Check the Tauri documentation.
-   **Missing Assets**: This version uses placeholder 3D objects. Actual 3D models (`.glb`, `.gltf`) should be placed in `src-tauri/assets/` and loaded appropriately in the scene components.

## Notes

-   The AI integration currently uses mock responses in `server.js`. Replace the mock logic with actual calls to the xAI API (or another service) as needed.
-   The game export functionality is very basic and generates a script with the configuration. A full runtime would be needed to execute these scripts standalone.
-   3D assets are not included; placeholder shapes are used.
