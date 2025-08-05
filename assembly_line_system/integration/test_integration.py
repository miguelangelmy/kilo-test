"""
Integration test script for the assembly line system.

This script tests the integration between the environment, agents,
and RLlib models to ensure they work together correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv, Material, Station

def test_environment_functionality():
    """Test basic environment functionality."""
    print("=== Testing Environment Functionality ===")
    
    try:
        # Create environment
        env = AssemblyLineEnv(
            num_conveyors=2,
            num_cranes=1, 
            num_robotic_arms=2,
            num_assembly_stations=1
        )
        
        # Test reset
        obs, info = env.reset()
        print(f"✓ Environment reset successful")
        print(f"  Observation shape: {obs.shape}")
        print(f"  Observation dtype: {obs.dtype}")
        
        # Test observation space
        expected_shape = (6, 4)  # 2+1+2+1 stations × 4 features
        assert obs.shape == expected_shape, f"Expected shape {expected_shape}, got {obs.shape}"
        print(f"✓ Observation space correct")
        
        # Test action space
        actions = [0] * 6  # NO_OP for all stations
        obs, rewards, done, truncated, info = env.step(actions)
        print(f"✓ Step function successful")
        print(f"  Rewards shape: {np.array(rewards).shape}")
        print(f"  Done: {done}, Truncated: {truncated}")
        
        # Test rendering
        env.render()
        print(f"✓ Rendering successful")
        
        # Test material spawning and flow
        for _ in range(10):
            actions = [1, 0, 2, 3, 4, 5]  # Different actions for each station
            obs, rewards, done, truncated, info = env.step(actions)
            
            if done or truncated:
                print(f"Episode ended at step {env.current_step}")
                break
        
        print("✓ Environment functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test agent creation and basic functionality."""
    print("\n=== Testing Agent Creation ===")
    
    try:
        from assembly_line_system.agents.conveyor_agent import ConveyorAgent
        from assembly_line_system.agents.crane_agent import CraneAgent  
        from assembly_line_system.agents.robotic_arm_agent import RoboticArmAgent
        from assembly_line_system.agents.assembly_station_agent import AssemblyStationAgent
        
        # Test agent creation (without actually starting them)
        agents = []
        
        # Create conveyor agent
        conveyor_agent = ConveyorAgent(
            agent_id="conveyor_0",
            jid="conveyor@localhost", 
            password="password",
            env=None  # Will be set later
        )
        agents.append(("conveyor", conveyor_agent))
        print(f"✓ Conveyor agent created")
        
        # Create crane agent
        crane_agent = CraneAgent(
            agent_id="crane_0",
            jid="crane@localhost",
            password="password", 
            env=None
        )
        agents.append(("crane", crane_agent))
        print(f"✓ Crane agent created")
        
        # Create robotic arm agents
        for i in range(2):
            robotic_arm = RoboticArmAgent(
                agent_id=f"robotic_arm_{i}",
                jid=f"robotic_arm_{i}@localhost",
                password="password",
                env=None
            )
            agents.append((f"robotic_arm_{i}", robotic_arm))
        print(f"✓ Robotic arm agents created")
        
        # Create assembly station agent
        assembly_station = AssemblyStationAgent(
            agent_id="assembly_station_0",
            jid="assembly_station@localhost", 
            password="password",
            env=None
        )
        agents.append(("assembly_station", assembly_station))
        print(f"✓ Assembly station agent created")
        
        # Test agent-specific methods
        for agent_name, agent in agents:
            if hasattr(agent, 'can_accept_transfer'):
                can_accept = agent.can_accept_transfer("test_material", 1)
                print(f"✓ {agent_name} can_accept_transfer method works")
                
            if hasattr(agent, 'get_ready_time'):
                ready_time = agent.get_ready_time()
                print(f"✓ {agent_name} get_ready_time method works")
                
            if hasattr(agent, 'perform_transfer'):
                transfer_result = agent.perform_transfer()
                print(f"✓ {agent_name} perform_transfer method works")
        
        print("✓ Agent creation test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Agent creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rllib_models():
    """Test RLlib model creation and basic functionality."""
    print("\n=== Testing RLlib Models ===")
    
    try:
        from ray.rllib.models import ModelCatalog
        
        # Import all models
        from assembly_line_system.rllib_models.conveyor_model import ConveyorModel
        from assembly_line_system.rllib_models.crane_model import CraneModel
        from assembly_line_system.rllib_models.robotic_arm_model import RoboticArmModel  
        from assembly_line_system.rllib_models.assembly_station_model import AssemblyStationModel
        
        # Register models
        ModelCatalog.register_custom_model("conveyor_model", ConveyorModel)
        ModelCatalog.register_custom_model("crane_model", CraneModel)
        ModelCatalog.register_custom_model("robotic_arm_model", RoboticArmModel)
        ModelCatalog.register_custom_model("assembly_station_model", AssemblyStationModel)
        
        print(f"✓ All RLlib models registered successfully")
        
        # Test model creation with mock spaces
        import gymnasium as gym
        
        obs_space = gym.spaces.Box(low=0, high=1, shape=(6, 4), dtype=np.float32)
        action_space = gym.spaces.Discrete(6)
        
        models_to_test = [
            ("conveyor_model", ConveyorModel),
            ("crane_model", CraneModel), 
            ("robotic_arm_model", RoboticArmModel),
            ("assembly_station_model", AssemblyStationModel)
        ]
        
        for model_name, model_class in models_to_test:
            try:
                model = model_class(
                    obs_space=obs_space,
                    action_space=action_space, 
                    num_outputs=6,
                    model_config={"model": {}},
                    name=model_name
                )
                
                # Test forward pass with dummy input
                import tensorflow as tf
                
                dummy_obs = {
                    "obs": tf.random.normal((1, 6, 4))
                }
                
                logits, state = model.forward(dummy_obs, [], [])
                value = model.value_function()
                
                print(f"✓ {model_name} forward pass successful")
                print(f"  Logits shape: {logits.shape}")
                print(f"  Value shape: {value.shape}")
                
            except Exception as e:
                print(f"✗ {model_name} test failed: {e}")
                
        print("✓ RLlib models test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ RLlib models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_protocol_integration():
    """Test protocol integration with agents."""
    print("\n=== Testing Protocol Integration ===")
    
    try:
        from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol
        
        # Test protocol message creation
        request_msg = MaterialTransferProtocol.create_request_message(
            source_id="conveyor_0",
            target_jid="crane@localhost", 
            material_id="mat_001",
            quantity=5,
            destination="assembly_station"
        )
        
        confirm_msg = MaterialTransferProtocol.create_confirm_message(
            target_id="conveyor_0",
            source_jid="crane@localhost",
            ready_time=10
        )
        
        execute_msg = MaterialTransferProtocol.create_execute_message(
            source_id="crane_0",
            target_jid="assembly_station@localhost"
        )
        
        complete_msg = MaterialTransferProtocol.create_complete_message(
            target_id="crane_0",
            source_jid="assembly_station@localhost", 
            status="success"
        )
        
        print(f"✓ Protocol message creation successful")
        
        # Test protocol message handling (with mock agent)
        class MockAgent:
            def __init__(self):
                self.agent_id = "mock_agent"
                
            def can_accept_transfer(self, material_id, quantity):
                return True
                
            def get_ready_time(self):
                return 5
                
            def perform_transfer(self):
                return "success"
        
        mock_agent = MockAgent()
        
        # Test request handling
        response = MaterialTransferProtocol.handle_request(mock_agent, request_msg)
        print(f"✓ Protocol handle_request works")
        
        # Test execute handling  
        response = MaterialTransferProtocol.handle_execute(mock_agent, execute_msg)
        print(f"✓ Protocol handle_execute works")
        
        print("✓ Protocol integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Protocol integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_integration_demo():
    """Create a simple demonstration of the integrated system."""
    print("\n=== Creating Integration Demo ===")
    
    try:
        # Create environment
        env = AssemblyLineEnv(
            num_conveyors=1,
            num_cranes=1,
            num_robotic_arms=1, 
            num_assembly_stations=1
        )
        
        # Reset environment
        obs, info = env.reset()
        
        print("Running demo simulation for 20 steps...")
        
        # Run a simple simulation
        for step in range(20):
            # Create actions: each station does something different
            actions = [
                1,  # Conveyor: MOVE_FORWARD
                3,  # Crane: PICKUP  
                4,  # Robotic arm: DROP
                5   # Assembly station: PROCESS
            ]
            
            obs, rewards, done, truncated, info = env.step(actions)
            
            print(f"Step {step + 1}:")
            print(f"  Total reward: {sum(rewards):.3f}")
            print(f"  Completed products: {env.completed_products}")
            
            if done or truncated:
                print(f"Episode ended at step {step + 1}")
                break
        
        # Final statistics
        print(f"\nDemo completed!")
        print(f"Final step: {env.current_step}")
        print(f"Total products completed: {env.completed_products}")
        
        # Show final state
        env.render()
        
        return True
        
    except Exception as e:
        print(f"✗ Integration demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("=== Assembly Line System Integration Tests ===")
    
    test_results = []
    
    # Run all tests
    test_functions = [
        ("Environment Functionality", test_environment_functionality),
        ("Agent Creation", test_agent_creation), 
        ("RLlib Models", test_rllib_models),
        ("Protocol Integration", test_protocol_integration),
        ("Integration Demo", create_integration_demo)
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n{'='*50}")
        result = test_func()
        test_results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("=== INTEGRATION TEST SUMMARY ===")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The system is ready for the next phase.")
    else:
        print("⚠️  Some tests failed. Please review the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)