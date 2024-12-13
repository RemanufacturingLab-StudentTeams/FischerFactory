import os
import logging
from logger import c
import asyncio
from asyncua import Client, ua
from common import singleton_decorator as s
from typing import Any
from common import config
from backend import mockOpcuaClient
from datetime import datetime

@s.singleton
class OPCUAClient:
    """Wrapper class around the `asyncua` client. Provides reconnection logic, logging, error handling and connection status monitoring. Is a singleton.

    Raises:
        ConnectionRefusedError: If the PLC cannot connect. The connection parameters are in `.env.dev` or `.env.prod`, depending on what mode the program runs in.

    Returns:
        (OPCUAClient): A new instance if none exists, or the existing instance.
    """
    connection_status = False
    
    def __new__(cls, *args, **kwargs):
        if config.mode == 'dev':
            instance = mockOpcuaClient.MockOPCUAClient(*args, **kwargs)
            logging.info("[OPCUAClient] Running in development mode. Using MockOPCUAClient.")
            return instance
        else:
            instance = super().__new__(cls)
            logging.info("[OPCUAClient] Running in production mode. Using real OPCUAClient.")
            return instance
    
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
            logging.info(f"[OPCUAClient] Attempting to connect to PLC at {self.url}.")
            await self.client.connect()
            logging.info(f"[OPCUAClient] Connected to PLC at {self.url}.")
            self.reconnect_attempts = 0
            self.connection_status = True
            
        except Exception as e:
            logging.error(f"[OPCUAClient] Failed to connect to PLC at {self.url}.")
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                logging.info(f"[OPCUAClient] Attempting reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await asyncio.create_task(self.attempt_reconnection())
            else:
                logging.error("[OPCUAClient] Max reconnection attempts reached. Stopping OPCUA client.")
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
        
    async def write(self, node_id: str, value: Any) -> None:
        """Writes a value to the node specified by the Node ID.

        Args:
            node_id (str): Example format: `ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"`.
            value (Any): The value to write. See `schemas/opcua/opcua_schema.ts>DataType` for which values the server accepts.
        """
        
        if not self.connection_status:
            logging.warning(f"[OPCUAClient] Trying to write node, but connection status is False.")
            return
        
        data_type = self._get_data_type_from_node_id(node_id)
        try:
            converted_value = self._convert_to_correct_type(value, data_type)
            node = self.client.get_node(node_id)
            logging.debug(f"[OPCUAClient] Trying to write value {value} to node {c(node_id, 'white')}")
            await node.write_value(converted_value)
            logging.info(f"[OPCUAClient] Wrote value {value} to node {c(node_id, 'white')}")
        except Exception as e:
            logging.error(f"[OPCUAClient] Failed to write value {value} to node {c(node_id, 'white')}: {e}")
            
    def _get_data_type_from_node_id(self, node_id: str) -> str:
        """Determine the data type from the node ID prefix."""
        
        # Hardcoded VariantTypes for node id's that do not fit the standard.
        match node_id.split('.')[-1].strip('\"'):
            case 'OvenTime':
                return 'Int32'
            case 'SawTime':
                return 'Int32'
            case 'DoOven':
                return 'Boolean'
            case 'DoSaw':
                return 'Boolean'
            case 'track_puck':
                return 'String'
        
        prefixes = {
            'x': 'Boolean',
            's': 'String',
            'w': 'Word',  # 16 bits
            'ldt': 'DateTime',
            'i': 'Int16',
            'di': 'Int32',
            'r': 'Float'
        }
        for prefix, data_type in prefixes.items():
            if node_id.split('.')[-1].strip('\"').split('_')[0] == prefix:
                return data_type
        raise ValueError(f"Unknown node ID prefix: {node_id[:2]}")

    def _convert_to_correct_type(self, value: Any, data_type: str) -> object:
        """Convert the input value to the correct type."""
        if data_type == 'Boolean':
            return ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
        elif data_type == 'Int16':
            return ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
        elif data_type == 'Int32':
            return ua.DataValue(ua.Variant(value, ua.VariantType.Int32))
        elif data_type == 'Float':
            return ua.DataValue(ua.Variant(value, ua.VariantType.Float))
        elif data_type == 'DateTime':
            if isinstance(value, datetime):
                return ua.DataValue(ua.Variant(value, ua.VariantType.DateTime))
            else:
                raise ValueError(f"Invalid datetime format for {data_type}")
        elif data_type == 'String':
            return ua.DataValue(ua.Variant(value, ua.VariantType.String))
        elif data_type == 'Word':  # 16 bits
            return int(value) & 0xFFFF
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
            
    async def read(self, node_id: str):
        """Reads the value of a node specified by the Node ID.

        Args:
            node_id (str): Example format: `ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"`.

        Returns:
            (Any | None): The value of the requested Node or `None`.
        """
        if not self.connection_status:
            logging.warning(f"[OPCUAClient] Trying to read node, but connection status is False.")
            return None
        
        node = self.client.get_node(node_id)
        
        try:
            res = await node.read_value()
            logging.debug(f"[OPCUAClient] Read node: {c(node_id, 'cyan', 'white')}: {c(res, 'cyan')}")
            return res
        except Exception as e:
            logging.error(f"[OPCUAClient] Failed to read value of node {c(node_id, 'white')}: {e}")
            return None
        
    def get_status(self):
        return self.connection_status
    
    def get_reconnection_attempts(self):
        return self.reconnect_attempts
