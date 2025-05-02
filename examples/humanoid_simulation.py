import gymnasium as gym
import time
import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv

# Note: This script requires 'gymnasium', 'mujoco', 'stable-baselines3', and 'torch'.
# You can install them using: pip install gymnasium[mujoco] stable-baselines3[extra] torch

# --- Configuration ---
MODEL_NAME = "ppo_humanoid_stand"
LOG_DIR = "logs/"
MODEL_PATH = os.path.join(LOG_DIR, MODEL_NAME)
TOTAL_TIMESTEPS = 500_000 # Reduced total steps as requested
N_ENVS = 12 # Increased parallel environments for M4 Max
LEARNING_RATE = 5e-4 # Increased learning rate (caution: may affect stability)
TRAIN_MODEL = True # Set to False to load and run a pre-trained model
RUN_TRAINED_MODEL = True # Set to True to watch the trained agent

os.makedirs(LOG_DIR, exist_ok=True)

def train_humanoid():
    """Trains the PPO agent for the Humanoid environment."""
    print(f"Starting training for {TOTAL_TIMESTEPS} timesteps...")
    # Create vectorized environments for parallel training
    # Using DummyVecEnv as SubprocVecEnv might have issues on some systems (macOS)
    env = make_vec_env("Humanoid-v5", n_envs=N_ENVS, vec_env_cls=DummyVecEnv)

    # Define the PPO model
    model = PPO("MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=LOG_DIR,
                learning_rate=LEARNING_RATE,
                n_steps=2048, # Number of steps to run for each environment per update
                batch_size=64 * N_ENVS, # Mini-batch size
                n_epochs=10, # Number of epochs when optimizing the surrogate loss
                gamma=0.99, # Discount factor
                gae_lambda=0.95, # Factor for trade-off of bias vs variance for Generalized Advantage Estimator
                clip_range=0.2, # Clipping parameter PPO
                ent_coef=0.0, # Entropy coefficient
                vf_coef=0.5, # Value function coefficient
                max_grad_norm=0.5 # Max value for gradient clipping
                )

    # Train the agent
    model.learn(total_timesteps=TOTAL_TIMESTEPS, tb_log_name=MODEL_NAME)

    # Save the trained model
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    env.close()
    return model

def run_humanoid(model_path):
    """Loads a trained model and runs the simulation with rendering."""
    print(f"Loading model from {model_path} and running simulation...")
    # Create a single environment with rendering
    env = gym.make("Humanoid-v5", render_mode="human")
    model = PPO.load(model_path, env=env)

    obs, info = env.reset()
    steps = 0
    episode_count = 0
    try:
        print("Running trained model. Press Ctrl+C in the terminal to stop.")
        while True: # Run indefinitely until interrupted
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
            # Optional delay
            # time.sleep(0.01)
            if terminated or truncated:
                episode_count += 1
                print(f"Episode {episode_count} finished after {steps} steps.")
                obs, info = env.reset()
                steps = 0
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    finally:
        env.close()
        print("Rendered environment closed.")

if __name__ == "__main__":
    try:
        if TRAIN_MODEL:
            train_humanoid()

        if RUN_TRAINED_MODEL:
            if os.path.exists(MODEL_PATH + ".zip"):
                 run_humanoid(MODEL_PATH)
            else:
                 print(f"Error: Trained model not found at {MODEL_PATH}.zip. Set TRAIN_MODEL=True to train first.")

    except gym.error.DependencyNotInstalled as e:
        print(f"Error: {e}")
        print("Please make sure you have installed the necessary dependencies.")
        print("Try running: pip install gymnasium[mujoco] stable-baselines3[extra] torch")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Script finished.")