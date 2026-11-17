<template>
  <div class="app-container">
    <header class="header">
      <h1>GoodFix AI Agent</h1>
      <div class="settings-panel">
        <label for="scale">Skala:</label>
        <input id="scale" v-model.number="scale" type="range" min="1" max="100" @input="updateScale">
        <span>{{ scale }}%</span>
      </div>
    </header>

    <div class="main-content">
      <div class="context-panel">
        <h2>Kontekst Pracy</h2>
        <div class="context-items">
          <div v-for="(item, key) in contextItems" :key="key" class="context-item">
            <strong>{{ key }}:</strong>
            <p>{{ item }}</p>
          </div>
        </div>
        <button @click="clearContext" class="btn btn-danger">Wyczyść Kontekst</button>
      </div>

      <div class="chat-panel">
        <div class="chat-messages" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" class="message">
            <div class="message-sender">{{ message.sender }}:</div>
            <div class="message-content">{{ message.content }}</div>
          </div>
        </div>

        <div class="chat-input">
          <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="Wpisz wiadomość..." />
          <button @click="sendMessage">Wyślij</button>
        </div>

        <div class="file-upload">
          <input type="file" @change="handleFileUpload" />
          <button @click="uploadFile">Prześlij plik</button>
        </div>
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
      inputMessage: '',
      messages: [
        {
          sender: 'System',
          content: 'Witaj w GoodFix AI Agent. Możesz zadać pytanie, przesłać plik lub zarządzać kontekstem.'
        }
      ],
      scale: 25,
      contextItems: {},
      uploadedFile: null
    };
  },
  mounted() {
    this.loadContext();
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim()) return;

      // Dodaj wiadomość użytkownika
      this.messages.push({
        sender: 'Użytkownik',
        content: this.inputMessage
      });

      try {
        const response = await axios.post('http://localhost:8000/chat', {
          message: this.inputMessage,
          context: JSON.stringify(this.contextItems)
        });

        // Dodaj odpowiedź agenta
        this.messages.push({
          sender: 'Agent',
          content: response.data.response
        });

        // Sprawdź czy odpowiedź zawiera informacje o kontekście
        if (response.data.response.includes('kontekst')) {
          this.loadContext();
        }
      } catch (error) {
        console.error('Błąd podczas wysyłania wiadomości:', error);
        this.messages.push({
          sender: 'Błąd',
          content: 'Wystąpił błąd podczas przetwarzania zapytania'
        });
      }

      this.inputMessage = '';
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.uploadedFile = {
            name: file.name,
            content: e.target.result
          };
        };
        reader.readAsText(file);
      }
    },
    async uploadFile() {
      if (!this.uploadedFile) return;

      try {
        const response = await axios.post('http://localhost:8000/upload_file', {
          file_type: 'text',
          content: this.uploadedFile.content
        });

        this.messages.push({
          sender: 'System',
          content: response.data.message
        });
      } catch (error) {
        console.error('Błąd podczas przesyłania pliku:', error);
        this.messages.push({
          sender: 'Błąd',
          content: 'Wystąpił błąd podczas przesyłania pliku'
        });
      }
    },
    async loadContext() {
      try {
        // W tym miejscu można dodać logikę do pobierania kontekstu z backendu
        // Na potrzeby prototypu ustawiamy przykładowe dane
        this.contextItems = {
          'Projekt': 'GoodFix',
          'Zadanie': 'Integracja systemów AI',
          'Status': 'W toku'
        };
      } catch (error) {
        console.error('Błąd podczas ładowania kontekstu:', error);
      }
    },
    clearContext() {
      this.contextItems = {};
      this.messages.push({
        sender: 'System',
        content: 'Kontekst został wyczyszczony'
      });
    },
    updateScale() {
      // Wysyłanie zmiany skali do backendu
      axios.post('http://localhost:8000/settings', {
        scale: this.scale
      }).then(response => {
        console.log(response.data.message);
      }).catch(error => {
        console.error('Błąd podczas aktualizacji ustawień:', error);
      });
    }
  }
};
</script>

<style>
.app-container {
  font-family: 'Courier New', monospace;
  background-color: #0a0a0a;
  color: #00ff00;
  min-height: 100vh;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #00ff00;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.settings-panel {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-panel input[type="range"] {
  width: 100px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.context-panel {
  flex: 1;
  background-color: #111;
  border: 1px solid #00ff00;
  padding: 15px;
  border-radius: 5px;
}

.chat-panel {
  flex: 3;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-messages {
  flex: 1;
  background-color: #111;
  border: 1px solid #00ff00;
  padding: 15px;
  border-radius: 5px;
  overflow-y: auto;
  max-height: 400px;
}

.message {
  margin-bottom: 10px;
  padding: 5px;
  border-radius: 3px;
}

.message-sender {
  font-weight: bold;
  color: #00ff00;
}

.message-content {
  color: #fff;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  background-color: #111;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 10px;
  border-radius: 3px;
}

.chat-input button {
  background-color: #00ff00;
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 3px;
  cursor: pointer;
}

.file-upload {
  display: flex;
  gap: 10px;
  align-items: center;
}

.file-upload input {
  flex: 1;
}

.file-upload button {
  background-color: #00ff00;
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 3px;
  cursor: pointer;
}

.btn {
  background-color: #00ff00;
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 3px;
  cursor: pointer;
}

.btn-danger {
  background-color: #ff0000;
  color: #fff;
}

.context-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #222;
  border-radius: 3px;
}

.context-item strong {
  color: #00ff00;
}
</style>