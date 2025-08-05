"""
Training script for multi-agent assembly line system using RLlib.
"""

import os
import ray
from typing import Dict, Any

def train_multiagent_system():
    """
    Train the complete multi-agent assembly line system using RLlib API.
    
    This function trains all agent types (conveyor, crane, robotic arm, assembly station)
    in a coordinated manner to optimize the entire assembly line.
    """
    try:
        # Initialize Ray
        ray.init()
        
        # Register all custom models
        from ray.rllib.models import ModelCatalog
        
        from assembly_line_system.rllib_models.conveyor_model import ConveyorModel
        from assembly_line_system.rllib_models.crane_model import CraneModel
        from assembly_line_system.rllib_models.robotic_arm_model import RoboticArmModel
        from assembly_line_system.rllib_models.assembly_station_model import AssemblyStationModel
        
        ModelCatalog.register_custom_model("conveyor_model", ConveyorModel)
        ModelCatalog.register_custom_model("crane_model", CraneModel)
        ModelCatalog.register_custom_model("robotic_arm_model", RoboticArmModel)
        ModelCatalog.register_custom_model("assembly_station_model", AssemblyStationModel)

        # Define multi-agent configuration
        config = {
            "env": "assembly_line_env",
            
            # Multi-agent setup
            "multiagent": {
                "policies": {
                    "conveyor_policy": (
                        None,  # Use default loss
                        "assembly_line_env:observation_space", 
                        "assembly_line_env:action_space",
                        {
                            "custom_model": "conveyor_model",
                            "custom_model_config": {}
                        }
                    ),
                    "crane_policy": (
                        None,  # Use default loss
                        "assembly_line_env:observation_space", 
                        "assembly_line_env:action_space",
                        {
                            "custom_model": "crane_model",
                            "custom_model_config": {}
                        }
                    ),
                    "robotic_arm_policy": (
                        None,  # Use default loss
                        "assembly_line_env:observation_space", 
                        "assembly_line_env:action_space",
                        {
                            "custom_model": "robotic_arm_model",
                            "custom_model_config": {}
                        }
                    ),
                    "assembly_station_policy": (
                        None,  # Use default loss
                        "assembly_line_env:observation_space", 
                        "assembly_line_env:action_space",
                        {
                            "custom_model": "assembly_station_model",
                            "custom_model_config": {}
                        }
                    )
                },
                
                # Policy mapping function
                "policy_mapping_fn": lambda agent_id, episode, **kwargs: {
                    "conveyor_0": "conveyor_policy",
                    "crane_0": "crane_policy", 
                    "robotic_arm_0": "robotic_arm_policy",
                    "robotic_arm_1": "robotic_arm_policy",
                    "assembly_station_0": "assembly_station_policy"
                }.get(agent_id, "conveyor_policy"),
                
                # Distribution strategy
                "policy_mapping_fn": lambda agent_id, episode, **kwargs: {
                    "conveyor_0": "conveyor_policy",
                    "crane_0": "crane_policy", 
                    "robotic_arm_0": "robotic_arm_policy",
                    "robotic_arm_1": "robotic_arm_policy",
                    "assembly_station_0": "assembly_station_policy"
                }.get(agent_id, "conveyor_policy")
            },
            
            # Environment configuration
            "env_config": {
                "num_conveyors": 1,
                "num_cranes": 1,
                "num_robotic_arms": 2,
                "num_assembly_stations": 1
            },
            
            # Training parameters
            "train_batch_size": 4000,
            "num_workers": 4,
            "gamma": 0.99,
            "lambd": 0.95,  # GAE lambda
            "entropy_coeff": 0.01,
            "learning_starts": 2000,
            "lr": 0.0003,
            
            # Model parameters
            "model": {
                "custom_model": "conveyor_model",  # Default model
                "custom_model_config": {},
                "use_lstm": False,
                "max_seq_len": 20
            },
            
            # Evaluation settings
            "evaluation_interval": 10,
            "evaluation_num_episodes": 5,
            
            # Checkpointing
            "checkpoint_freq": 50,
            "checkpoint_at_end": True
        }

        # Create trainer using PPO for multi-agent training
        from ray.rllib.agents.ppo import PPOTrainer
        trainer = PPOTrainer(config=config)

        # Training loop with detailed monitoring
        print("Starting multi-agent training...")
        
        for i in range(100):  # Train for 100 iterations
            result = trainer.train()
            
            print(f"\n=== Training Iteration {i + 1} ===")
            print(f"Total Reward: {result['episode_reward_mean']:.2f}")
            
            # Print individual policy performance
            for policy_id, stats in result.get('policy_reward_mean', {}).items():
                print(f"  {policy_id}: {stats:.2f}")
                
            print(f"Episode Length: {result['episode_len_mean']:.2f}")
            print(f"Time Total: {result['time_total_s']:.2f}s")
            
            # Check for convergence
            if result.get('episode_reward_mean', 0) > 500:
                print("Training converged!")
                break
                
            # Print progress every 10 iterations
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/100 iterations completed")

        # Save the trained model
        checkpoint_path = trainer.save()
        print(f"\nMulti-agent model saved to: {checkpoint_path}")
        
        # Print final statistics
        print("\n=== Final Training Statistics ===")
        for key, value in result.items():
            if isinstance(value, (int, float)):
                print(f"{key}: {value:.4f}")
        
        return trainer

    except Exception as e:
        print(f"Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Shutdown Ray
        ray.shutdown()

def train_individual_agents():
    """
    Train individual agent types separately for comparison and debugging.
    """
    agents_config = {
        "conveyor": {
            "model_class": "assembly_line_system.rllib_models.conveyor_model.ConveyorModel",
            "env_config": {"num_conveyors": 1, "num_cranes": 0, "num_robotic_arms": 0, "num_assembly_stations": 0}
        },
        "crane": {
            "model_class": "assembly_line_system.rllib_models.crane_model.CraneModel", 
            "env_config": {"num_conveyors": 0, "num_cranes": 1, "num_robotic_arms": 0, "num_assembly_stations": 0}
        },
        "robotic_arm": {
            "model_class": "assembly_line_system.rllib_models.robotic_arm_model.RoboticArmModel",
            "env_config": {"num_conveyors": 0, "num_cranes": 0, "num_robotic_arms": 1, "num_assembly_stations": 0}
        },
        "assembly_station": {
            "model_class": "assembly_line_system.rllib_models.assembly_station_model.AssemblyStationModel",
            "env_config": {"num_conveyors": 0, "num_cranes": 0, "num_robotic_arms": 0, "num_assembly_stations": 1}
        }
    }
    
    trained_agents = {}
    
    for agent_name, config in agents_config.items():
        print(f"\n=== Training {agent_name} agent ===")
        
        try:
            # Initialize Ray
            ray.init(ignore_reinit_error=True)
            
            # Register model
            from ray.rllib.models import ModelCatalog
            
            if agent_name == "conveyor":
                from assembly_line_system.rllib_models.conveyor_model import ConveyorModel
                ModelCatalog.register_custom_model("custom_model", ConveyorModel)
            elif agent_name == "crane":
                from assembly_line_system.rllib_models.crane_model import CraneModel
                ModelCatalog.register_custom_model("custom_model", CraneModel)
            elif agent_name == "robotic_arm":
                from assembly_line_system.rllib_models.robotic_arm_model import RoboticArmModel
                ModelCatalog.register_custom_model("custom_model", RoboticArmModel)
            elif agent_name == "assembly_station":
                from assembly_line_system.rllib_models.assembly_station_model import AssemblyStationModel
                ModelCatalog.register_custom_model("custom_model", AssemblyStationModel)

            # Create trainer configuration
            trainer_config = {
                "env": "assembly_line_env",
                "model": {
                    "custom_model": "custom_model",
                    "custom_model_config": {}
                },
                "env_config": config["env_config"],
                "train_batch_size": 1000,
                "num_workers": 2,
                "gamma": 0.99,
                "lambd": 0.95,
                "entropy_coeff": 0.01,
                "learning_starts": 500
            }

            # Create and train agent
            from ray.rllib.agents.ppo import PPOTrainer
            trainer = PPOTrainer(config=trainer_config)
            
            # Train for a few iterations
            for i in range(20):
                result = trainer.train()
                
                if (i + 1) % 5 == 0:
                    print(f"  Iteration {i + 1}: Reward = {result['episode_reward_mean']:.2f}")
            
            # Save trained agent
            checkpoint_path = trainer.save()
            print(f"  {agent_name} model saved to: {checkpoint_path}")
            
            trained_agents[agent_name] = trainer
            
        except Exception as e:
            print(f"  Failed to train {agent_name}: {e}")
        finally:
            # Shutdown Ray
            ray.shutdown()
    
    return trained_agents

def main():
    """Main training function with menu options."""
    print("=== Multi-Agent Assembly Line Training ===")
    print("\nChoose training mode:")
    print("1. Full multi-agent training (recommended)")
    print("2. Individual agent training")
    print("3. Both (multi-agent first, then individual)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        try:
            trainer = train_multiagent_system()
            print("\nMulti-agent training completed successfully!")
        except Exception as e:
            print(f"\nTraining failed: {e}")
            
    elif choice == "2":
        try:
            trained_agents = train_individual_agents()
            print(f"\nIndividual agent training completed! Trained {len(trained_agents)} agents.")
        except Exception as e:
            print(f"\nTraining failed: {e}")
            
    elif choice == "3":
        try:
            print("\nStarting with full multi-agent training...")
            trainer = train_multiagent_system()
            
            print("\nNow training individual agents for comparison...")
            trained_agents = train_individual_agents()
            
            print(f"\nAll training completed! Multi-agent model + {len(trained_agents)} individual agents.")
        except Exception as e:
            print(f"\nTraining failed: {e}")
            
    else:
        print("Invalid choice. Please run the script again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()