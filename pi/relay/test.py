from asyncua import Client as OPCUAClient
from asyncua import Node
from asyncua.ua.uatypes import ExtensionObject, Variant, VariantType
from asyncua.common.subscription import DataChangeNotificationHandlerAsync, DataChangeNotif
from typing import Any
import os
import asyncio
from datetime import datetime, date

PLC_IP = os.getenv('PLC_IP')
PLC_PORT = int(os.getenv('PLC_PORT'))

def _parse_value(value: Any):
    if not isinstance(value, (date, datetime, int, str, bool, float)):
        if isinstance(value, list):
            return [_parse_value(v) for v in value]
        return {k: _parse_value(v) for k, v in value.__dict__.items()}
    else:
        return value
    
class TestHandler(DataChangeNotificationHandlerAsync):
    
    async def datachange_notification(self, node: Node, val: ExtensionObject, data: DataChangeNotif):
        print("Node: " + (await node.read_display_name()).Text)
        
        # Access the Variant
        v: Variant = data.monitored_item.Value.Value
        print(v.VariantType.name)
        print(_parse_value(v.Value))


async def test() -> None:
    o = OPCUAClient(f"opc.tcp://{PLC_IP}:{PLC_PORT}")
    await o.connect()
    await o.load_data_type_definitions()
    handler = TestHandler()
    s = await o.create_subscription(period=1000, handler=handler)
    node = o.get_node('ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"')
    await s.subscribe_data_change(node)
    
    await asyncio.Future()

asyncio.run(test())
