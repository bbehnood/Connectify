from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import uuid
import json

from app.core.websocket_manager import ConnectionManager, get_manager
from app.schemas.chat import (
    ChatMessage,
    SystemMessage,
    SetUsernameMessage,
    CommandMessage,
)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, manager: ConnectionManager = Depends(get_manager)
):
    # Generate a unique ID for this connection
    connection_id = str(uuid.uuid4())

    await manager.connect(websocket, connection_id)

    # Send confirmation and current user account
    await websocket.send_json(
        {
            "type": "system",
            "sender": "Server",
            "message": f"Welcome! You are connected with ID: {connection_id}. Users online: {manager.get_connection_count()}",
        }
    )

    await manager.broadcast(
        {
            "type": "system",
            "sender": "Server",
            "message": f"User {connection_id[:6]}... has joined.",  # Short ID for privacy
        }
    )

    try:
        while True:
            data = await websocket.receive_text()

            try:
                data_dict = json.loads(data)

                message_type = data_dict.get("type")

                if message_type == "message":
                    received_message = ChatMessage(**data_dict)
                elif message_type == "set_username":
                    received_message = SetUsernameMessage(**data_dict)
                elif message_type == "command":
                    received_message = CommandMessage(**data_dict)
                elif message_type == "system":
                    # Clients shouldn't typically send system messages
                    print(
                        f"Received unexpected system message from {connection_id}: {data}"
                    )
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "system",
                                "sender": "Server",
                                "message": "You cannot send system messages.",
                            }
                        ),
                        websocket,
                    )
                    continue
                else:
                    # Unknown type
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "system",
                                "sender": "Server",
                                "message": "Unknown message type received.",
                            }
                        ),
                        websocket,
                    )
                    continue

            except json.JSONDecodeError:
                print(f"Invalid JSON format from {connection_id}: {data}")
                await manager.send_personal_message(
                    json.dumps(
                        {
                            "type": "system",
                            "sender": "Server",
                            "message": "Invalid JSON format. Please send valid JSON.",
                        }
                    ),
                    websocket,
                )
                continue
            except Exception as e:  # Catches Pydantic validation errors etc.
                print(
                    f"Pydantic validation or parsing error for {connection_id}: {data} - Error: {e}"
                )
                await manager.send_personal_message(
                    json.dumps(
                        {
                            "type": "system",
                            "sender": "Server",
                            "message": f"Message validation failed: {e}",
                        }
                    ),
                    websocket,
                )
                continue

            # --- Message Handling Logic ---
            current_username = manager.get_username(connection_id)

            if isinstance(received_message, SetUsernameMessage):
                new_username = received_message.username.strip()
                if new_username:
                    # Check if username is already taken
                    if (
                        new_username in manager.user_connections.values()
                        and current_username != new_username
                    ):
                        await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "system",
                                    "sender": "Server",
                                    "message": f"Username '{new_username}' is already taken. Please choose another.",
                                }
                            ),
                            websocket,
                        )
                    else:
                        old_username = manager.get_username(connection_id)
                        await manager.set_username(connection_id, new_username)
                        if old_username:  # If user had a previous username
                            await manager.broadcast(
                                {
                                    "type": "system",
                                    "sender": "Server",
                                    "message": f"User '{old_username}' has changed their name to '{new_username}'.",
                                },
                                sender_connection_id=connection_id,
                            )
                else:
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "system",
                                "sender": "Server",
                                "message": "Username cannot be empty.",
                            }
                        ),
                        websocket,
                    )

            elif isinstance(received_message, ChatMessage):
                sender_display_name = (
                    current_username
                    if current_username
                    else f"User ({connection_id[:6]}...)"
                )
                # Prepare message for broadcast
                message_to_broadcast = {
                    "type": "message",
                    "sender": sender_display_name,
                    "message": received_message.message,
                }
                await manager.broadcast(
                    message_to_broadcast, sender_connection_id=connection_id
                )

            elif isinstance(received_message, CommandMessage):
                # Handle commands like /nick, /join, /leave etc.
                if received_message.command == "nick":
                    if received_message.args:
                        new_username = received_message.args[0]
                        if new_username:
                            await manager.set_username(connection_id, new_username)
                        else:
                            await manager.send_personal_message(
                                json.dumps(
                                    {
                                        "type": "system",
                                        "sender": "Server",
                                        "message": "Username cannot be empty.",
                                    }
                                ),
                                websocket,
                            )
                    else:
                        await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "system",
                                    "sender": "Server",
                                    "message": "Usage: /nick <new_username>",
                                }
                            ),
                            websocket,
                        )
                else:
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "system",
                                "sender": "Server",
                                "message": f"Unknown command: /{received_message.command}",
                            }
                        ),
                        websocket,
                    )

            elif isinstance(received_message, SystemMessage):
                # Server should not receive system messages from client directly
                print(
                    f"Received unexpected system message from {connection_id}: {data}"
                )

            else:
                # Fallback for unexpected message types
                await manager.send_personal_message(
                    json.dumps(
                        {
                            "type": "system",
                            "sender": "Server",
                            "message": "Unknown message type received.",
                        }
                    ),
                    websocket,
                )
    except WebSocketDisconnect:
        username = (
            manager.get_username(connection_id) or f"User ({connection_id[:6]}...)"
        )
        manager.disconnect(connection_id)
        # Announce disconnection to others
        await manager.broadcast(
            {
                "type": "system",
                "sender": "Server",
                "message": f"User '{username}' has left the chat.",
            },
            sender_connection_id=None,
        )  # Broadcast to everyone
    except Exception as e:
        print(f"An unexpected error occurred with {connection_id}: {e}")
        username = (
            manager.get_username(connection_id) or f"User ({connection_id[:6]}...)"
        )
        manager.disconnect(connection_id)
        await manager.broadcast(
            {
                "type": "system",
                "sender": "Server",
                "message": f"User '{username}' has been disconnected due to an error.",
            },
            sender_connection_id=None,
        )
