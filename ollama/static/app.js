async function sendMessage() {
    const userText = document.getElementById("userInput").value;

    const response = await fetch("http://127.0.0.1:5000/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userText }),
    });

    const responseData = await response.json();
    const botResponse = responseData.response;
    displayMessage("Bot", botResponse);
}

function displayMessage(sender, text) {
    const chatDiv = document.getElementById("chat");
    const messageDiv = document.createElement("div");
    messageDiv.textContent = `${sender}: ${text}`;
    chatDiv.appendChild(messageDiv);
}
