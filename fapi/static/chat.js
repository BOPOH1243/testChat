const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
let ws = new WebSocket("ws://" + window.location.host + "/ws");

// Отображение сообщений в чате
ws.onmessage = function(event) {
    let message = document.createElement("div");
    message.textContent = event.data;
    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;  // Автопрокрутка вниз
};

// Отправка сообщения при нажатии Enter
input.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        ws.send(input.value);
        input.value = "";  // Очистка поля ввода
    }
});
