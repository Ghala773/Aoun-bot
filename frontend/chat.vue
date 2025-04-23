<template>
  <div :class="theme" class="chat-container">
    <div class="header">
      <h2 class="chat-title">
        <img src="/chatbot.png" alt="Chatbot Icon" class="chat-icon" />
        Aoun Bot
      </h2>
      <div class="header-controls">
        <button @click="toggleTheme" class="theme-toggle">
          <i :class="theme === 'light' ? 'i-heroicons-moon' : 'i-heroicons-sun'"></i>
        </button>
        <button @click="clearChat" class="clear-button" title="Clear conversation">
          <i class="i-heroicons-trash"></i>
        </button>
      </div>
    </div>

    <div class="chat-messages">
      <div v-for="(message, index) in chatHistory" :key="index" class="message-wrapper">
        <div class="message" :class="message.role">
          <img v-if="message.role === 'bot'" src="/chatbot.png" class="bot-avatar" />
          <div class="message-content">
            <p v-html="convertMarkdown(message.content)"></p>
            <span class="timestamp">{{ message.timestamp }}</span>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="loading-indicator">
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>

    <div class="input-box">
      <UInput
        v-model="userInput"
        placeholder="Ask me about events, museums, or places in Saudi Arabia..."
        class="custom-input w-full"
        @keyup.enter="sendMessage"
        color="red"
        :disabled="isLoading"
        autocomplete="off"
        autofocus
      />
      <UButton
        @click="sendMessage"
        icon="i-heroicons-paper-airplane"
        color="red"
        variant="solid"
        class="custom-button"
        :disabled="isLoading || !userInput.trim()"
        :loading="isLoading"
      >
        Send
      </UButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import axios from "axios";
import showdown from "showdown";
import { useToast } from "#imports";

const converter = new showdown.Converter({
  simplifiedAutoLink: true,
  tasklists: true,
  emoji: true
});

const chatHistory = ref([]);
const userInput = ref("");
const theme = ref("light");
const isLoading = ref(false);
const error = ref(null);
const sessionId = ref(Date.now().toString());
const abortController = ref(null);
const toast = useToast();

// Initialize with default greeting
const initialGreeting = `Hello! 👋 I'm Aoun, your Saudi tourism assistant. You can ask me about tourism attraction, events and museums in Saudi Arabia`;

// Theme management
const toggleTheme = () => {
  theme.value = theme.value === "light" ? "dark" : "light";
  localStorage.setItem("theme", theme.value);
  document.documentElement.setAttribute("data-theme", theme.value);
};

// Load/save chat history
const loadChatHistory = () => {
  const saved = localStorage.getItem(`chatHistory_${sessionId.value}`);
  if (saved) {
    try {
      chatHistory.value = JSON.parse(saved);
    } catch (e) {
      console.error("Error loading chat history:", e);
    }
  }
};

const saveChatHistory = () => {
  localStorage.setItem(
    `chatHistory_${sessionId.value}`,
    JSON.stringify(chatHistory.value)
  );
};

// Clear chat history
const clearChat = () => {
  chatHistory.value = [];
  sessionId.value = Date.now().toString();
  saveChatHistory();
  toast.add({
    title: 'Conversation cleared',
    timeout: 2000
  });
};

// Handle special commands
const handleSpecialCommands = (input) => {
  const cmd = input.toLowerCase().trim();
  
  if (cmd === '/clear') {
    clearChat();
    return true;
  }
  
  if (cmd === '/help') {
    chatHistory.value.push({
      role: "bot",
      content: `Available commands:
/clear - Reset conversation
/help - Show this help

Try asking about:
- Events in [city]
- Museums in [city]
- Places to visit in [region]`,
      timestamp: getCurrentTime()
    });
    return true;
  }
  
  return false;
};

// Typing animation
const typeMessage = async (text, index) => {
  let i = 0;
  let typingMessage = "";
  chatHistory.value[index].content = "";
  
  return new Promise((resolve) => {
    const interval = setInterval(() => {
      typingMessage += text[i];
      chatHistory.value[index].content = typingMessage;
      i++;
      
      if (i === text.length) {
        clearInterval(interval);
        resolve();
      }
    }, 20);
  });
};

// Get current time for timestamps
const getCurrentTime = () => {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

// Clean up pending requests
const cleanupRequest = () => {
  if (abortController.value) {
    abortController.value.abort();
    abortController.value = null;
  }
  isLoading.value = false;
};

// Markdown conversion
const convertMarkdown = (text) => {
  return converter.makeHtml(text || "");
};

// Scroll to bottom of chat
const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.chat-messages');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
};

