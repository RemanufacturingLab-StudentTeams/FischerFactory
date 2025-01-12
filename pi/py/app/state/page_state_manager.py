from common import config
from common import singleton_decorator as s
from typing import Any
import asyncio
import logging
from asyncio import Task
from state import state_data_schema
from websockets.server import ServerConnection
import websockets
import os
import json
from backend import mqttClient


@s.singleton
class PageStateManager:
    """Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks. It is a singleton."""

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.mqttClient = mqttClient.MqttClient()
            self.data = state_data_schema._data
            self.connections: dict[str, ServerConnection] = {}
            self.initialized = True

    async def hydrate_page(self, page: str):
        """Meant to fetch data once (as opposed to monitoring, which fetches continually), used to fetch static (unchanging) data for a page.
        It does this by sending a read request to the relay to re-publish all PLC values.
        For other MQTT data sources, it unfortunately cannot request data, because MQTT does not natively support read requests.

        Args:
            page (str): Which page to fetch hydration data for.
        """
        await self.mqttClient.publish(
            os.getenv("MQTT_RELAY_TOPIC") + "/read",
            {
                "topics": [
                    topic.lstrip("relay/")
                    for topic in self.data.get(page, {}).values()
                    if topic.startswith(
                        "relay"
                    )  # only send read requests for PLC topics
                ]
            },
        )

    async def stop_monitoring(self, page: str):
        """Stop all monitoring tasks."""
        logging.debug(f"[PSM] Stopping all monitoring tasks")
        if page == "global":
            return
        for topic in self.data.get(page, {}):
            self.mqttClient.client.unsubscribe(topic)

    async def monitor_page(self, page: str):
        """Called on page load. Stops all previous monitoring tasks and starts monitoring data for the requested page.
        When it receives a message on a topic, it emits this value over a WebSocket using the page and key for the pathname. For instance, when monitoring the `factory-overview` page, it will emit on `factory-overview/plc_version` and `factory-overview/turtlebot_current_state`.
        On the clientside, a clientside callback listens on this websocket and stores the value in a dcc.Store, so it can be accessed by the GUI.

        Args:
            page (str): Which page to poll/subscribe to monitoring data for.
        """

        logging.debug(
            f"[PSM] Monitoring page: {page} with data: {[k for k, s in self.data.get(page, {}).items()]}"
        )

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, topic in self.data.get(page, {}).items():
            logging.debug(
                f"[PSM] Creating monitoring task for key {key} on topic {topic}"
            )

            async def callback(msg, key=key):
                conn = self.connections.get(key)
                if conn is None:
                    logging.warning(
                        f"[PSM] Received data for key {key}, but no ServerConnection exists for that key."
                    )
                else:
                    try:
                        await conn.send(json.dumps(msg))
                        logging.debug(
                            f"[PSM] Sent message {msg} to FrontEnd WebSocket {key}"
                        )
                    except Exception as e:
                        logging.error(
                            f"[PSM] Failed to send message to frontend WebSocket {key}: {e}"
                        )

            logging.debug(f"[PSM] Adding monitoring task...")
            subscription_tasks = []
            subscription_tasks.append(
                asyncio.create_task(
                    self.mqttClient.subscribe(topic, qos=1, callback=callback)
                )
            )

        logging.debug(f"[PSM] Awaiting monitoring tasks.")

        await asyncio.gather(*subscription_tasks)

    async def send_data(self, page: str, key: str, data: dict):
        """Publish a data item to a source.

        Args:
            page (str): Page to that contains the key. Use a hyphen as a delimiter. Example: `factory-data`.
            data (dict): A dictionary that will be translated to JSON to send to the broker. Example: {'order_do_oven': True, 'order_bake_time': 4000}.
        """
        if page not in self.data:
            return

        topic = self.data.get(page, {}).get(key, {})

        logging.debug(f"[PSM] Sending user data: {data} over {topic}")
        await self.mqttClient.publish(topic, data)

    # def generate_websockets(self, page: str) -> list[FrontEndWebSocket]:
    #     """Must be called in the layout variable of every page to receive external data updates. Generates the WebSocket components that function as endpoints for the PSM to send external data to.

    #     Args:
    #         page (str): Page to that contains the key. Use a hyphen as a delimiter. Example: `factory-data`.
    #     """

    #     res = []
    #     for (key, topic) in self.data.get(page, {}).items():
    #         url = f"ws://localhost:{os.getenv('WS_PORT')}/{key}"

    #         frontendWS = FrontEndWebSocket(id={'source': 'mqtt', 'path': f'{key}'}, url=url, message=None)
    #         logging.debug(f"[PSM] Generated frontend WebSocket: id={key} on url=ws://localhost:{os.getenv('WS_PORT')}/{key}")
    #         res += frontendWS

    #     return res
