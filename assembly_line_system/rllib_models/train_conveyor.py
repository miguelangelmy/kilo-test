"""
Training script for conveyor belt agents using RLlib.
"""

import os
import subprocess
import ray
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv
from assembly_line_system.rllib_models.conveyor_model import ConveyorModel

def train_conveyor_agent():
    """
    Train a conveyor belt agent using RLlib via CLI.
    """
    # Register custom model
    from ray.rllib.models import ModelCatalog
    ModelCatalog.register_custom_model("conveyor_model", ConveyorModel)

    # Define training configuration as a dictionary and write it as JSON
    config = {
        "env": "AssemblyLineEnv",
        "model": {
            "custom_model": "conveyor_model",
            "custom_model_config": {}
        },
        "num_workers": 2,
        "train_batch_size": 1000,
        "gamma": 0.99,
        "lambd": 0.95,  # Changed from "lambda" to avoid Python keyword conflict
        "entropy_coeff": 0.01,
        "learning_starts": 1000,
        # Add environment-specific configuration
        "env_config": {
            "num_conveyors": 2,
            "num_cranes": 1,
            "num_robotic_arms": 2,
            "num_assembly_stations": 1
        }
    }

    # Write config to a temporary file
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        config_file = f.name

    try:
        # Run RLlib training via CLI
        cmd = [
            "python", "-m", "ray.rllib.train",
            "--algo", "DQN",
            "--env", "AssemblyLineEnv",
            "--config", config_file,
            "--run", "DQN",
            "--stop", "training_iteration:10"  # Reduced for testing
        ]

        print("Running RLlib training with command:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode != 0:
            raise RuntimeError(f"RLlib training failed with return code {result.returncode}")

    finally:
        # Clean up temp file
        os.unlink(config_file)

def train_conveyor_agent_api():
    """
    Train a conveyor belt agent using RLlib API (alternative to CLI).
    This provides better error handling and debugging capabilities.
    """
    try:
        # Initialize Ray
        ray.init()
        
        # Register custom model
        from ray.rllib.models import ModelCatalog
        ModelCatalog.register_custom_model("conveyor_model", ConveyorModel)

        # Define training configuration
        config = {
            "env": AssemblyLineEnv,
            "model": {
                "custom_model": "conveyor_model",
                "custom_model_config": {}
            },
            "num_workers": 2,
            "train_batch_size": 1000,
            "gamma": 0.99,
            "lambd": 0.95,  # Changed from "lambda" to avoid Python keyword conflict
            "entropy_coeff": 0.01,
            "learning_starts": 1000,
            # Add environment-specific configuration
            "env_config": {
                "num_conveyors": 2,
                "num_cranes": 1,
                "num_robotic_arms": 2,
                "num_assembly_stations": 1
            }
        }

        # Create trainer
        from ray.rllib.agents.dqn import DQNTrainer
        trainer = DQNTrainer(config=config)

        # Training loop
        print("Starting training...")
        for i in range(10):  # Train for 10 iterations
            result = trainer.train()
            
            print(f"Iteration {i + 1}:")
            print(f"  Episode reward mean: {result['episode_reward_mean']}")
            print(f"  Episode len mean: {result['episode_len_mean']}")
            print(f"  Time total: {result['time_total_s']:.2f}s")
            
            # Check for convergence
            if result.get('episode_reward_mean', 0) > 100:
                print("Training converged!")
                break

        # Save the trained model
        checkpoint_path = trainer.save()
        print(f"Model saved to: {checkpoint_path}")
        
        return trainer

    except Exception as e:
        print(f"Training failed with error: {e}")
        raise
    finally:
        # Shutdown Ray
        ray.shutdown()

def main():
    """Main training function."""
    print("Choose training method:")
    print("1. CLI-based training")
    print("2. API-based training (recommended)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        train_conveyor_agent()
    elif choice == "2":
        try:
            trainer = train_conveyor_agent_api()
            print("Training completed successfully!")
        except Exception as e:
            print(f"Training failed: {e}")
    else:
        print("Invalid choice. Running API-based training by default.")
        try:
            trainer = train_conveyor_agent_api()
            print("Training completed successfully!")
        except Exception as e:
            print(f"Training failed: {e}")

if __name__ == "__main__":
    main()