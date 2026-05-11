from pydantic import BaseModel
from typing import Optional, Literal, List


class BaseMessage(BaseModel):
    type: Literal["message", "system", "command", "set_username"]  # Types of messages


class ChatMessage(BaseMessage):
    type: Literal["message"] = "message"
    message: str
    sender: Optional[str] = None  # This will be the username or connection ID


class SystemMessage(BaseMessage):
    type: Literal["system"] = "system"
    message: str
    sender: str = "Server"  # System messages always come from the server


class CommandMessage(BaseMessage):
    type: Literal["command"] = "command"
    command: str
    args: Optional[List[str]] = []


class SetUsernameMessage(BaseMessage):
    type: Literal["set_username"] = "set_username"
    username: str


# Union of all possible message types for receiving
ReceivedMessage = ChatMessage | SystemMessage | CommandMessage | SetUsernameMessage
