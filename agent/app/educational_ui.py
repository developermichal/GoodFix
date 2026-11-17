from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

from agent.app.educational_agent import educational_agent

app = Flask(__name__)

# Szablon HTML dla interfejsu edukacyjnego
EDUCATIONAL_UI_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Edukacja Eweliny</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; }
        .session-info { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .learning-materials { margin: 20px 0; }
        .material-item { padding: 10px; margin: 5px 0; background: #f9f9f9; border-radius: 3px; }
        .controls { margin: 20px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        .chat-history { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin: 10px 0; background: #f9f9f9; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #e3f2fd; text-align: right; }
        .agent-message { background: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Edukacja Eweliny</h1>
            <p>Sesja edukacyjna z Michałem Wiśniewskim</p>
        </div>
        
        <div class="session-info">
            <h3>Informacje o sesji</h3>
            <p><strong>ID sesji:</strong> <span id="session-id">{{ session_id }}</span></p>
            <p><strong>Poziom nauki:</strong> <span id="learning-level">{{ learning_level }}%</span></p>
            <p><strong>Poziom sarkazmu:</strong> <span id="sarkasm-level">{{ sarkasm_level }}%</span></p>
        </div>
        
        <div class="controls">
            <h3>Kontrola sesji</h3>
            <button onclick="updateLearningLevel(10)">Zwiększ poziom nauki (+10%)</button>
            <button onclick="updateLearningLevel(-10)">Zmniejsz poziom nauki (-10%)</button>
            <button onclick="updateSarkasmLevel(10)">Zwiększ sarkazm (+10%)</button>
            <button onclick="updateSarkasmLevel(-10)">Zmniejsz sarkazm (-10%)</button>
            <button onclick="closeSession()">Zamknij sesję</button>
        </div>
        
        <div class="learning-materials">
            <h3>Materiały edukacyjne</h3>
            <div id="materials-list">
                <!-- Materiały będą dodawane tutaj dynamicznie -->
            </div>
            <button onclick="addMaterial()">Dodaj materiał</button>
        </div>
        
        <div class="chat">
            <h3>Chat edukacyjny</h3>
            <div class="chat-history" id="chat-history">
                <!-- Historia rozmowy będzie dodawana tutaj -->
            </div>
            <input type="text" id="user-input" placeholder="Wpisz wiadomość...">
            <button onclick="sendMessage()">Wyślij</button>
        </div>
        
        <div class="personality-analysis">
            <h3>Analiza kontekstu osobowości</h3>
            <div id="personality-analysis">
                <!-- Analiza kontekstu osobowości będzie dodawana tutaj -->
            </div>
        </div>
    </div>
    
    <script>
        const sessionId = '{{ session_id }}';
        
        // Funkcje do zarządzania sesją
        function updateLearningLevel(change) {
            fetch('/api/session/' + sessionId + '/learning', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change: change})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('learning-level').textContent = data.learning_level + '%';
            });
        }
        
        function updateSarkasmLevel(change) {
            fetch('/api/session/' + sessionId + '/sarkasm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change: change})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('sarkasm-level').textContent = data.sarkasm_level + '%';
            });
        }
        
        function closeSession() {
            if (confirm('Czy na pewno chcesz zamknąć sesję?')) {
                fetch('/api/session/' + sessionId + '/close', {
                    method: 'POST'
                })
                .then(response => {
                    if (response.ok) {
                        alert('Sesja została zamknięta');
                        window.close();
                    }
                });
            }
        }
        
        // Funkcje do zarządzania materiałami
        function addMaterial() {
            const title = prompt('Tytuł materiału:');
            const content = prompt('Treść materiału:');
            
            if (title && content) {
                fetch('/api/session/' + sessionId + '/materials', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        type: 'books',
                        title: title,
                        content: content
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert('Materiał dodany');
                    loadMaterials();
                });
            }
        }
        
        function loadMaterials() {
            fetch('/api/session/' + sessionId + '/materials')
            .then(response => response.json())
            .then(data => {
                const materialsList = document.getElementById('materials-list');
                materialsList.innerHTML = '';
                data.materials.forEach(material => {
                    const item = document.createElement('div');
                    item.className = 'material-item';
                    item.innerHTML = `<strong>${material.title}</strong><br>${material.content}`;
                    materialsList.appendChild(item);
                });
            });
        }
        
        // Funkcje do chatu
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (message) {
                // Dodaj wiadomość użytkownika do historii
                const chatHistory = document.getElementById('chat-history');
                const userMessage = document.createElement('div');
                userMessage.className = 'message user-message';
                userMessage.textContent = 'Użytkownik: ' + message;
                chatHistory.appendChild(userMessage);
                
                // Wyślij wiadomość do agenta
                fetch('/api/session/' + sessionId + '/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => {
                    // Dodaj odpowiedź agenta do historii
                    const agentMessage = document.createElement('div');
                    agentMessage.className = 'message agent-message';
                    agentMessage.textContent = 'Michał: ' + data.response;
                    chatHistory.appendChild(agentMessage);
                    
                    // Przewiń do końca
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                });
                
                input.value = '';
            }
        }
        
        // Funkcje do analizy kontekstu osobowości
        function loadPersonalityAnalysis() {
            fetch('/api/session/' + sessionId + '/personality')
            .then(response => response.json())
            .then(data => {
                const analysisDiv = document.getElementById('personality-analysis');
                analysisDiv.innerHTML = '<pre>' + JSON.stringify(data.analysis, null, 2) + '</pre>';
            });
        }
        
        // Inicjalizacja
        loadMaterials();
        loadPersonalityAnalysis();
    </script>
