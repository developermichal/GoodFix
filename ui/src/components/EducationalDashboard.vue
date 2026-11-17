<template>
  <div class="educational-dashboard">
    <div class="header">
      <h1>Edukacja Eweliny</h1>
      <p>Sesja edukacyjna z Michałem Wiśniewskim</p>
    </div>
    
    <div class="session-info">
      <h3>Informacje o sesji</h3>
      <p><strong>ID sesji:</strong> {{ sessionId }}</p>
      <p><strong>Poziom nauki:</strong> {{ learningLevel }}%</p>
      <p><strong>Poziom sarkazmu:</strong> {{ sarkasmLevel }}%</p>
    </div>
    
    <div class="controls">
      <h3>Kontrola sesji</h3>
      <button @click="updateLearningLevel(10)" class="btn btn-primary">Zwiększ poziom nauki (+10%)</button>
      <button @click="updateLearningLevel(-10)" class="btn btn-secondary">Zmniejsz poziom nauki (-10%)</button>
      <button @click="updateSarkasmLevel(10)" class="btn btn-warning">Zwiększ sarkazm (+10%)</button>
      <button @click="updateSarkasmLevel(-10)" class="btn btn-info">Zmniejsz sarkazm (-10%)</button>
      <button @click="closeSession" class="btn btn-danger">Zamknij sesję</button>
    </div>
    
    <div class="learning-materials">
      <h3>Materiały edukacyjne</h3>
      <div class="material-list">
        <div v-for="material in materials" :key="material.title" class="material-item">
          <strong>{{ material.title }}</strong><br>
          {{ material.content }}
        </div>
      </div>
      <button @click="addMaterial" class="btn btn-success">Dodaj materiał</button>
    </div>
    
    <div class="chat">
      <h3>Chat edukacyjny</h3>
      <div class="chat-history" ref="chatHistory">
        <div v-for="message in messages" :key="message.id" class="message" :class="message.type">
          <strong>{{ message.sender }}:</strong> {{ message.content }}
        </div>
      </div>
      <div class="input-group">
        <input v-model="userMessage" type="text" class="form-control" placeholder="Wpisz wiadomość...">
        <button @click="sendMessage" class="btn btn-primary">Wyślij</button>
      </div>
    </div>
    
    <div class="personality-analysis">
      <h3>Analiza kontekstu osobowości</h3>
      <div class="analysis-content">
        <pre>{{ JSON.stringify(personalityAnalysis, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EducationalDashboard',
  data() {
    return {
      sessionId: '',
      learningLevel: 0,
      sarkasmLevel: 1,
      materials: [],
      messages: [],
      userMessage: '',
      personalityAnalysis: {}
    }
  },
  mounted() {
    // Pobierz ID sesji z parametrów URL
    this.sessionId = this.$route.params.sessionId || 'default-session';
    this.loadSessionData();
    this.loadMaterials();
    this.loadPersonalityAnalysis();
  },
  methods: {
    async loadSessionData() {
      try {
        const response = await fetch(`/api/session/${this.sessionId}`);
        const data = await response.json();
        this.learningLevel = data.learning_level || 0;
        this.sarkasmLevel = data.sarkasm_level || 1;
      } catch (error) {
        console.error('Błąd podczas ładowania danych sesji:', error);
      }
    },
    
    async updateLearningLevel(change) {
      try {
        const response = await fetch(`/api/session/${this.sessionId}/learning`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({change: change})
        });
        const data = await response.json();
        this.learningLevel = data.learning_level;
      } catch (error) {
        console.error('Błąd podczas aktualizacji poziomu nauki:', error);
      }
    },
    
    async updateSarkasmLevel(change) {
      try {
        const response = await fetch(`/api/session/${this.sessionId}/sarkasm`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({change: change})
        });
        const data = await response.json();
        this.sarkasmLevel = data.sarkasm_level;
      } catch (error) {
        console.error('Błąd podczas aktualizacji poziomu sarkazmu:', error);
      }
    },
    
    async addMaterial() {
      const title = prompt('Tytuł materiału:');
      const content = prompt('Treść materiału:');
      
      if (title && content) {
        try {
          await fetch(`/api/session/${this.sessionId}/materials`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              type: 'books',
              title: title,
              content: content
            })
          });
          
          this.loadMaterials();
        } catch (error) {
          console.error('Błąd podczas dodawania materiału:', error);
        }
      }
    },
    
    async loadMaterials() {
      try {
        const response = await fetch(`/api/session/${this.sessionId}/materials`);
        const data = await response.json();
        this.materials = data.materials || [];
      } catch (error) {
        console.error('Błąd podczas ładowania materiałów:', error);
      }
    },
    
    async sendMessage() {
      if (!this.userMessage.trim()) return;
      
      // Dodaj wiadomość użytkownika
      const userMessage = {
        id: Date.now(),
        sender: 'Użytkownik',
        content: this.userMessage,
        type: 'user-message'
      };
      this.messages.push(userMessage);
      
      try {
        const response = await fetch(`/api/session/${this.sessionId}/chat`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message: this.userMessage})
        });
        
        const data = await response.json();
        
        // Dodaj odpowiedź agenta
        const agentMessage = {
          id: Date.now() + 1,
          sender: 'Michał',
          content: data.response,
          type: 'agent-message'
        };
        this.messages.push(agentMessage);
        
        // Wyczyść pole wiadomości
        this.userMessage = '';
        
        // Przewiń do końca
        this.$nextTick(() => {
          const chatHistory = this.$refs.chatHistory;
          if (chatHistory) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
          }
        });
      } catch (error) {
        console.error('Błąd podczas wysyłania wiadomości:', error);
      }
    },
    
    async loadPersonalityAnalysis() {
      try {
        const response = await fetch(`/api/session/${this.sessionId}/personality`);
        const data = await response.json();
        this.personalityAnalysis = data.analysis || {};
      } catch (error) {
        console.error('Błąd podczas ładowania analizy kontekstu:', error);
      }
    },
    
    async closeSession() {
      if (confirm('Czy na pewno chcesz zamknąć sesję?')) {
        try {
          await fetch(`/api/session/${this.sessionId}/close`, {method: 'POST'});
          this.$router.push('/');
        } catch (error) {
          console.error('Błąd podczas zamykania sesji:', error);
        }
      }
    }
  }
}
</script>

<style scoped>
.educational-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.session-info {
  background: #e8f4f8;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
}

.controls {
  margin: 20px 0;
}

.btn {
  margin: 5px;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-warning { background: #ffc107; color: black; }
.btn-info { background: #17a2b8; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-success { background: #28a745; color: white; }

.learning-materials {
  margin: 20px 0;
}

.material-item {
  padding: 10px;
  margin: 5px 0;
  background: #f9f9f9;
  border-radius: 3px;
}

.chat {
  margin: 20px 0;
}

.chat-history {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  padding: 10px;
  margin: 10px 0;
  background: #f9f9f9;
}

.message {
  margin: 10px 0;
  padding: 10px;
  border-radius: 5px;
}

.user-message {
  background: #e3f2fd;
  text-align: right;
}

.agent-message {
  background: #f5f5f5;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.form-control {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.analysis-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
}
</style>