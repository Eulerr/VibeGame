import gymnasium as gym
import time
import os
from stable_baselines3 import PPO
import torch # Ensure torch is imported if needed by the model policy

# --- Configuration ---
LOG_DIR = "logs_continuous/" # Should match the training script's log dir
LATEST_MODEL_FILENAME = "latest_model.zip"
LATEST_MODEL_PATH = os.path.join(LOG_DIR, LATEST_MODEL_FILENAME)
CHECK_INTERVAL_SECONDS = 5 # How often to check for a new model file
RENDER_FPS = 60 # Target FPS for rendering

def run_viewer():
    """Loads the latest model periodically and runs the simulation with rendering."""
    print("Starting viewer...")
    print(f"Watching for model updates at: {LATEST_MODEL_PATH}")
    print(f"Checking every {CHECK_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")

    env = None
    model = None
    last_load_time = 0
    last_render_time = time.time()

    try:
        while True:
            current_time = time.time()
            model_updated = False

            # Check if the model file exists and has been modified
            if os.path.exists(LATEST_MODEL_PATH):
                try:
                    mod_time = os.path.getmtime(LATEST_MODEL_PATH)
                    if mod_time > last_load_time:
                        print(f"\nDetected updated model (Timestamp: {mod_time}). Loading...")
                        # Close existing env before loading new model if necessary
                        if env is not None:
                            env.close()
                            env = None # Ensure it's recreated

                        # Create environment only when needed
                        if env is None:
                             env = gym.make("Humanoid-v5", render_mode="human")

                        # Load the latest model
                        model = PPO.load(LATEST_MODEL_PATH, env=env)
                        print("Model loaded successfully.")
                        last_load_time = mod_time
                        model_updated = True
                        # Reset environment with the new model context
                        obs, info = env.reset()

                except FileNotFoundError:
                    # Model might have been deleted between check and load
                    print(f"Warning: Model file {LATEST_MODEL_PATH} disappeared during load attempt.")
                    model = None # Invalidate current model
                    if env is not None:
                        env.close()
                        env = None
                except Exception as e:
                    print(f"\nError loading model: {e}")
                    print("Will retry loading on next check.")
                    model = None # Invalidate current model
                    if env is not None:
                        env.close()
                        env = None
                    # Wait before next check to avoid spamming errors
                    time.sleep(CHECK_INTERVAL_SECONDS)
                    continue

            # Run simulation step if model and env are loaded
            if model is not None and env is not None:
                try:
                    # Control render speed
                    time_since_last_render = current_time - last_render_time
                    if time_since_last_render < 1.0 / RENDER_FPS:
                        time.sleep((1.0 / RENDER_FPS) - time_since_last_render)
                    last_render_time = time.time() # Update after potential sleep

                    action, _states = model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, info = env.step(action)

                    if terminated or truncated:
                        # print("Episode finished. Resetting environment.") # Optional: less verbose
                        obs, info = env.reset()

                except Exception as e:
                    # Handle potential errors during env.step or predict
                    print(f"\nError during simulation step: {e}")
                    print("Resetting environment and attempting to reload model on next cycle.")
                    model = None # Force reload on next cycle
                    if env is not None:
                        env.close()
                        env = None
                    time.sleep(CHECK_INTERVAL_SECONDS) # Wait before retrying
                    continue
            elif not os.path.exists(LATEST_MODEL_PATH):
                 # If model file doesn't exist yet, just wait
                 print(f"Waiting for model file to appear at {LATEST_MODEL_PATH}...", end='\r')
                 time.sleep(CHECK_INTERVAL_SECONDS)


            # Wait before the next check if no model update happened
            if not model_updated and model is None: # Only sleep if no model is loaded
                 time.sleep(CHECK_INTERVAL_SECONDS)
            elif not model_updated and model is not None:
                 # If model is loaded and running, check more frequently or rely on FPS limiter
                 time.sleep(0.1) # Short sleep to prevent busy-waiting


    except KeyboardInterrupt:
        print("\nViewer stopped by user.")
    finally:
        if env is not None:
            env.close()
            print("Viewer environment closed.")

if __name__ == "__main__":
    # Add check for dependencies?
    run_viewer()