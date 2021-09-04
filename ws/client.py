from datetime import datetime
import websockets, typing, asyncio, json
from json.decoder import JSONDecodeError

from .base import BaseSocket
from .models import Message
from .wsprotocols import WSCProtocol

class ClientSocket(BaseSocket):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.listeners['message'].append(self.on_message)
        self.listeners['connect'].append(self.on_connect)
        self.connection = None
    def connect(self, ws_url: str):
        self.loop.run_until_complete(self.__main(ws_url))
        self.loop.run_forever()
    async def on_message(self, message):
        pass
    async def __message_consumer(self):
        async for message in self.connection:
            try:
                data = json.loads(message)
            except JSONDecodeError:
                data = message
            await asyncio.wait([coro(Message(data=data,
                                             websocket=self.connection,
                                             created_at=datetime.utcnow()
                                            )) for coro in self.listeners['message']])
    async def __on_connect(self):
        await asyncio.wait([coro() for coro in self.listeners['connect']])
    async def on_connect(self):
        pass
    async def __main(self, ws_url):
        self.connection = await websockets.connect(ws_url, create_protocol=WSCProtocol)
        await asyncio.wait([self.__message_consumer(),
                            self.__on_connect()
                            ])
    async def send(self, content: typing.Any = None, *, data: dict = None):
        await self.connection.send(content=content, data=data)
