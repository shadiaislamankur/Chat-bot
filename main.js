// main.js

document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("send-btn");
  const turboBtn = document.getElementById("turbo-btn"); // New Turbo mode button
  const userInput = document.getElementById("user-input");
  const chatbox = document.getElementById("chatbox");
  let turboMode = false; // Flag to track Turbo mode status

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

  turboBtn.addEventListener("click", toggleTurboMode); // Attach click event to Turbo mode button

  function sendMessage() {
    const message = userInput.value.trim();
    if (message === "") return;

    // Add user message to chatbox
    appendMessage("outgoing", message);

    // Determine the mode based on the turboMode flag
    const mode = turboMode ? "turbo" : "normal";

    // Send message and mode to Flask app
    fetch("http://127.0.0.1:5000/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message, mode: mode }), // Include the mode in the request
    })
      .then((response) => response.json())
      .then((data) => {
        // Add response to chatbox
        appendMessage("incoming", data.answer);
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    // Clear input
    userInput.value = "";
  }

  function toggleTurboMode() {
    var button = document.getElementById("turbo-btn");
        if (button.innerHTML === "Normal") {
            button.innerHTML = "Turbo";
        } else {
            button.innerHTML = "Normal";
        }
    // Toggle the Turbo mode flag
    turboMode = !turboMode;
    // You can add additional UI changes or logic based on Turbo mode status here
    console.log("Turbo mode:", turboMode ? "enabled" : "disabled");
  }

  function appendMessage(type, message) {
    const li = document.createElement("li");
    li.classList.add("chat", type);
    const icon = type === "incoming" ? "smart_toy" : "";
    li.innerHTML = `
      <span class="material-symbols-outlined">${icon}</span>
      <p>${message}</p>
    `;
    chatbox.appendChild(li);
    // Scroll to the bottom of chatbox
    chatbox.scrollTop = chatbox.scrollHeight;
  }
});
