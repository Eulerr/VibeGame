# VibeGame Examples

This directory contains example reinforcement learning scripts using Gymnasium and Stable Baselines3 to train and visualize a Humanoid agent.

## Setup

1.  **Navigate to the examples directory:**
    ```bash
    cd examples
    ```

2.  **Create and activate a Python virtual environment:**
    > hint... you may want to use `uv` to set this up as its way cleaner and
    -   **macOS / Linux (bash/zsh):**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    -   **Windows (PowerShell):**
        ```powershell
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        ```
        *(Note: You might need to adjust your execution policy on Windows: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Examples

Make sure your virtual environment is activated before running any scripts.

### 1. `humanoid_simulation.py`

This script trains a PPO agent for a fixed number of timesteps (`TOTAL_TIMESTEPS`) to make the Humanoid stand up. After training (if `TRAIN_MODEL` is `True` in the script), it saves the model to `logs/` and then runs the trained agent with rendering (if `RUN_TRAINED_MODEL` is `True`).

*   **To run:**
    ```bash
    python humanoid_simulation.py
    ```
*   **Configuration:** You can modify `TRAIN_MODEL`, `RUN_TRAINED_MODEL`, `TOTAL_TIMESTEPS`, etc., directly within the script.

### 2. `humanoid_train_continuous.py`

This script trains a PPO agent continuously (or until interrupted). It periodically saves the latest version of the model atomically to `logs_continuous/latest_model.zip`. This script is designed to be run in the background or for long training sessions. It can be stopped with `Ctrl+C`, which will trigger a final save. If restarted, it will attempt to resume training from `latest_model.zip`.

*   **To run:**
    ```bash
    python humanoid_train_continuous.py
    ```
*   **Output:** Training logs and TensorBoard data go to `logs_continuous/`. The latest model is saved as `logs_continuous/latest_model.zip`.

### 3. `humanoid_viewer.py`

This script acts as a live viewer for the model being trained by `humanoid_train_continuous.py`. It periodically checks for updates to `logs_continuous/latest_model.zip`. If a newer model is found, it loads it and continues rendering the agent's behavior using the latest policy.

*   **Prerequisite:** `humanoid_train_continuous.py` should be running, or have run previously to create the `latest_model.zip` file.
*   **To run:**
    ```bash
    python humanoid_viewer.py
    ```
*   **Behavior:** Opens a rendering window showing the Humanoid agent. It will automatically update the agent's policy whenever the `latest_model.zip` file is updated by the training script. Press `Ctrl+C` to stop the viewer.