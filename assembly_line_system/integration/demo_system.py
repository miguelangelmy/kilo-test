"""
Demo script for the complete assembly line system integration.

This script demonstrates how the environment, agents, and models work together
in a coordinated multi-agent system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv

class SimpleAgentController:
    """
    Simple controller that maps observations to actions for each agent type.
    
    This is a basic rule-based controller that demonstrates the integration
    between environment and agents. In a real implementation, this would be
    replaced by RL-trained policies.
    """
    
    def __init__(self, env):
        self.env = env
        self.station_types = []
        
        # Determine station types based on environment configuration
        all_stations = (env.conveyor_stations + env.crane_stations + 
                       env.robotic_arm_stations + env.assembly_stations)
        
        for station in all_stations:
            if hasattr(station, 'type'):
                self.station_types.append(station.type)
    
    def get_actions(self, observation):
        """
        Convert observation to actions for each station.
        
        Args:
            observation: Current environment observation
            
        Returns:
            List of actions for each station
        """
        actions = []
        
        # Simple rule-based policy
        for i, obs in enumerate(observation):
            station_type = self.station_types[i] if i < len(self.station_types) else "unknown"
            
            # Extract features from observation
            occupancy = obs[1]  # Second element is occupancy
            queue_length = obs[2] * 10  # Third element is normalized queue length
            
            # Decision logic based on station type
            if station_type == "conveyor":
                action = self._get_conveyor_action(occupancy, queue_length)
            elif station_type == "crane":
                action = self._get_crane_action(occupancy, queue_length)
            elif station_type == "robotic_arm":
                action = self._get_robotic_arm_action(occupancy, queue_length)
            elif station_type == "assembly_station":
                action = self._get_assembly_station_action(occupancy, queue_length)
            else:
                action = 0  # NO_OP
                
            actions.append(action)
        
        return actions
    
    def _get_conveyor_action(self, occupancy, queue_length):
        """Get action for conveyor station."""
        if occupancy < 0.3 and queue_length > 2:
            return 1  # MOVE_FORWARD - move materials forward
        elif occupancy > 0.8:
            return 2  # MOVE_BACKWARD - move materials backward
        else:
            return 0  # NO_OP
    
    def _get_crane_action(self, occupancy, queue_length):
        """Get action for crane station."""
        if occupancy < 0.5:
            return 3  # PICKUP - pick up materials
        elif occupancy > 0.7:
            return 4  # DROP - drop materials
        else:
            return 0  # NO_OP
    
    def _get_robotic_arm_action(self, occupancy, queue_length):
        """Get action for robotic arm station."""
        if occupancy < 0.4:
            return 3  # PICKUP - pick up materials
        elif occupancy > 0.6 and queue_length < 3:
            return 4  # DROP - drop materials
        else:
            return 5  # PROCESS - process materials
    
    def _get_assembly_station_action(self, occupancy, queue_length):
        """Get action for assembly station."""
        if occupancy > 0.2:
            return 5  # PROCESS - process materials
        else:
            return 0  # NO_OP

def run_system_demo():
    """
    Run a complete demonstration of the assembly line system.
    
    This shows how all components work together in an integrated simulation.
    """
    print("=== Assembly Line System Demo ===")
    
    try:
        # Create environment with moderate complexity
        env = AssemblyLineEnv(
            num_conveyors=2,
            num_cranes=1,
            num_robotic_arms=2, 
            num_assembly_stations=1
        )
        
        # Create simple agent controller
        controller = SimpleAgentController(env)
        
        # Reset environment
        obs, info = env.reset()
        
        print(f"Environment created with:")
        print(f"  - {env.num_conveyors} conveyor stations")
        print(f"  - {env.num_cranes} crane stations") 
        print(f"  - {env.num_robotic_arms} robotic arm stations")
        print(f"  - {env.num_assembly_stations} assembly stations")
        print(f"  Total observation space: {obs.shape}")
        
        # Simulation parameters
        max_steps = 50
        print(f"\nRunning simulation for {max_steps} steps...")
        
        # Simulation loop
        step_rewards = []
        total_products = 0
        
        for step in range(max_steps):
            # Get actions from controller
            actions = controller.get_actions(obs)
            
            # Execute environment step
            obs, rewards, done, truncated, info = env.step(actions)
            
            # Track statistics
            step_rewards.append(sum(rewards))
            total_products = env.completed_products
            
            # Print progress every 10 steps
            if (step + 1) % 10 == 0:
                avg_reward = np.mean(step_rewards[-10:]) if len(step_rewards) >= 10 else np.mean(step_rewards)
                print(f"Step {step + 1:2d}: Avg Reward = {avg_reward:.3f}, Products = {total_products}")
            
            # Check if episode should end
            if done or truncated:
                print(f"Episode ended at step {step + 1}")
                break
        
        # Final statistics
        print(f"\n=== Demo Results ===")
        print(f"Total steps: {step + 1}")
        print(f"Final products completed: {total_products}")
        print(f"Average reward per step: {np.mean(step_rewards):.3f}")
        print(f"Total reward earned: {sum(step_rewards):.3f}")
        
        # Show final state
        print(f"\nFinal System State:")
        env.render()
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_interaction():
    """Test interaction between different agent types."""
    print("\n=== Testing Agent Interaction ===")
    
    try:
        # Create a minimal environment for focused testing
        env = AssemblyLineEnv(
            num_conveyors=1,
            num_cranes=1,
            num_robotic_arms=1,
            num_assembly_stations=1
        )
        
        controller = SimpleAgentController(env)
        obs, info = env.reset()
        
        print("Testing coordinated agent behavior...")
        
        # Run a focused test with specific action patterns
        for step in range(20):
            actions = controller.get_actions(obs)
            
            # Print current state and actions
            print(f"\nStep {step + 1}:")
            
            all_stations = (env.conveyor_stations + env.crane_stations + 
                          env.robotic_arm_stations + env.assembly_stations)
            
            for i, (station, action) in enumerate(zip(all_stations, actions)):
                action_names = ["NO_OP", "MOVE_FORWARD", "MOVE_BACKWARD", "PICKUP", "DROP", "PROCESS"]
                print(f"  {station.type}_{i}: {action_names[action]} (occupancy: {station.occupancy:.2f})")
            
            # Execute step
            obs, rewards, done, truncated, info = env.step(actions)
            
            if done or truncated:
                break
        
        print("✓ Agent interaction test completed")
        return True
        
    except Exception as e:
        print(f"✗ Agent interaction test failed: {e}")
        return False

def demonstrate_material_flow():
    """Demonstrate material flow through the system."""
    print("\n=== Demonstrating Material Flow ===")
    
    try:
        env = AssemblyLineEnv(
            num_conveyors=2,
            num_cranes=0,  # No cranes for simpler flow
            num_robotic_arms=1,
            num_assembly_stations=1
        )
        
        controller = SimpleAgentController(env)
        obs, info = env.reset()
        
        print("Tracking material flow through the system...")
        
        # Track materials over time
        for step in range(30):
            actions = controller.get_actions(obs)
            obs, rewards, done, truncated, info = env.step(actions)
            
            # Count materials at each station type
            conveyor_materials = sum(len(s.materials) for s in env.conveyor_stations)
            robotic_arm_materials = sum(len(s.materials) for s in env.robotic_arm_stations)
            assembly_materials = sum(len(s.materials) for s in env.assembly_stations)
            
            print(f"Step {step + 1:2d}: "
                  f"Conveyors={conveyor_materials}, "
                  f"Robotic Arms={robotic_arm_materials}, "
                  f"Assembly={assembly_materials}, "
                  f"Completed={env.completed_products}")
            
            if done or truncated:
                break
        
        print(f"\nMaterial flow demonstration completed!")
        print(f"Total materials processed: {env.completed_products}")
        
        return True
        
    except Exception as e:
        print(f"✗ Material flow demonstration failed: {e}")
        return False

def performance_benchmark():
    """Run a simple performance benchmark."""
    print("\n=== Performance Benchmark ===")
    
    try:
        import time
        
        # Test different environment sizes
        configurations = [
            (1, 0, 1, 1),   # Minimal
            (2, 1, 2, 1),   # Medium  
            (3, 1, 3, 2),   # Large
        ]
        
        for config in configurations:
            num_conveyors, num_cranes, num_robotic_arms, num_assembly_stations = config
            
            print(f"\nTesting configuration: {num_conveyors}C, {num_cranes}R, {num_robotic_arms}A, {num_assembly_stations}S")
            
            # Create environment
            env = AssemblyLineEnv(
                num_conveyors=num_conveyors,
                num_cranes=num_cranes,
                num_robotic_arms=num_robotic_arms,
                num_assembly_stations=num_assembly_stations
            )
            
            controller = SimpleAgentController(env)
            
            # Benchmark timing
            start_time = time.time()
            steps = 25
            
            obs, info = env.reset()
            for _ in range(steps):
                actions = controller.get_actions(obs)
                obs, rewards, done, truncated, info = env.step(actions)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"  {steps} steps in {elapsed:.3f} seconds")
            print(f"  Average: {elapsed/steps:.4f} seconds per step")
            
        print("✓ Performance benchmark completed")
        return True
        
    except Exception as e:
        print(f"✗ Performance benchmark failed: {e}")
        return False

def main():
    """Run the complete system demonstration."""
    print("🚀 Assembly Line System Integration Demo")
    print("=" * 50)
    
    demo_functions = [
        ("System Demo", run_system_demo),
        ("Agent Interaction", test_agent_interaction), 
        ("Material Flow", demonstrate_material_flow),
        ("Performance Benchmark", performance_benchmark)
    ]
    
    results = []
    
    for demo_name, demo_func in demo_functions:
        print(f"\n{'='*50}")
        result = demo_func()
        results.append((demo_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("=== DEMO SUMMARY ===")
    
    passed = 0
    for demo_name, result in results:
        status = "✓ SUCCESS" if result else "✗ FAILED"
        print(f"{demo_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} demos completed successfully")
    
    if passed == len(results):
        print("🎉 All system integration demos completed successfully!")
        print("The system is ready for advanced multi-agent training.")
    else:
        print(f"⚠️  {len(results) - passed} demos failed. Please review the issues.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)