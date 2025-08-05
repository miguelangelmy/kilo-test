"""
Tests for the communication protocols.
"""

import pytest
import json
from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol

def test_material_transfer_request():
    """Test creating a material transfer request message."""
    msg = MaterialTransferProtocol.create_request_message(
        "conveyor_1",
        "crane_1@localhost",
        "material_42",
        3,
        "assembly_station_1"
    )

    # Check message properties
    assert msg.to == "crane_1@localhost"

    # Check message content
    content = msg.body
    assert "material_id" in content
    assert "quantity" in content
    assert "destination" in content

def test_material_transfer_confirm():
    """Test creating a material transfer confirmation message."""
    msg = MaterialTransferProtocol.create_confirm_message(
        "crane_1",
        "conveyor_1@localhost",
        5
    )

    # Check message properties
    assert msg.to == "conveyor_1@localhost"

    # Check message content
    content = msg.body
    assert "target" in content
    assert "ready_time" in content

def test_material_transfer_execute():
    """Test creating a material transfer execution message."""
    msg = MaterialTransferProtocol.create_execute_message(
        "conveyor_1",
        "crane_1@localhost"
    )

    # Check message properties
    assert msg.to == "crane_1@localhost"
    content = json.loads(msg.body)
    assert content["message_type"] == MaterialTransferProtocol.EXECUTE_TRANSFER

    # Check message content
    content = msg.body
    assert "source" in content

def test_material_transfer_complete():
    """Test creating a material transfer completion message."""
    msg = MaterialTransferProtocol.create_complete_message(
        "crane_1",
        "conveyor_1@localhost",
        "success"
    )

    # Check message properties
    assert msg.to == "conveyor_1@localhost"
    content = json.loads(msg.body)
    assert content["message_type"] == MaterialTransferProtocol.TRANSFER_COMPLETE

    # Check message content
    content = msg.body
    assert "target" in content
    assert "status" in content

def test_material_transfer_handling():
    """Test handling material transfer messages."""
    # Create a mock agent
    class MockAgent:
        def __init__(self):
            self.agent_id = "mock_agent"
            self.transfers = []

        def can_accept_transfer(self, material_id, quantity):
            return True

        def get_ready_time(self):
            return 5

        def perform_transfer(self):
            self.transfers.append("transfer_performed")
            return "success"

    agent = MockAgent()

    # Create a request message
    msg = MaterialTransferProtocol.create_request_message(
        "source_agent",
        "mock_agent@localhost",
        "material_42",
        3,
        "destination"
    )

    # Handle the request
    response = MaterialTransferProtocol.handle_request(agent, msg)

    # Check that a confirmation was created
    assert response is not None
    content = json.loads(response.body)
    assert content["message_type"] == MaterialTransferProtocol.CONFIRM_TRANSFER

    # Create an execute message
    msg = MaterialTransferProtocol.create_execute_message(
        "source_agent",
        "mock_agent@localhost"
    )

    # Handle the execution
    response = MaterialTransferProtocol.handle_execute(agent, msg)

    # Check that a completion message was created
    assert response is not None
    content = json.loads(response.body)
    assert content["message_type"] == MaterialTransferProtocol.TRANSFER_COMPLETE

    # Check that the transfer was performed
    assert len(agent.transfers) == 1