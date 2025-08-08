"""
Material Transfer Protocol implementation.

This module defines the communication protocol for transferring materials
between agents in the assembly line system.
"""

import json
from spade.message import Message

class MaterialTransferProtocol:
    """
    Protocol for handling material transfers between agents.

    This protocol defines the message format and behavior for transferring
    materials from one agent to another.
    """

    # Message types
    REQUEST_TRANSFER = "material_transfer_request"
    CONFIRM_TRANSFER = "material_transfer_confirm"
    EXECUTE_TRANSFER = "material_transfer_execute"
    TRANSFER_COMPLETE = "material_transfer_complete"
    TRANSFER_REJECT = "material_transfer_reject"

    @staticmethod
    def create_request_message(source_id, target_jid, material_id, quantity, destination):
        """
        Create a material transfer request message.

        Args:
            source_id (str): ID of the sending agent
            target_jid (str): JID of the receiving agent
            material_id (str): ID of the material to transfer
            quantity (int): Quantity of materials to transfer
            destination (str): Final destination of the materials

        Returns:
            Message: Formatted XMPP message
        """
        content = {
            "message_type": MaterialTransferProtocol.REQUEST_TRANSFER,
            "source": source_id,
            "material_id": material_id,
            "quantity": quantity,
            "destination": destination
        }

        return Message(to=target_jid,
                      body=json.dumps(content))

    @staticmethod
    def create_confirm_message(target_id, source_jid, ready_time):
        """
        Create a material transfer confirmation message.

        Args:
            target_id (str): ID of the receiving agent
            source_jid (str): JID of the sending agent
            ready_time (int): Time when target is ready to receive

        Returns:
            Message: Formatted XMPP message
        """
        content = {
            "message_type": MaterialTransferProtocol.CONFIRM_TRANSFER,
            "target": target_id,
            "ready_time": ready_time
        }

        return Message(to=source_jid,
                      body=json.dumps(content))

    @staticmethod
    def create_execute_message(source_id, target_jid):
        """
        Create a material transfer execution message.

        Args:
            source_id (str): ID of the sending agent
            target_jid (str): JID of the receiving agent

        Returns:
            Message: Formatted XMPP message
        """
        content = {
            "message_type": MaterialTransferProtocol.EXECUTE_TRANSFER,
            "source": source_id
        }

        return Message(to=target_jid,
                      body=json.dumps(content))

    @staticmethod
    def create_complete_message(target_id, source_jid, status):
        """
        Create a material transfer completion message.

        Args:
            target_id (str): ID of the receiving agent
            source_jid (str): JID of the sending agent
            status (str): Transfer status ("success" or "failure")

        Returns:
            Message: Formatted XMPP message
        """
        content = {
            "message_type": MaterialTransferProtocol.TRANSFER_COMPLETE,
            "target": target_id,
            "status": status
        }

        return Message(to=source_jid,
                      body=json.dumps(content))

    @staticmethod
    def create_reject_message(source_id, target_jid, reason):
        """
        Create a material transfer rejection message.

        Args:
            source_id (str): ID of the sending agent
            target_jid (str): JID of the receiving agent
            reason (str): Reason for rejection

        Returns:
            Message: Formatted XMPP message
        """
        content = {
            "message_type": MaterialTransferProtocol.TRANSFER_REJECT,
            "source": source_id,
            "reason": reason
        }

        return Message(to=target_jid,
                      body=json.dumps(content))

    @staticmethod
    def handle_request(agent, msg):
        """
        Handle a material transfer request.

        Args:
            agent: The receiving agent
            msg: Incoming XMPP message

        Returns:
            Message: Confirmation message or None if request is refused
        """
        content = json.loads(msg.body)
        message_type = content.pop("message_type", None)

        # Extract information from message
        source_id = content["source"]
        material_id = content["material_id"]
        quantity = content["quantity"]
        destination = content["destination"]

        print(f"{agent.agent_id}: Received transfer request for {quantity} of material {material_id} from {source_id}")

        # Check if agent can accept the transfer
        if agent.can_accept_transfer(material_id, quantity):
            ready_time = agent.get_ready_time()
            print(f"{agent.agent_id}: Confirming transfer, ready at {ready_time}")

            # Send confirmation
            return MaterialTransferProtocol.create_confirm_message(
                agent.agent_id, msg.sender, ready_time
            )
        else:
            print(f"{agent.agent_id}: Cannot accept transfer")
            # Send rejection message
            reject_content = {
                "message_type": MaterialTransferProtocol.TRANSFER_REJECT,
                "source": source_id,
                "reason": "insufficient_capacity"
            }
            reject_msg = Message(to=msg.sender, body=json.dumps(reject_content))
            return reject_msg

    @staticmethod
    def handle_execute(agent, msg):
        """
        Handle a material transfer execution.

        Args:
            agent: The receiving agent
            msg: Incoming XMPP message

        Returns:
            Message: Completion message
        """
        content = json.loads(msg.body)
        message_type = content.pop("message_type", None)
        source_id = content["source"]

        print(f"{agent.agent_id}: Executing transfer from {source_id}")

        # Perform the transfer (implementation depends on agent type)
        status = agent.perform_transfer()

        print(f"{agent.agent_id}: Transfer completed with status: {status}")

        # Send completion message
        return MaterialTransferProtocol.create_complete_message(
            agent.agent_id, msg.sender, status
        )
        
    @staticmethod
    def handle_reject(agent, msg):
        """
        Handle a material transfer rejection.

        Args:
            agent: The receiving agent
            msg: Incoming XMPP message

        Returns:
            None
        """
        content = json.loads(msg.body)
        message_type = content.pop("message_type", None)

        print(f"{agent.agent_id}: Transfer request rejected: {content}")
        
        # Handle rejection - could log or take corrective action
        return None