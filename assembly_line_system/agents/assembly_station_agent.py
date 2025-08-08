"""
Assembly Station Agent implementation for the assembly line system.
"""

from assembly_line_system.agents.base_agent import AssemblyLineAgent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import time

class AssemblyStationAgent(AssemblyLineAgent):
    """
    Agent representing an assembly station in the assembly line.

    Responsibilities:
    - Assemble final products from components
    - Coordinate with other stations for material flow
    - Handle quality control and product validation
    """

    def __init__(self, agent_id, jid, password, env):
        """
        Initialize the assembly station agent.

        Args:
            agent_id (str): Unique identifier for the agent
            jid (str): JID for XMPP communication
            password (str): Password for XMPP authentication
            env: Reference to the shared environment
        """
        super().__init__(agent_id, jid, password, env)

        # Assembly station-specific attributes
        self.production_rate = 1.0  # Products per time step
        self.quality_control = 0.98  # Quality assurance level (0.0 to 1.0)
        self.current_products = []
        self.assembly_queue = []

    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class AssemblyStationCyclicBehaviour(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Assembly station cyclic behaviour running")

                # Check for materials to assemble
                await self._assemble_products()

        return AssemblyStationCyclicBehaviour()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class AssemblyStationPeriodicBehaviour(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Assembly station periodic behaviour running")

                # Check quality and perform maintenance
                await self._check_quality()

        return AssemblyStationPeriodicBehaviour(period=25)  # Check every 25 time steps

    async def _assemble_products(self):
        """Assemble products from components."""
        print(f"{self.agent_id}: Assembling products")

        # Simulate assembly process
        if len(self.assembly_queue) > 0:
            print(f"{self.agent_id}: Assembling {len(self.assembly_queue)} products")
            # Simulate assembly time
            await asyncio.sleep(3)
            print(f"{self.agent_id}: Products assembled successfully")
            
            # Move completed products to output
            self.current_products.extend(self.assembly_queue)
            self.assembly_queue.clear()

    async def _check_quality(self):
        """Check product quality and perform maintenance tasks."""
        print(f"{self.agent_id}: Checking quality control")
        
        # In a real implementation, this would check actual product quality
        if self.current_products:
            print(f"{self.agent_id}: Quality control for {len(self.current_products)} products")

    async def setup(self):
        """Set up the assembly station agent."""
        print(f"{self.agent_id}: Assembly station agent started")
        await super().setup()

    async def on_start(self):
        """Handle agent start event."""
        print(f"{self.agent_id}: Assembly station agent started")

    async def on_stop(self):
        """Handle agent stop event."""
        print(f"{self.agent_id}: Assembly station agent stopped")
        
    # Methods for XMPP communication
    def can_accept_transfer(self, material_id, quantity):
        """Check if this assembly station can accept a transfer."""
        # Assembly stations typically have high capacity for components
        return True
        
    def get_ready_time(self):
        """Get the time when this assembly station will be ready to accept a transfer."""
        return int(time.time()) + 2  # Ready in 2 seconds
        
    def perform_transfer(self):
        """Perform the actual material transfer."""
        # In a real implementation, this would update internal state
        return "success"