</body>
</html>
'''

@app.route('/educational/<session_id>')
def educational_dashboard(session_id):
    # Sprawdź czy sesja istnieje
    status = educational_agent.get_session_status(session_id)
    if not status:
        return "Sesja nie istnieje", 404
    
    return render_template_string(
        EDUCATIONAL_UI_TEMPLATE,
        session_id=session_id,
        learning_level=status.get('learning_level', 0),
        sarkasm_level=status.get('sarkasm_level', 1)
    )

@app.route('/api/session/<session_id>/learning', methods=['POST'])
def update_learning_level(session_id):
    data = request.get_json()
    change = data.get('change', 0)
    
    # Pobierz aktualny poziom
    status = educational_agent.get_session_status(session_id)
    current_level = status.get('learning_level', 0)
    
    # Aktualizuj poziom
    new_level = max(0, min(100, current_level + change))
    educational_agent.update_learning_level(session_id, new_level)
    
    return jsonify({'learning_level': new_level})

@app.route('/api/session/<session_id>/sarkasm', methods=['POST'])
def update_sarkasm_level(session_id):
    data = request.get_json()
    change = data.get('change', 0)
    
    # Pobierz aktualny poziom
    status = educational_agent.get_session_status(session_id)
    current_level = status.get('sarkasm_level', 1)
    
    # Aktualizuj poziom
    new_level = max(1, min(100, current_level + change))
    educational_agent.update_sarkasm_level(session_id, new_level)
    
    return jsonify({'sarkasm_level': new_level})

@app.route('/api/session/<session_id>/materials', methods=['POST'])
def add_material(session_id):
    data = request.get_json()
    
    educational_agent.add_learning_material(
        session_id,
        data.get('type', 'books'),
        data.get('title', ''),
        data.get('content', '')
    )
    
    return jsonify({'status': 'success'})

@app.route('/api/session/<session_id>/materials', methods=['GET'])
def get_materials(session_id):
    materials = educational_agent.get_learning_materials('books')
    return jsonify({'materials': materials})

@app.route('/api/session/<session_id>/chat', methods=['POST'])
def chat(session_id):
    data = request.get_json()
    message = data.get('message', '')
    
    response = educational_agent.generate_response(session_id, message)
    
    return jsonify({'response': response})

@app.route('/api/session/<session_id>/personality', methods=['GET'])
def get_personality_analysis(session_id):
    analysis = educational_agent.get_personality_analysis(session_id)
    return jsonify({'analysis': analysis})

@app.route('/api/session/<session_id>/close', methods=['POST'])
def close_session(session_id):
    educational_agent.close_session(session_id)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)