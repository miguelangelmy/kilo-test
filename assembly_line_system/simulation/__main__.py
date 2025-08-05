"""
Main entry point for the assembly line simulation.
"""

import gymnasium as gym
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv

def main():
    """Run a basic simulation of the assembly line environment."""
    print("Starting Assembly Line Simulation...")

    # Create environment
    env = AssemblyLineEnv()

    # Reset environment
    observation = env.reset()
    print("Initial observation:")
    print(observation)

    # Run for a few time steps
    for step in range(5):
        print(f"\n--- Time Step {step} ---")

        # Take random actions for demonstration
        actions = {
            'conveyor_1': env.action_space.sample(),
            'crane_1': env.action_space.sample(),
            'robotic_arm_1': env.action_space.sample(),
            'assembly_station_1': env.action_space.sample()
        }

        # Execute actions
        observation, rewards, done, info = env.step(actions)

        print(f"Actions: {actions}")
        print(f"Rewards: {rewards}")
        print(f"Done: {done}")

        # Render environment
        env.render()

        if done:
            print("Simulation completed!")
            break

    print("\nSimulation finished.")

if __name__ == "__main__":
    main()