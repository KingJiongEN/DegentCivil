import asyncio
import json

from starlette.websockets import WebSocket, WebSocketDisconnect

from ..utils.log import LogManager


class WebSocketServer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebSocketServer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.connected_clients = set()
            self.callback = None
            self._initialized = True

    @classmethod
    def _get_instance(cls):
        if not cls._instance:
            return None
        return cls._instance

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            websocket = WebSocket(scope=scope, receive=receive, send=send)
            await websocket.accept()
            self.connected_clients.add(websocket)
            LogManager.log_info(f"[Network]: Establish connection from {websocket.client}")
            try:
                while True:
                    message = await websocket.receive_text()
                    await self.on_message(message)
            except WebSocketDisconnect:
                LogManager.log_info("[Network]: WebSocket disconnected normally")
            except Exception as e:
                LogManager.log_error(f"[Network]: {e}")
            finally:
                try:
                    if websocket in self.connected_clients:
                        self.connected_clients.remove(websocket)
                    await websocket.close()
                except Exception as e:
                    LogManager.log_warning(f"[Network]: disconnecting {e}")

    async def on_message(self, message):
        LogManager.log_info(f"[Network]: Receive message: {message}")
        if message == "start":
            if self.callback:
                task = asyncio.create_task(self.callback())

    @classmethod
    async def broadcast_message_async(cls, message_type: str, data: json):
        instance = cls._get_instance()
        if instance:
            await instance.execute_broadcast_message(message_type, data)

    @classmethod
    def broadcast_message(cls, message_type: str, data: json):
        instance = cls._get_instance()
        if instance:
            coroutine = instance.execute_broadcast_message(message_type, data)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(coroutine, loop)
            else:
                loop.run_until_complete(coroutine)

    async def execute_broadcast_message(self, message_type: str, data: json):
        message = json.dumps({"type": message_type, "data": data})
        LogManager.log_debug(f"[Network]: Broadcasting message")
        try:
            if self.connected_clients:
                await asyncio.gather(*(client.send_text(message) for client in self.connected_clients))
        except Exception as e:
            LogManager.log_error(f"[Network]: Error broadcasting message: {e}")
