import asyncio
import json
import websockets
from typing import Callable, Optional


class LogsWebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.on_log_received: Optional[Callable] = None
        self.running = False
        self.connected = False

    async def connect(self):
        """Подключается к WebSocket серверу и слушает логи"""
        retry_delay = 3
        max_retry_delay = 10

        while True:
            try:
                async with websockets.connect(
                        self.url,
                        ping_interval=20,
                        ping_timeout=10,
                        close_timeout=5,
                        open_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    self.running = True
                    self.connected = True
                    retry_delay = 3

                    # Отправляем ping каждые 15 секунд
                    async def send_ping():
                        while self.running:
                            try:
                                await websocket.send("ping")
                                await asyncio.sleep(15)
                            except:
                                break

                    ping_task = asyncio.create_task(send_ping())

                    try:
                        async for message in websocket:
                            if message == "pong":
                                continue

                            try:
                                log_entry = json.loads(message)
                                if self.on_log_received:
                                    await self.on_log_received(log_entry)
                            except:
                                pass
                    finally:
                        ping_task.cancel()

            except:
                self.connected = False

            if not self.running:
                break

            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, max_retry_delay)

    async def close(self):
        """Закрывает соединение"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass