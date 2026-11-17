<template>
  <div class="app-container">
    <header class="app-header">
      <h1>GoodFix AI Agent</h1>
      <div class="session-controls">
        <button @click="createNewSession" class="btn btn-primary">Nowa sesja</button>
        <button @click="closeSession" class="btn btn-secondary">Zamknij sesję</button>
      </div>
    </header>

    <div class="session-status">
      <span>Session ID: {{ sessionId }}</span>
      <span>Status: {{ sessionStatus }}</span>
    </div>

    <div class="main-content">
      <div class="chat-container">
        <div class="chat-messages" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" class="message">
            <div class="message-sender">{{ message.sender }}</div>
            <div class="message-content">{{ message.content }}</div>
          </div>
        </div>

        <div class="chat-input">
          <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="Wpisz wiadomość..." />
          <button @click="sendMessage">Wyślij</button>
        </div>
      </div>

      <div class="file-upload">
        <h3>Przesyłanie plików</h3>
        <input type="file" @change="handleFileUpload" />
        <button @click="uploadFile">Prześlij plik</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      sessionId: 'default-session',
      sessionStatus: 'aktywna',
      messages: [],
      inputMessage: '',
      uploadedFile: null
    };
  },
  mounted() {
    this.initializeSession();
  },
  methods: {
    async initializeSession() {
      try {
        await axios.post(`/sessions`, {
          session_id: this.sessionId,
          context: {}
        });
        console.log('Sesja zainicjalizowana');
      } catch (error) {
        console.error('Błąd inicjalizacji sesji:', error);
      }
    },

    async createNewSession() {
      this.sessionId = `session-${Date.now()}`;
      this.messages = [];
      this.sessionStatus = 'aktywna';
      await this.initializeSession();
    },

    async closeSession() {
      try {
        await axios.delete(`/sessions/${this.sessionId}`);
        this.sessionStatus = 'zamknięta';
        console.log('Sesja zamknięta');
      } catch (error) {
        console.error('Błąd podczas zamykania sesji:', error);
      }
    },

    async sendMessage() {
      if (!this.inputMessage.trim()) return;

      try {
        const response = await axios.post('/chat', {
          session_id: this.sessionId,
          message: this.inputMessage
        });

        this.messages.push({
          sender: 'Użytkownik',
          content: this.inputMessage
        });

        this.messages.push({
          sender: 'Agent',
          content: response.data.message
        });

        this.inputMessage = '';
      } catch (error) {
        console.error('Błąd wysyłania wiadomości:', error);
      }
    },

    handleFileUpload(event) {
      this.uploadedFile = event.target.files[0];
    },

    async uploadFile() {
      if (!this.uploadedFile) return;

      const formData = new FormData();
      formData.append('file', this.uploadedFile);

      try {
        await axios.post('/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('Plik przesłany');
      } catch (error) {
        console.error('Błąd przesyłania pliku:', error);
      }
    }
  }
};
</script>

<style>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

.session-controls button {
  margin-left: 10px;
  padding: 8px 16px;
  background-color: #444;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.session-controls button:hover {
  background-color: #555;
}

.session-status {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #222;
  border-radius: 4px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 500px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: #222;
  border-radius: 4px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 4px;
}

.message-sender {
  font-weight: bold;
  color: #4caf50;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  background-color: #333;
  color: #fff;
  border: 1px solid #555;
  border-radius: 4px;
}

.chat-input button {
  padding: 10px 20px;
  background-color: #4caf50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.file-upload {
  width: 300px;
  padding: 20px;
  background-color: #222;
  border-radius: 4px;
}

.file-upload input {
  margin-bottom: 10px;
  display: block;
}

.file-upload button {
  padding: 10px 20px;
  background-color: #2196f3;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>