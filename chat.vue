<template>
  <div :class="theme" class="chat-container">
    <div class="header">
      <h2 class="chat-title">
        <img src="/chatbot.png" alt="Chatbot Icon" class="chat-icon" />
        Aoun Chatbot
      </h2>
      <button @click="toggleTheme" class="theme-toggle">
        <i :class="theme === 'light' ? 'i-heroicons-moon' : 'i-heroicons-sun'"></i>
      </button>
    </div>

    <div v-for="(message, index) in chatHistory" :key="index" class="message-wrapper">
      <div class="message" :class="message.role">
        <img v-if="message.role === 'bot'" src="/chatbot.png" class="bot-avatar" />
        <div class="message-content">
          <p v-html="convertMarkdown(message.content)"></p>
          <span class="timestamp">{{ message.timestamp }}</span>
        </div>
      </div>
    </div>

    <div class="input-box">
      <UInput
        v-model="userInput"
        placeholder="Ask me anything..."
        class="custom-input w-full"
        @keyup.enter="sendMessage"
        color="red"
      />
      <UButton
        @click="sendMessage"
        icon="i-heroicons-paper-airplane"
        color="red"
        variant="solid"
        class="custom-button"
      >
        Send
      </UButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import showdown from "showdown";

const converter = new showdown.Converter();
const chatHistory = ref([]);
const userInput = ref("");
const theme = ref("light");
const botTypingMessage = ref("");

// Toggle Light/Dark Theme
const toggleTheme = () => {
  theme.value = theme.value === "light" ? "dark" : "light";
  localStorage.setItem("theme", theme.value);
  document.documentElement.setAttribute("data-theme", theme.value);
};

// Simulate Typing Animation
const typeMessage = async (text, index) => {
  let i = 0;
  botTypingMessage.value = "";
  return new Promise((resolve) => {
    const interval = setInterval(() => {
      botTypingMessage.value += text[i];
      chatHistory.value[index].content = botTypingMessage.value;
      i++;
      if (i === text.length) {
        clearInterval(interval);
        resolve();
      }
    }, 30);
  });
};

// Send User Input
const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  chatHistory.value.push({
    role: "user",
    content: userInput.value,
    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  });

  const query = userInput.value;
  userInput.value = "";

  try {
    const res = await axios.post("http://127.0.0.1:8000/chat", { query });
    let response = res.data.response || "No response received.";

    chatHistory.value.push({
      role: "bot",
      content: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    });

    await typeMessage(response, chatHistory.value.length - 1);
  } catch (err) {
    chatHistory.value.push({
      role: "bot",
      content: "Error: Unable to fetch response.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    });
  }
};

// Greet on Load
onMounted(async () => {
  theme.value = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", theme.value);

  const greeting = "Hello! 👋 I’m Aoun, your Saudi tourism assistant. Ask me about museums or events!";
  chatHistory.value.push({ role: "bot", content: "", timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) });
  await typeMessage(greeting, 0);
});

const convertMarkdown = (text) => converter.makeHtml(text || "");
</script>






<style scoped>
/* Main Chat Container */
.chat-container {
  max-width: 600px;
  margin: auto;
  padding: 15px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.5s ease-in-out;
}

/* Chat Icon in the title */
.chat-icon {
  width: 40px; 
  height: 40px;
}

/* Bot Avatar inside the chat */
.bot-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
}


/* Chatbot Title */
.chat-title {
  text-align: center;
  font-size: 1.5em;
  color: #d32f2f;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* Message Wrapper */
.message-wrapper {
  display: flex;
  width: 100%;
  margin-bottom: 15px; /* Add spacing */
}

/* User Messages - Align Right */
.user {
  background-color: #d32f2f;
  color: white;
  padding: 10px 15px;
  border-radius: 15px 15px 0px 15px;
  max-width: 60%;
  align-self: flex-end;
  text-align: right;
  margin-left: auto; /* Push user message to the right */
}

/* Bot Messages - Align Left */
.bot {
  background-color: rgba(0, 0, 0, 0.05);
  color: black;
  padding: 15px 20px;
  border-radius: 15px 15px 15px 0px;
  max-width: 80%;
  align-self: flex-start;
  text-align: left;
  margin-right: auto;
  line-height: 1.6;
  font-size: 15px;
  font-family: 'Segoe UI', sans-serif;
  white-space: pre-wrap; /* Preserve line breaks */
  word-wrap: break-word;
  box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.1);
}

.message-content strong {
  font-weight: bold;
  display: inline-block;
  min-width: 90px;
}


/* Send Button */
.u-button {
  background-color: #d32f2f !important; /* Red button */
  color: white !important;
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 1em;
}


.custom-button {
  background-color: #d32f2f !important; /* Red */
  color: white !important; /* White text */
  border-radius: 5px;
  border: none !important;
  padding: 10px 16px;
  font-size: 1em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

/* Input Box */
.input-box {
  display: flex;
  margin-top: 10px;
  gap: 10px;
}

/* Input Field */
.w-full {
  flex-grow: 1;
}


/* Button color */
.input-box .u-button {
  background-color: #d32f2f !important; /* Red */
  color: white !important; /* White text */
  border-radius: 5px;
}

/* Hover effect */
.input-box .u-button:hover {
  background-color: #b71c1c !important; /* Darker red */
}


/* Button border */
.input-box .u-button {
  border: none !important;
}


.w-full {
  flex-grow: 1;
}



/* Light & Dark Mode */


:root {
  --bg-color-light: #f5f5f5;
  --text-color-light: black;
  --bg-color-dark: #1e1e1e;
  --text-color-dark: white;
}

.light {
  background-color: var(--bg-color-light);
  color: var(--text-color-light);
}

.dark {
  background-color: var(--bg-color-dark);
  color: var(--text-color-dark);
}

/* Chat Container */
.chat-container {
  max-width: 600px;
  margin: auto;
  padding: 15px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.5s ease-in-out;
}

/* Header with Theme Toggle */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}

/* Theme Toggle Button */
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.8rem;
  color: inherit;
  transition: transform 0.2s ease-in-out;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

/* Light Mode Icon */
.i-heroicons-moon {
  color: black; /* Change color for better visibility */
}

/* Dark Mode Icon */
.i-heroicons-sun {
  color: yellow;
}



/* Message Alignment */
.user {
  background-color: #d32f2f;
  color: white;
  padding: 10px 15px;
  border-radius: 15px 15px 0px 15px;
  max-width: 60%;
  align-self: flex-end;
  text-align: right;
  margin-left: auto;
}

/* Bot Messages - Improve formatting */
.bot {
  background-color: rgba(0, 0, 0, 0.05);
  color: black;
  padding: 15px 20px;
  border-radius: 15px 15px 15px 0px;
  max-width: 80%;
  align-self: flex-start;
  text-align: left;
  margin-right: auto;
  line-height: 1.6;
  font-size: 15px;
  font-family: 'Segoe UI', sans-serif;
  white-space: pre-wrap; /* Preserve line breaks */
  word-wrap: break-word;
  box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.1);
}


.dark .bot {
  background-color: #444;
  color: white;
}

.dark .user {
  background-color: #d32f2f;
}

/* Input and Button Styling */
.input-box {
  display: flex;
  margin-top: 10px;
  gap: 10px;
}

.w-full {
  flex-grow: 1;
}

</style>
