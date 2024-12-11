const socket = new WebSocket('ws://yourserver.com/socket');


socket.onopen = function(event) {
    console.log('WebSocket is open now.');
};

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    displayMessage(message);
};

function displayMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const newMessage = document.createElement('div');
    newMessage.textContent = message.user + ': ' + message.text;
    chatBox.appendChild(newMessage);
}

document.getElementById('send-button').addEventListener('click', function() {
    const inputField = document.getElementById('message-input');
    const message = {
        user: 'YourUsername',
        text: inputField.value
    };
    socket.send(JSON.stringify(message));
    inputField.value = '';
});

// document.getElementById('search-btn').addEventListener('click', async () => {
//     const query = document.getElementById('search-input').value;
//     const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
//     const results = await response.json();

//     const resultsContainer = document.getElementById('search-results');
//     resultsContainer.innerHTML = '';

//     if (results.length) {
//         results.forEach((person) => {
//             const li = document.createElement('li');
//             li.textContent = person.name;
//             li.addEventListener('click', () => {
//                 // Implement logic to open chat with the selected person
//                 window.location.href = `/chat/${person.id}`;
//             });
//             resultsContainer.appendChild(li);
//         });
//     } else {
//         resultsContainer.innerHTML = '<li>No users found</li>';
//     }
// });
async function loadChatHistory(userId, contactId) {
    try {
        const response = await fetch(`/get_messages?user_id=${userId}&contact_id=${contactId}`);
        const messages = await response.json();

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = ''; // Clear current messages

        messages.forEach(msg => {
            const messageClass = msg.sender_id === userId ? 'sent' : 'received';
            messagesContainer.innerHTML += `<div class="message ${messageClass}">
                <strong>${messageClass === 'sent' ? 'You' : 'Them'}:</strong> ${msg.message}
                <span class="timestamp">${new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>`;
        });
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

async function handleLogin(username, password) {
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (data.success) {
            const userId = data.user_id; // Retrieved from the backend
            sessionStorage.setItem('user_id', userId);

            // Optionally, load recent contacts or history
            const recentContact = sessionStorage.getItem('recent_contact');
            if (recentContact) {
                loadChatHistory(userId, recentContact);
            }
        } else {
            alert('Login failed: ' + data.error);
        }
    } catch (error) {
        console.error('Login error:', error);
    }
}
