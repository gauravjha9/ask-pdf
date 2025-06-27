import { API_BASE_URL } from './constants.js';

export function appendMessage(content, className = 'bot-message') {
    const message = document.createElement('div');
    message.className = `message ${className}`;
    message.innerHTML = content;
    document.getElementById('chat-messages').appendChild(message);
    scrollToBottom();
    return message;
}

export function clearInput(id) {
    document.getElementById(id).value = '';
}

function scrollToBottom() {
    const chat = document.getElementById('chat-messages');
    chat.scrollTop = chat.scrollHeight;
}

export async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-file`, {
        method: 'POST',
        body: formData
    });

    return response.json();
}

export async function sendQuery(sessionId, question) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('query', question);

    const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        body: formData
    });

    return response.json();
}
