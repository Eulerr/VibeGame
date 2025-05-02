import gymnasium as gym
import time
import os
import shutil
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
# Removed CheckpointCallback, using custom callback now
from stable_baselines3.common.callbacks import BaseCallback

# Note: This script requires 'gymnasium', 'mujoco', 'stable-baselines3', and 'torch'.
# You can install them using: pip install gymnasium[mujoco] stable-baselines3[extra] torch

# --- Configuration ---
MODEL_NAME = "ppo_humanoid_continuous"
LOG_DIR = "logs_continuous/"
# Define path for the single, frequently updated model file
LATEST_MODEL_FILENAME = "latest_model.zip"
LATEST_MODEL_PATH = os.path.join(LOG_DIR, LATEST_MODEL_FILENAME)
LATEST_MODEL_TEMP_PATH = os.path.join(LOG_DIR, "latest_model_temp.zip")

# Use a very large number for effectively infinite training
TOTAL_TIMESTEPS = 100_000_000
N_ENVS = 12
LEARNING_RATE = 5e-4
# Save frequency: How many rollouts between saves.
# A rollout completes every n_steps * n_envs total steps.
# n_steps=2048, n_envs=12 => ~24576 steps per rollout.
SAVE_EVERY_N_ROLLOUTS = 5 # Save approx every 120k total steps

os.makedirs(LOG_DIR, exist_ok=True)

class AtomicSaveCallback(BaseCallback):
    """
    Callback for saving the model to a fixed path atomically,
    overwriting the previous file. Saves every N rollouts.
    """
    def __init__(self, save_path, temp_save_path, save_freq_rollouts=10, verbose=0):
        super().__init__(verbose)
        self.save_path = save_path
        self.temp_save_path = temp_save_path
        self.save_freq_rollouts = save_freq_rollouts
        self.rollouts_since_last_save = 0

    def _on_rollout_end(self) -> bool:
        """
        This method is called at the end of each rollout.
        """
        self.rollouts_since_last_save += 1
        if self.rollouts_since_last_save >= self.save_freq_rollouts:
            self.rollouts_since_last_save = 0 # Reset counter
            if self.verbose > 0:
                print(f"Saving latest model to {self.save_path} (Rollout {self.n_calls})")
            try:
                # Save to temporary file first
                self.model.save(self.temp_save_path)
                # Atomically replace the old file with the new one
                # os.replace is generally atomic on POSIX and Windows
                os.replace(self.temp_save_path, self.save_path)
                if self.verbose > 1:
                    print(f"Successfully saved latest model to {self.save_path}")
            except Exception as e:
                print(f"Error saving model: {e}")
                # Clean up temp file if it exists
                if os.path.exists(self.temp_save_path):
                    os.remove(self.temp_save_path)
        return True # Continue training

    def _on_step(self) -> bool:
        # Required by BaseCallback, but logic is in _on_rollout_end
        return True


def train_humanoid_continuously():
    """Trains the PPO agent continuously, saving the latest model periodically."""
    print(f"Starting continuous training (target: {TOTAL_TIMESTEPS} timesteps)...")
    print(f"Latest model will be saved approx every {SAVE_EVERY_N_ROLLOUTS} rollouts to {LATEST_MODEL_PATH}")

    # Create vectorized environments (NO RENDER)
    env = make_vec_env("Humanoid-v5", n_envs=N_ENVS, vec_env_cls=DummyVecEnv)

    # Custom callback for atomic saving
    atomic_save_callback = AtomicSaveCallback(
        save_path=LATEST_MODEL_PATH,
        temp_save_path=LATEST_MODEL_TEMP_PATH,
        save_freq_rollouts=SAVE_EVERY_N_ROLLOUTS,
        verbose=1
    )

    # Define the PPO model
    # Check if the latest_model file exists to resume training
    if os.path.exists(LATEST_MODEL_PATH):
        print(f"Resuming training from latest model: {LATEST_MODEL_PATH}")
        # Load the last saved model
        model = PPO.load(LATEST_MODEL_PATH, env=env, tensorboard_log=LOG_DIR)
        # Ensure the environment is correctly set after loading
        model.set_env(env)
    else:
        print("No latest model found, starting new training.")
        model = PPO("MlpPolicy",
                    env,
                    verbose=1,
                    tensorboard_log=LOG_DIR,
                    learning_rate=LEARNING_RATE,
                    n_steps=2048,
                    batch_size=64 * N_ENVS,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    clip_range=0.2,
                    ent_coef=0.0,
                    vf_coef=0.5,
                    max_grad_norm=0.5
                    )

    try:
        # Train the agent indefinitely
        model.learn(total_timesteps=TOTAL_TIMESTEPS,
                    tb_log_name=MODEL_NAME,
                    callback=atomic_save_callback,
                    reset_num_timesteps=not os.path.exists(LATEST_MODEL_PATH)) # Reset counter only if starting fresh

        # Save the final model (might not be reached)
        final_save_path = os.path.join(LOG_DIR, MODEL_NAME + "_final.zip")
        model.save(final_save_path)
        print(f"Training finished (or reached limit). Final model saved to {final_save_path}")

    except KeyboardInterrupt:
        print("\nTraining interrupted by user. Saving final model...")
        interrupt_save_path = os.path.join(LOG_DIR, MODEL_NAME + "_interrupted.zip")
        # Also save to the latest path one last time
        try:
            model.save(LATEST_MODEL_TEMP_PATH)
            os.replace(LATEST_MODEL_TEMP_PATH, LATEST_MODEL_PATH)
            print(f"Saved final state to {LATEST_MODEL_PATH}")
            # Optionally save a separate interrupted file
            # shutil.copyfile(LATEST_MODEL_PATH, interrupt_save_path)
            # print(f"Copied final state to {interrupt_save_path}")
        except Exception as e:
             print(f"Error saving final model on interrupt: {e}")

    finally:
        env.close()
        print("Training environment closed.")


if __name__ == "__main__":
    try:
        train_humanoid_continuously()
    except gym.error.DependencyNotInstalled as e:
        print(f"Error: {e}")
        print("Please make sure you have installed the necessary dependencies.")
        print("Try running: pip install gymnasium[mujoco] stable-baselines3[extra] torch")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Script finished.")