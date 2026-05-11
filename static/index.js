const chatbox = document.getElementById('chatbox');
const messageInput = document.getElementById('messageInput');
const usernameInput = document.getElementById('usernameInput');
const usernameContainer = document.getElementById('username-input-container');
const sendButton = document.querySelector('#input-area button');

const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const ws_path = `${ws_scheme}://${window.location.host}/ws`;
const socket = new WebSocket(ws_path);

let currentUsername = null;

function addMessage(sender, message, type = "other") {
	const messageElement = document.createElement('div');
	messageElement.classList.add('message');

	let formattedSender = sender;

	if (type === "my") {
		messageElement.classList.add('my-message');
		formattedSender = "You"; // Always display "You" for your own messages
	} else if (type === "system") {
		messageElement.classList.add('system-message');
		formattedSender = sender; // System sender is often "Server" or descriptive
	} else {
		messageElement.classList.add('other-message');
		formattedSender = `<span class="sender-info">${sender}</span>`; // Other users
	}

	// HTML content to prevent XSS for plain text, but allows sender/type specific formatting
	if (type === "system") {
		 messageElement.innerHTML = `${formattedSender}: ${message}`;
	} else {
		 messageElement.innerHTML = `${formattedSender}: ${message}`;
	}
	chatbox.appendChild(messageElement);
	chatbox.scrollTop = chatbox.scrollHeight;
}

function setUsername() {
	const username = usernameInput.value.trim();
	if (!username) {
		alert("Username cannot be empty.");
		return;
	}
	
	// Send username setting message to server
	const messageToSend = {
		type: "set_username",
		username: username
	};
	socket.send(JSON.stringify(messageToSend));
	
	// Disable username input and button after setting
	usernameInput.disabled = true;
	usernameContainer.style.display = 'none'; // Hide username input section
	messageInput.disabled = false;
	sendButton.disabled = false;
	messageInput.focus();
}

function sendMessage() {
	const message = messageInput.value.trim();
	if (message === "") return;

	if (socket.readyState === WebSocket.OPEN) {
		let messageToSend;
		if (message.startsWith('/')) { // Check for commands
			const parts = message.substring(1).split(' ');
			const command = parts[0];
			const args = parts.slice(1);
			messageToSend = {
				type: "command",
				command: command,
				args: args
			};
		} else {
			messageToSend = {
				type: "message",
				message: message
			};
		}
		socket.send(JSON.stringify(messageToSend));
		// Add your own message immediately to the chatbox
		addMessage("You", message, "my");
		messageInput.value = "";
	} else {
		addMessage("Server", "Cannot send message. Connection is not open.", "system");
	}
}

// --- WebSocket Event Handlers ---
socket.onopen = function(event) {
	console.log("WebSocket connection opened.");
	// Remove "Connecting..." message
	chatbox.innerHTML = ''; 
	addMessage("Server", "Connected! Please set your username.", "system");
	// The username input is already visible by default
};

socket.onmessage = function(event) {
	console.log("Message from server:", event.data);
	try {
		const data = JSON.parse(event.data);

		if (data.type === "message") {
			// For messages from others, display their username
			addMessage(data.sender, data.message, "other");
		} else if (data.type === "system") {
			// Display system messages
			addMessage(data.sender, data.message, "system");
		} else if (data.type === "set_username") {
			console.log("Username set confirmation received (handled by system message).");
		}
	} catch (e) {
		console.error("Failed to parse message or unknown message format:", event.data, e);
		addMessage("Server", `Received: ${event.data}`, "system"); // Fallback
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed:", event);
	addMessage("Server", `Disconnected: ${event.reason || 'Connection closed'}`, "system");
	messageInput.disabled = true;
	sendButton.disabled = true;
};

socket.onerror = function(event) {
	console.error("WebSocket error observed:", event);
	addMessage("Server", "Connection error.", "system");
	messageInput.disabled = true;
	sendButton.disabled = true;
};

// --- Event Listeners ---
messageInput.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		sendMessage();
	}
});

usernameInput.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		setUsername();
	}
});

// Initial focus on username input
usernameInput.focus();

