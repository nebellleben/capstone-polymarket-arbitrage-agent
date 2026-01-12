"""
WebSocket endpoint for real-time updates.

This module provides WebSocket support for broadcasting real-time
alerts, cycle completions, and metrics updates to connected clients.
"""

import asyncio
import json
from datetime import datetime
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.utils.logging_config import logger

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for broadcasting.

    Maintains a set of active connections and provides methods
    for broadcasting messages to all connected clients.
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

        logger.info(
            "websocket_connected",
            client_id=id(websocket),
            total_connections=len(self.active_connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        # Note: This is synchronous, called from disconnect handler
        self.active_connections.discard(websocket)

        logger.info(
            "websocket_disconnected",
            client_id=id(websocket),
            remaining_connections=len(self.active_connections),
        )

    async def broadcast(self, message_type: str, data: dict) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message_type: Type of message (alert_created, cycle_completed, etc.)
            data: Message data payload
        """
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Create a copy of connections to avoid modification during iteration
        connections = list(self.active_connections)

        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(
                    "websocket_send_failed",
                    client_id=id(connection),
                    error=str(e),
                )
                disconnected.append(connection)

        # Clean up disconnected clients
        async with self._lock:
            for connection in disconnected:
                self.active_connections.discard(connection)

        if disconnected:
            logger.info(
                "websocket_cleaned_disconnected",
                count=len(disconnected),
            )

    async def send_personal(self, message: dict, websocket: WebSocket) -> None:
        """
        Send a message to a specific client.

        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(
                "websocket_personal_send_failed",
                client_id=id(websocket),
                error=str(e),
            )


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time updates.

    Clients can connect to this endpoint to receive real-time broadcasts
    of new alerts, cycle completions, and metrics updates.

    Connected clients will receive messages in this format:
    {
        "type": "alert_created" | "cycle_completed" | "metrics_updated",
        "data": { ... },
        "timestamp": "2025-01-12T10:00:00Z"
    }
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connection_established",
                "data": {"message": "Connected to arbitrage detection monitoring"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            # Receive and handle client messages (if any)
            try:
                data = await websocket.receive_text()

                # Parse client message
                message = json.loads(data)

                # Handle ping/pong for keep-alive
                if message.get("type") == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                # Add other message types as needed (e.g., configuration updates)

            except Exception as e:
                logger.warning(
                    "websocket_receive_error",
                    client_id=id(websocket),
                    error=str(e),
                )
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("websocket_disconnected_clean", client_id=id(websocket))
    except Exception as e:
        manager.disconnect(websocket)
        logger.error(
            "websocket_error",
            client_id=id(websocket),
            error=str(e),
        )


# Helper functions for broadcasting from other modules

async def broadcast_alert(alert_data: dict) -> None:
    """
    Broadcast a new alert to all connected clients.

    Args:
        alert_data: Alert data dictionary
    """
    await manager.broadcast("alert_created", alert_data)


async def broadcast_cycle_complete(cycle_data: dict) -> None:
    """
    Broadcast cycle completion to all connected clients.

    Args:
        cycle_data: Cycle metrics data dictionary
    """
    await manager.broadcast("cycle_completed", cycle_data)


async def broadcast_metrics_update(metrics_data: dict) -> None:
    """
    Broadcast metrics update to all connected clients.

    Args:
        metrics_data: Metrics data dictionary
    """
    await manager.broadcast("metrics_updated", metrics_data)


# Export functions for use in other modules
__all__ = [
    "manager",
    "broadcast_alert",
    "broadcast_cycle_complete",
    "broadcast_metrics_update",
]
