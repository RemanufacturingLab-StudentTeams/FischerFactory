# Manages the OPC UA Client asynchronously. This OPC UA Client writes Dashboard commands to the PLC and awaits responses.

from dotenv import load_dotenv
import os
import logging
from asyncua import Client, ua

class OPCUAClient:
    
    _instance = None
    def __new__(cls, *args, **kwargs): # singleton pattern
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
        return cls._instance        
    
    def __init__(self) -> None:
        self.url = f"opc.tcp://{os.getenv('PLC_IP')}:{os.getenv('PLC_PORT')}" 
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()
        
    async def connect(self):
        if self.client is None:
            self.client = Client(self.url)
            try:
                await self.client.connect()
                logging.info(f"Connected to PLC at {self.url}.")
            except Exception as e:
                logging.error(f"[OPCUACLient] Could not connect to PLC at {self.url}.")
                raise ConnectionError(f"Could not connect to PLC at {self.url}.")
            
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            logging.info("Disconnected from PLC.")
        
    async def write(self, node_id: str, value):
        node = self.client.get_node(node_id)
        try:
            await node.write_value(value)
            logging.info(f"Wrote value {value} to node {node_id}")
        except Exception as e:
            logging.error(f"Failed to write value {value} to node {node_id}: {e}")
            
    async def read(self, node_id: str):
        node = self.client.get_node(node_id)
        try:
            res = await node.read_value()
            logging.debug(f"[OPCUAClient] Read value of node {node_id}: {res}")
            return res
        except Exception as e:
            logging.error(f"Failed to read value of node {node_id}: {e}")
            return None