// Main message sending function
const sendMessage = async () => {
  const inputText = userInput.value.trim();
  if (!inputText || isLoading.value) return;

  // Handle special commands
  if (handleSpecialCommands(inputText)) {
    userInput.value = "";
    scrollToBottom();
    return;
  }

  // Clean up any pending request
  cleanupRequest();

  // Clear previous errors
  error.value = null;
  
  // Add user message to chat
  chatHistory.value.push({
    role: "user",
    content: inputText,
    timestamp: getCurrentTime()
  });

  userInput.value = "";
  isLoading.value = true;
  saveChatHistory();

  // Create new AbortController
  abortController.value = new AbortController();

  try {
    // Add loading message
    const loadingIndex = chatHistory.value.push({
      role: "bot",
      content: "",
      timestamp: getCurrentTime()
    }) - 1;

    const response = await axios.post(
      "http://localhost:8000/chat",
      { 
        query: inputText,
        conversation_id: sessionId.value
      },
      {
        signal: abortController.value.signal,
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    );

    if (!response.data?.response) {
      throw new Error("Empty response from server");
    }

    // Update the loading message with actual response
    chatHistory.value[loadingIndex].content = response.data.response;
    await typeMessage(response.data.response, loadingIndex);
    
  } catch (err) {
    if (!axios.isCancel(err)) {
      console.error("API Error:", err);
      
      // Remove empty loading message if exists
      if (chatHistory.value.length > 0 && chatHistory.value[chatHistory.value.length - 1].content === "") {
        chatHistory.value.pop();
      }
      
      // Set appropriate error message
      let errorMessage = "Sorry, something went wrong.";
      if (err.message.includes("timeout")) {
        errorMessage = "The request took too long. Please try again.";
      } else if (err.response) {
        errorMessage = "Server error occurred. Please try again later.";
      } else if (err.request) {
        errorMessage = "Network error. Please check your connection.";
      }

      error.value = errorMessage;
      chatHistory.value.push({
        role: "bot",
        content: errorMessage,
        timestamp: getCurrentTime()
      });
    }
  } finally {
    isLoading.value = false;
    abortController.value = null;
    saveChatHistory();
    scrollToBottom();
  }
};

// Initialize component
onMounted(async () => {
  // Set theme
  theme.value = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", theme.value);

  // Load chat history
  loadChatHistory();

  // Add initial greeting if new session
  if (chatHistory.value.length === 0) {
    chatHistory.value.push({ 
      role: "bot", 
      content: "", 
      timestamp: getCurrentTime() 
    });
    await typeMessage(initialGreeting, 0);
    saveChatHistory();
  }

  // Scroll to bottom initially
  scrollToBottom();
});

// Clean up on component unmount
onUnmounted(() => {
  cleanupRequest();
});

// Watch for chat history changes to scroll
watch(chatHistory, () => {
  scrollToBottom();
}, { deep: true });
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
  display: flex;
  flex-direction: column;
  height: 90vh;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.header-controls {
  display: flex;
  gap: 10px;
}

/* Chat Messages Area */
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 15px;
}

/* Chat Icon in the title */
.chat-icon {
  width: 40px; 
  height: 40px;
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
  margin: 0;
}

/* Bot Avatar */
.bot-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
}

/* Messages */
.message-wrapper {
  display: flex;
  width: 100%;
  margin-bottom: 15px;
}

.user {
  background-color: #d32f2f;
  color: white;
  padding: 10px 15px;
  border-radius: 15px 15px 0px 15px;
  max-width: 80%;
  align-self: flex-end;
  text-align: right;
  margin-left: auto;
}

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
  white-space: pre-wrap;
  word-wrap: break-word;
  box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.1);
}

/* Dark Mode */
.dark .bot {
  background-color: #444;
  color: white;
}

.dark .user {
  background-color: #d32f2f;
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  justify-content: center;
  padding: 10px;
}

.loading-dots {
  display: flex;
  gap: 5px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d32f2f;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
}

/* Error Message */
.error-message {
  color: #d32f2f;
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  background-color: rgba(211, 47, 47, 0.1);
  text-align: center;
}

/* Input Box */
.input-box {
  display: flex;
  margin-top: auto;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.custom-button {
  background-color: #d32f2f !important;
  color: white !important;
  border-radius: 5px;
  border: none !important;
  padding: 10px 16px;
  font-size: 1em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  min-width: 80px;
}

.custom-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.w-full {
  flex-grow: 1;
}

/* Theme Toggle */
.theme-toggle, .clear-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: inherit;
  transition: transform 0.2s ease-in-out;
  padding: 5px;
}

.theme-toggle:hover, .clear-button:hover {
  transform: scale(1.1);
}

/* Clear Button */
.clear-button {
  color: #d32f2f;
}

/* Timestamp */
.timestamp {
  display: block;
  font-size: 0.8em;
  opacity: 0.7;
  margin-top: 5px;
}

/* Markdown content */
.message-content :deep(p) {
  margin: 0;
}

.message-content :deep(strong) {
  font-weight: bold;
}

.message-content :deep(a) {
  color: #d32f2f;
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #d32f2f;
  border-radius: 10px;
}

.dark .chat-messages::-webkit-scrollbar-thumb {
  background: #f44336;
}
</style>