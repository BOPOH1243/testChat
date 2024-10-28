// static/chat.js

const token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
const socket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    const chat = document.getElementById("chat");
    chat.innerHTML += `<p><b>${message.username}:</b> ${message.content}</p>`;
};

function sendMessage() {
    const input = document.getElementById("message");
    socket.send(input.value);
    input.value = "";
}
