"""
Base agent class for the assembly line system using SPADE.
"""

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import time

class AssemblyLineAgent(Agent):
    """
    Base agent class for assembly line components.

    This class provides the foundation for all agents in the system,
    including conveyor belts, cranes, robotic arms, and assembly stations.
    """

    def __init__(self, agent_id, jid, password, env):
        """
        Initialize the agent.

        Args:
            agent_id (str): Unique identifier for the agent
            jid (str): JID for XMPP communication
            password (str): Password for XMPP authentication
            env: Reference to the shared environment
        """
        super().__init__(jid, password)

        self.agent_id = agent_id
        self.env = env

        # Register default behaviors
        self.default_behaviours = [
            self._setup_cyclic_behaviour(),
            self._setup_periodic_behaviour()
        ]

    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class CyclicBehaviourHandler(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Cyclic behaviour running")
                # Implementation will be expanded

        return CyclicBehaviourHandler()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class PeriodicBehaviourHandler(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Periodic behaviour running")
                # Implementation will be expanded

        return PeriodicBehaviourHandler()

    async def setup(self):
        """Set up the agent."""
        print(f"{self.agent_id}: Agent started")
        await super().setup()

    async def start_agent(self):
        """Start the agent."""
        print(f"{self.agent_id}: Starting agent...")
        await self.start()

    async def stop_agent(self):
        """Stop the agent."""
        print(f"{self.agent_id}: Stopping agent...")
        await self.stop()

    async def send_message(self, to_jid, message_type, content):
        """
        Send a message using SPADE protocols.

        Args:
            to_jid (str): Recipient JID
            message_type (str): Type of message (e.g., 'material_transfer', 'task_assignment')
            content (dict): Message content
        """
        from spade.message import Message

        # Include message type in the content
        content_with_type = {
            "message_type": message_type,
            **content
        }
        msg = Message(to=to_jid,
                      body=json.dumps(content_with_type))

        await self.send(msg)
        
    # Methods to be implemented by subclasses for proper XMPP communication
    def can_accept_transfer(self, material_id, quantity):
        """Check if this agent can accept a transfer."""
        # Default implementation - should be overridden by subclasses
        return True
        
    def get_ready_time(self):
        """Get the time when this agent will be ready to accept a transfer."""
        # Default implementation - should be overridden by subclasses
        return int(time.time()) + 5
        
    def perform_transfer(self):
        """Perform the actual material transfer."""
        # Default implementation - should be overridden by subclasses
        return "success"