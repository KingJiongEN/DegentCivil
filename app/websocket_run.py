import sys

import uvicorn

sys.path.append('./')

from starlette.responses import PlainTextResponse
from starlette.routing import Route, WebSocketRoute

from app.communication.websocket_server import WebSocketServer
from app.main import main
from config import config


async def homepage(request):
    return PlainTextResponse('Hello, world!')


ws_server = WebSocketServer()
ws_server.callback = main
routes = [
    Route("/", homepage),
    WebSocketRoute("/ws", ws_server)
]

from starlette.applications import Starlette

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host=config.server_host, port=config.server_port)
