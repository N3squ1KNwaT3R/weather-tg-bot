from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Set
import json
from datetime import datetime
from loguru import logger

websocket_router = APIRouter(prefix="/ws", tags=["websocket"])


# Хранилище активных WebSocket соединений
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.log_buffer = []  # Буфер последних логов
        self.max_buffer_size = 100

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Admin connected to logs WebSocket. Total connections: {len(self.active_connections)}")

        # Отправляем буферизированные логи новому подключению
        for log_entry in self.log_buffer:
            try:
                await websocket.send_json(log_entry)
            except Exception as e:
                logger.error(f"Error sending buffered log: {e}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Admin disconnected from logs WebSocket. Total connections: {len(self.active_connections)}")

    async def broadcast_log(self, log_data: dict):
        """Отправляет лог всем подключенным клиентам"""
        # Добавляем в буфер
        self.log_buffer.append(log_data)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)

        # Отправляем активным соединениям
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(log_data)
            except Exception as e:
                logger.error(f"Error broadcasting log: {e}")
                disconnected.add(connection)

        # Удаляем отключен��ые соединения
        self.active_connections -= disconnected


manager = ConnectionManager()


@websocket_router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint для real-time логов"""
    await manager.connect(websocket)
    try:
        while True:
            # Ждем ping от клиента для поддержания соединения
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def log_user_activity(
        user_id: int,
        username: str,
        action: str,
        details: dict = None,
        level: str = "info"
):
    """Функция для логирования активности пользователя"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "username": username,
        "action": action,
        "details": details or {},
        "level": level
    }

    # Логируем в loguru
    log_message = f"User {username} (ID: {user_id}) - {action}"
    if details:
        log_message += f" | Details: {json.dumps(details)}"

    if level == "error":
        logger.error(log_message)
    elif level == "warning":
        logger.warning(log_message)
    else:
        logger.info(log_message)

    # Отправляем в WebSocket
    await manager.broadcast_log(log_entry)