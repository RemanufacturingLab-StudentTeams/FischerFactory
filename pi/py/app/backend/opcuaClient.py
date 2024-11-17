# Manages the OPC UA Client asynchronously. This OPC UA Client writes Dashboard commands to the PLC and awaits responses.
import os
import logging
from logger import c
import asyncio
from asyncua import Client, ua
from common import singleton_decorator as s

@s.singleton
class OPCUAClient:
    connection_status = False
    
    def __init__(self) -> None:
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 10
            self.reconnect_interval = 5
            
            self.url = f"opc.tcp://{os.getenv('PLC_IP')}:{os.getenv('PLC_PORT')}" 
            self.client = Client(self.url, 30)
            
            self.client.session_timeout = 30000
            self.initialized = True 
            
            asyncio.create_task(self.connect())
        
    async def connect(self):
        try:
            logging.info(f"[OPCUACLient] Attempting to connect to PLC at {self.url}.")
            await self.client.connect()
            logging.info(f"[OPCUACLient] Connected to PLC at {self.url}.")
            self.reconnect_attempts = 0
            self.connection_status = True
            
        except Exception as e:
            logging.error(f"[OPCUACLient] Failed to connect to PLC at {self.url}.")
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                logging.info(f"[OPCUACLient] Attempting reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await asyncio.create_task(self.attempt_reconnection())
            else:
                logging.error("[OPCUACLient] Max reconnection attempts reached. Stopping OPCUA client.")
                raise ConnectionRefusedError()
            
    async def attempt_reconnection(self):
        self.connection_status = False
        await asyncio.sleep(self.reconnect_interval)
        await self.connect()
            
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            logging.info("[OPCUAClient] Disconnected from PLC.")
            self.connection_status = False
        
    async def write(self, node_id: str, value):
        node = self.client.get_node(node_id)
        try:
            await node.write_value(value)
            logging.info(f"[OPCUAClient] Wrote value {value} to node {c(node_id, 'white')}")
        except Exception as e:
            logging.error(f"[OPCUAClient] Failed to write value {value} to node {c(node_id, 'white')}: {e}")
            
    async def read(self, node_id: str):
        """Reads the value of a node specified by the Node ID.

        Args:
            node_id (str): Example format: `ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"`.

        Returns:
            Any, Any, Any | None: The value of the requested Node or `None`.
        """
        node = self.client.get_node(node_id)
        logging.info(f"[OPCUAClient] Trying to read value of node {c(node_id, 'white')}")
        
        try:
            res = await node.read_value()
            logging.info(f"[OPCUAClient] Read value of node {c(node_id, 'white', 'cyan')}: {c(res, 'white')}")
            return res
        except Exception as e:
            logging.error(f"[OPCUAClient] Failed to read value of node {c(node_id, 'white')}: {e}")
            return None
        
    def get_status(self):
        return self.connection_status
    
    def get_reconnection_attempts(self):
        return self.reconnect_attempts
