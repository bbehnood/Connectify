# Connectify

Connectify is a real-time chat application enabling seamless communication between users. This project features a FastAPI backend with WebSocket support for instant messaging and a Pydantic-based schema for robust message handling.

## Features
*   **Real-time Chat:** Users can send and receive messages instantly.
*   **Usernames:** Users can set and change their usernames.
*   **Command Handling:** Basic commands like `/nick` are supported.
*   **Robust Message Handling:** Uses Pydantic models for validating incoming and outgoing messages, ensuring data integrity.
*   **Connection Management:** Tracks connected users and broadcasts connection/disconnection events.

## Tech Stack

*   **Backend:** Python, FastAPI
*   **WebSockets:** FastAPI's WebSocket support
*   **Data Validation:** Pydantic
*   **Frontend:** Super simple frontend with HTML, CSS, JS (You can use the API with your own frontend)

## Project Structure

Connectify/

├── app/

│ ├── api/

│ │ ├── init.py

│ │ └── websocket.py

│ ├── core/

│ │ ├── init.py

│ │ └── websocket_manager.py

│ ├── schemas/

│ │ ├── init.py

│ │ └── chat.py

│ └── main.py

├── .env

├── .gitignore

├── requirements.txt

└── README.md

## Setup Instructions

### Prerequisites

*   Python 3.7+

### Installation

1.  **Clone the repository:**
```bash
git clone https://github.com/bbehnood/Connectify.git
cd Connectify
```
2.  **Set up a virtual environment (recommended):**
```bash
python3 -m venv .venv  # On Windows use `python -m venv .venv`
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3.  **Upgrade pip (recommended):**
```bash
python -m pip install --upgrade pip
```
4.  **Install the dependencies**:
```bash
pip install -r requirements.txt
```

### Running the Applications
```bash
uvicorn main:app --reload
```
*The server will run on http://localhost:8000*

## Usage
**Connecting**: When a user connects, they will receive a system message with their connection ID and the current number of users online.
**Setting Username**: Users can set their initial username or change it using:

*  A dedicated UI element (e.g., an input field and button).
*  The /nick <new_username> command in the chat input.

*Frontend Note*: Ensure you are sending a JSON payload like {"type": "set_username", "username": "YourName"} or {"type": "command", "command": "nick", "args": ["YourName"]}.

**Sending Messages**: Type messages in the chat input and press Enter or a send button.

*Frontend Note*: Messages should be sent as JSON like {"type": "message", "message": "Your chat message here"}.

**Receiving Messages**: Chat messages and system notifications (like user joins/leaves) will appear in the chat interface in real-time.

## Important Note on Message Handling

The backend expects messages in a specific JSON format:

*   **Chat Message**: {"type": "message", "message": "the content of the message"}
*   **Set Username**: {"type": "set_username", "username": "desired_username"}
*   **Command**: {"type": "command", "command": "command_name", "args": ["arg1", "arg2"]}

Ensure your frontend consistently sends data in these formats to avoid errors.

## Contributing

1.  **Fork the Project**
2.  **Create a Feature Branch (git checkout -b feature/AmazingFeature)**
3.  **Commit your Changes (git commit -m 'Add some AmazingFeature')**
4.  **Push to the Branch (git push origin feature/AmazingFeature)**
5.  **Open a Pull Request**
