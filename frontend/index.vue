// Landing page 
<template>
  <div class="welcome-container">
    <div class="welcome-box">
      <img src="/chatbot.png" alt="Aoun Bot" class="chatbot-icon" />
      <h1>Aoun Bot</h1>
      <p>Your AI assistant in Saudi Arabia.</p>
      
      <button @click="startChat" class="start-button">Start Chat</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const startChat = () => {
  router.push("/chat"); // Navigate to Chat Page
};
</script>

<style scoped>
/* Centered Box */
.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f5f5;
}

/* Welcome Box */
.welcome-box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 350px;
}


/* Chatbot Icon */
.chatbot-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 10px;
  display: block;
}


/* Heading */
h1 {
  color: #d32f2f;
  font-size: 24px;
}

/* Description */
p {
  color: gray;
  margin-bottom: 20px;
}

/* Start Button */
.start-button {
  padding: 12px 20px;
  background-color: #d32f2f;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: 0.3s;
}

.start-button:hover {
  background-color: #b71c1c;
}
</style>
