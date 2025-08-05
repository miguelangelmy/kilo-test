"""
Crane Agent implementation for the assembly line system.
"""

from assembly_line_system.agents.base_agent import AssemblyLineAgent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import random

class CraneAgent(AssemblyLineAgent):
    """
    Agent representing a crane in the assembly line.

    Responsibilities:
    - Lift and move heavy materials between stations
    - Optimize lifting routes and positioning
    - Handle fragile or oversized materials with care
    - Coordinate with other agents for material handoffs
    """

    def __init__(self, agent_id, jid, password, env):
        """
        Initialize the crane agent.

        Args:
            agent_id (str): Unique identifier for the agent
            jid (str): JID for XMPP communication
            password (str): Password for XMPP authentication
            env: Reference to the shared environment
        """
        super().__init__(agent_id, jid, password, env)

        # Crane-specific attributes
        self.max_lift_capacity = 10  # Maximum weight (tons)
        self.current_load_weight = 0
        self.position_x = random.uniform(0, 100)  # X position in the facility
        self.position_y = random.uniform(0, 100)  # Y position in the facility
        self.movement_speed = 2.0  # Movement speed (units per time step)
        self.lift_precision = 0.95  # Precision of lifting operations
        self.maintenance_status = "operational"  # operational, maintenance, broken

    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class CraneCyclicBehaviour(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Crane cyclic behaviour running")

                # Check maintenance status
                if self.maintenance_status == "operational":
                    # Look for materials to lift
                    await self._scan_for_materials()
                    
                    # Move to optimal position if needed
                    await self._optimize_position()
                    
                    # Perform lifting operations
                    await self._perform_lift_operations()
                else:
                    print(f"{self.agent_id}: Crane in {self.maintenance_status} status")

        return CraneCyclicBehaviour()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class CranePeriodicBehaviour(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Crane periodic behaviour running")

                # Check maintenance needs
                await self._check_maintenance()
                
                # Optimize lifting schedule
                await self._optimize_lift_schedule()

        return CranePeriodicBehaviour(period=15)  # Check every 15 time steps

    async def _scan_for_materials(self):
        """Scan for materials that need lifting."""
        print(f"{self.agent_id}: Scanning for materials to lift")
        
        # Simulate scanning environment
        available_materials = self._get_available_materials()
        
        for material in available_materials:
            if (self.can_lift_material(material) and 
                self.current_load_weight + material.weight <= self.max_lift_capacity):
                
                print(f"{self.agent_id}: Found suitable material {material.id}")
                await self._request_lift_permission(material)

    async def _optimize_position(self):
        """Optimize crane position based on material locations."""
        print(f"{self.agent_id}: Optimizing position")
        
        # Calculate optimal position based on pending materials
        target_x, target_y = self._calculate_optimal_position()
        
        # Move towards optimal position (simplified)
        distance = ((target_x - self.position_x)**2 + (target_y - self.position_y)**2)**0.5
        
        if distance > 1.0:  # If not close enough
            move_x = (target_x - self.position_x) / distance * self.movement_speed
            move_y = (target_y - self.position_y) / distance * self.movement_speed
            
            self.position_x += move_x
            self.position_y += move_y
            
            print(f"{self.agent_id}: Moved to position ({self.position_x:.1f}, {self.position_y:.1f})")

    async def _perform_lift_operations(self):
        """Perform material lifting operations."""
        print(f"{self.agent_id}: Performing lift operations")
        
        if self.current_load_weight > 0:
            # Transport current load to destination
            await self._transport_materials()
        else:
            # Look for new materials to pick up
            await self._pickup_materials()

    async def _transport_materials(self):
        """Transport currently loaded materials."""
        print(f"{self.agent_id}: Transporting {self.current_load_weight} tons of material")
        
        # Simulate transport with some probability of success
        if random.random() < self.lift_precision:
            # Successfully deliver materials
            delivered_weight = min(self.current_load_weight, 
                                 random.uniform(1, 3))  # Deliver some weight
            
            self.current_load_weight -= delivered_weight
            print(f"{self.agent_id}: Delivered {delivered_weight} tons, remaining: {self.current_load_weight}")
        else:
            # Transport failed due to precision issues
            print(f"{self.agent_id}: Transport precision issue")

    async def _pickup_materials(self):
        """Pick up materials from current location."""
        print(f"{self.agent_id}: Looking for materials to pick up")
        
        available_materials = self._get_available_materials()
        
        for material in available_materials:
            if (self.can_lift_material(material) and 
                self.current_load_weight + material.weight <= self.max_lift_capacity):
                
                # Pick up the material
                self.current_load_weight += material.weight
                print(f"{self.agent_id}: Picked up {material.id} ({material.weight} tons)")
                break  # Pick up one material at a time

    async def _check_maintenance(self):
        """Check if crane needs maintenance."""
        print(f"{self.agent_id}: Checking maintenance status")
        
        # Random chance of needing maintenance
        if random.random() < 0.05:  # 5% chance per check
            self.maintenance_status = "maintenance"
            print(f"{self.agent_id}: Crane needs maintenance")
            
        # Random chance of returning to operational
        elif self.maintenance_status == "maintenance" and random.random() < 0.3:
            self.maintenance_status = "operational"
            print(f"{self.agent_id}: Crane back to operational")

    async def _optimize_lift_schedule(self):
        """Optimize the lifting schedule for efficiency."""
        print(f"{self.agent_id}: Optimizing lift schedule")
        
        # Placeholder for RL-based scheduling optimization
        # In a real implementation, this would use the agent's policy network

    def can_lift_material(self, material):
        """Check if crane can lift a specific material."""
        # Check weight capacity
        if material.weight > self.max_lift_capacity:
            return False
            
        # Check maintenance status
        if self.maintenance_status != "operational":
            return False
            
        # Check precision requirements for fragile materials
        if hasattr(material, 'fragile') and material.fragile:
            return self.lift_precision > 0.9
            
        return True

    def _get_available_materials(self):
        """Get list of materials available for lifting."""
        # This would interface with the environment
        # For now, return simulated materials
        class MockMaterial:
            def __init__(self, mat_id, weight):
                self.id = mat_id
                self.weight = weight
                
        return [
            MockMaterial("mat_1", random.uniform(0.5, 8)),
            MockMaterial("mat_2", random.uniform(0.5, 8))
        ]

    def _calculate_optimal_position(self):
        """Calculate optimal position based on pending materials."""
        # Simple heuristic: move towards center of available materials
        target_x = 50 + random.uniform(-20, 20)
        target_y = 50 + random.uniform(-20, 20)
        
        return target_x, target_y

    async def _request_lift_permission(self, material):
        """Request permission to lift a specific material."""
        print(f"{self.agent_id}: Requesting lift permission for {material.id}")
        
        # In a real implementation, this would send a message to the material's current location
        # For now, simulate permission granted
        if random.random() < 0.8:  # 80% chance of permission
            print(f"{self.agent_id}: Lift permission granted")
        else:
            print(f"{self.agent_id}: Lift permission denied")

    async def setup(self):
        """Set up the crane agent."""
        print(f"{self.agent_id}: Crane agent started")
        await super().setup()

    async def on_start(self):
        """Handle agent start event."""
        print(f"{self.agent_id}: Crane agent started")

    async def on_stop(self):
        """Handle agent stop event."""
        print(f"{self.agent_id}: Crane agent stopped")

    # Material transfer protocol methods
    async def can_accept_transfer(self, material_id, quantity):
        """Check if crane can accept a material transfer."""
        return (self.maintenance_status == "operational" and 
                self.current_load_weight + quantity <= self.max_lift_capacity)

    async def get_ready_time(self):
        """Get time when crane is ready to receive materials."""
        return self.current_step + 5  # Ready in 5 time steps

    async def perform_transfer(self):
        """Perform a material transfer."""
        success = random.random() < self.lift_precision
        return "success" if success else "failure"