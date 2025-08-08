"""
Crane Agent implementation for the assembly line system.
"""

from assembly_line_system.agents.base_agent import AssemblyLineAgent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import time

class CraneAgent(AssemblyLineAgent):
    """
    Agent representing a crane in the assembly line.

    Responsibilities:
    - Move heavy objects between areas
    - Coordinate with conveyor belts and robotic arms
    - Handle material transfer operations
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
        self.capacity = 3  # Maximum materials that can be moved simultaneously
        self.lifting_capacity = 100.0  # Maximum weight in kg
        self.current_load = 0
        self.is_moving = False

    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class CraneCyclicBehaviour(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Crane cyclic behaviour running")

                # Check for materials to move
                if not self.is_moving:
                    await self._move_materials()

        return CraneCyclicBehaviour()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class CranePeriodicBehaviour(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Crane periodic behaviour running")

                # Check crane status and optimize operations
                await self._check_status()

        return CranePeriodicBehaviour(period=15)  # Check every 15 time steps

    async def _move_materials(self):
        """Move materials between areas."""
        print(f"{self.agent_id}: Moving materials")

        # Simulate crane movement
        if self.current_load > 0:
            print(f"{self.agent_id}: Moving {self.current_load} materials")
            self.is_moving = True
            # Simulate movement time
            await asyncio.sleep(1)
            self.is_moving = False
            print(f"{self.agent_id}: Materials moved successfully")

    async def _check_status(self):
        """Check crane status and perform maintenance tasks."""
        print(f"{self.agent_id}: Checking crane status")
        
        # In a real implementation, this would check actual crane status
        if self.current_load > 0:
            print(f"{self.agent_id}: Crane has {self.current_load} materials in transit")

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
        
    # Methods for XMPP communication
    def can_accept_transfer(self, material_id, quantity):
        """Check if this crane can accept a transfer."""
        return self.current_load + quantity <= self.capacity
        
    def get_ready_time(self):
        """Get the time when this crane will be ready to accept a transfer."""
        return int(time.time()) + 10  # Ready in 10 seconds
        
    def perform_transfer(self):
        """Perform the actual material transfer."""
        # In a real implementation, this would update internal state
        return "success"