import asyncio
import random
import logging
from typing import Any
from common import singleton_decorator as s

@s.singleton
class MockOPCUAClient:
    """Mock class for OPCUAClient to simulate OPCUA calls when the PLC is not accessible."""
    connection_status = False

    def __init__(self) -> None:
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 10
            self.reconnect_interval = 5
            self.initialized = True

            self.mock_data_store = {}  # Simulate nodes and their values
            asyncio.create_task(self.connect())

    async def connect(self):
        """Simulate connecting to a PLC."""
        
        logging.info("[MockOPCUAClient] Simulating connection to PLC.")
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate connection delay
        self.reconnect_attempts = 0
        self.connection_status = True
        logging.info("[MockOPCUAClient] Simulated connection established.")
        # as opposed to the real thing, there is no error handling because the mock class can't fail.

    async def disconnect(self):
        """Simulate disconnecting from the PLC."""
        if self.connection_status:
            logging.info("[MockOPCUAClient] Simulating disconnection from PLC.")
            await asyncio.sleep(random.uniform(0.2, 0.5))  # Simulate disconnection delay
            self.connection_status = False
            logging.info("[MockOPCUAClient] Simulated disconnection completed.")

    async def write(self, node_id: str, value: Any) -> None:
        """Simulate writing a value to a node."""
        if not self.connection_status:
            logging.warning("[MockOPCUAClient] Trying to write node, but connection status is False.")
            return False

        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate write delay
        self.mock_data_store[node_id] = value
        logging.info(f"[MockOPCUAClient] Simulated writing value {value} to node {node_id}.")

    async def read(self, node_id: str):
        """Simulate reading a value from a node."""
        if not self.connection_status:
            logging.warning("[MockOPCUAClient] Trying to read node, but connection status is False.")
            return None

        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate read delay
        value = self.mock_data_store.get(node_id, None)
        logging.info(f"[MockOPCUAClient] Simulated reading value {value} from node {node_id}.")
        return value

    def get_status(self):
        """Simulate getting the connection status."""
        return self.connection_status

    def get_reconnection_attempts(self):
        """Simulate getting the reconnection attempts count."""
        return self.reconnect_attempts
