<script setup>
import { ref, onMounted } from 'vue'

const api = import.meta.env.VITE_AGENT_API || 'http://localhost:8001'
const sessionId = ref(null)
const workspace = ref('.')
const tree = ref([])
const selected = ref(null)
const content = ref('')
const message = ref('')
const answer = ref('')
const ragCount = ref(0)
const toolCalls = ref([])
const busy = ref(false)
const sessions = ref([])
const pdfInput = ref(null)
const settings = ref(null)
const showSettings = ref(false)

async function createSession() {
  const response = await fetch(`${api}/api/sessions`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({workspace: workspace.value}) })
  const data = await response.json(); sessionId.value = data.session_id; await loadTree()
}
async function loadSessions() { sessions.value = await (await fetch(`${api}/api/sessions`)).json() }
async function openSession(id) {
  if (!id) return
  const data = await (await fetch(`${api}/api/sessions/${id}`)).json()
  sessionId.value = data.session_id; workspace.value = data.context.workspace || '.'; await loadTree()
}
async function uploadPdf() {
  if (!pdfInput.value?.files?.[0]) return
  const form = new FormData(); form.append('file', pdfInput.value.files[0])
  await fetch(`${api}/api/knowledge/pdf`, {method:'POST', body: form}); pdfInput.value.value = ''
}
async function loadTree() { tree.value = await (await fetch(`${api}/api/tree?path=${encodeURIComponent(workspace.value)}`)).json() }
async function loadSettings() { settings.value = await (await fetch(`${api}/api/settings`)).json() }
async function openFile(path) { selected.value = path; content.value = (await (await fetch(`${api}/api/file?path=${encodeURIComponent(workspace.value + '/' + path)}`)).json()).content }
async function saveFile() { await fetch(`${api}/api/file`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: workspace.value + '/' + selected.value, content: content.value})}); await loadTree() }
async function send() {
  if (!message.value || !sessionId.value) return
  busy.value = true
  const data = await (await fetch(`${api}/api/chat`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id: sessionId.value, message: message.value})})).json()
  answer.value = data.answer; ragCount.value = data.rag_count; toolCalls.value = data.tool_calls || []; message.value = ''; busy.value = false
}
function actionTitle(call) {
  const labels = { write_file: 'Utworzono lub zapisano plik', patch_file: 'Zmieniono plik', read_file: 'Odczytano plik', list_tree: 'Przeanalizowano strukturę' }
  return labels[call.name] || `Wykonano ${call.name}`
}
function actionPath(call) { return call.arguments?.path || call.arguments?.relative_path || '' }
onMounted(async () => { await createSession(); await loadSessions(); await loadSettings() })
</script>

<template>
  <div class="app-shell">
    <nav class="navbar navbar-dark bg-dark px-3 py-2 gap-2 app-toolbar">
      <span class="navbar-brand mb-0">GoodFix Agent</span>
      <input v-model="workspace" class="form-control workspace-input" placeholder="Katalog workspace"/>
      <button class="btn btn-outline-light" @click="createSession">Nowa sesja</button>
      <select class="form-select session-select" @change="openSession($event.target.value)"><option value="">Otwórz sesję</option><option v-for="item in sessions" :key="item.session_id" :value="item.session_id">{{ item.session_id }}</option></select>
      <input ref="pdfInput" type="file" accept="application/pdf" class="form-control pdf-input"/>
      <button class="btn btn-warning" @click="uploadPdf">Dodaj PDF do RAG</button>
      <button class="btn btn-outline-info settings-button" @click="showSettings = !showSettings">Ustawienia</button>
    </nav>
    <section v-if="showSettings" class="settings-panel card shadow" aria-label="Ustawienia agenta">
      <div class="card-header d-flex justify-content-between align-items-center"><strong>Ustawienia z .env</strong><button class="btn btn-sm btn-outline-secondary" @click="showSettings = false">Zamknij</button></div>
      <div v-if="settings" class="settings-grid">
        <div><span>Model</span><code>{{ settings.model }}</code></div>
        <div><span>Kontekst</span><code>{{ settings.context_tokens }} tokenów</code></div>
        <div><span>Warstwy GPU</span><code>{{ settings.gpu_layers }}</code></div>
        <div><span>Podział GPU</span><code>{{ settings.tensor_split }}</code></div>
        <div><span>Autosave</span><code>{{ settings.autosave_seconds }} s</code></div>
        <div><span>Chroma</span><code>{{ settings.chroma }}</code></div>
      </div>
      <div v-else class="p-3 text-muted">Ładowanie ustawień...</div>
    </section>
    <main class="container-fluid py-3 workspace-main"><div class="row g-3 workspace-row">
      <aside class="col-12 col-lg-3 panel-column"><div class="card panel"><div class="card-header panel-title">Explorer <span class="badge bg-secondary">{{ tree.length }}</span></div><div class="list-group list-group-flush file-list"><button v-for="item in tree.filter(x => x.kind === 'file')" :key="item.path" class="list-group-item list-group-item-action" @click="openFile(item.path)">{{ item.path }}</button></div></div></aside>
      <section class="col-12 col-lg-5 panel-column"><div class="card panel"><div class="card-header panel-title d-flex justify-content-between align-items-center"><span>{{ selected || 'Edytor pliku' }}</span><button v-if="selected" class="btn btn-sm btn-primary" @click="saveFile">Zapisz</button></div><textarea v-model="content" class="form-control code-editor" spellcheck="false" placeholder="Wybierz plik w Explorerze..."></textarea></div></section>
      <section class="col-12 col-lg-4 panel-column"><div class="card panel"><div class="card-header panel-title">Chat <span class="badge bg-secondary">RAG: {{ ragCount }}</span><span class="badge bg-info ms-1">Calls: {{ toolCalls.length }}</span></div><div class="card-body chat-body"><pre v-if="answer" class="answer">{{ answer }}</pre><section v-if="toolCalls.length" class="tool-calls" aria-label="Wykonane funkcje"><div class="tool-calls-title">Wykonane funkcje agenta ({{ toolCalls.length }})</div><article v-for="(call, index) in toolCalls" :key="index" class="tool-call"><div class="tool-call-heading"><strong>{{ actionTitle(call) }}</strong><code v-if="actionPath(call)">{{ actionPath(call) }}</code></div><div class="tool-result">{{ call.result || 'Funkcja wykonana.' }}</div><details class="technical-details"><summary>Szczegóły techniczne</summary><pre>{{ JSON.stringify(call.arguments, null, 2) }}</pre></details></article></section><textarea v-model="message" class="form-control message-box" placeholder="Opisz zmianę lub zadaj pytanie..."></textarea><button class="btn btn-success mt-3 w-100 send-button" :disabled="busy" @click="send">{{ busy ? 'Pracuję...' : 'Wyślij' }}</button></div></div></section>
    </div></main>
  </div>
</template>

<style>
:global(html), :global(body), :global(#app) { height: 100%; margin: 0; }
:global(body) { min-width: 900px; background: #f4f6f9; font-size: 16px; overflow: hidden; }
.app-shell { font-size: 150%; }
.app-shell { height: 100vh; display: flex; flex-direction: column; }
.app-toolbar { flex: 0 0 auto; min-height: 64px; }
.workspace-input { width: min(28vw, 360px); }
.session-select { width: 180px; }
.pdf-input { width: min(22vw, 300px); }
.workspace-main { flex: 1 1 auto; min-height: 0; }
.workspace-row { height: 100%; min-height: 0; display: grid; grid-template-columns: minmax(220px, 0.9fr) minmax(420px, 1.8fr) minmax(360px, 1.25fr); gap: 1rem; margin: 0; }
.workspace-row > .panel-column { width: auto; padding: 0; }
.panel-column { display: flex; min-height: 0; }
.panel { width: 100%; min-height: 0; display: flex; flex-direction: column; }
.panel-title { min-height: 48px; font-weight: 600; font-size: 1rem; }
.file-list { overflow: auto; min-height: 0; }
.code-editor { flex: 1 1 auto; min-height: 0; resize: none; border: 0; border-radius: 0 0 var(--bs-border-radius) var(--bs-border-radius); padding: 1rem; font: 0.95rem/1.5 Consolas, 'Courier New', monospace; }
.chat-body { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
.answer { flex: 1 1 auto; min-height: 120px; margin-bottom: 1rem; padding: 1rem; white-space: pre-wrap; overflow: auto; background: #f8f9fa; border-radius: .375rem; }
.message-box { min-height: 150px; resize: vertical; font-size: 1rem; }
.send-button { min-height: 44px; }
.settings-button { margin-left: auto; white-space: nowrap; }
.settings-panel { position: fixed; z-index: 20; top: 70px; right: 1rem; width: min(560px, calc(100vw - 2rem)); }
.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; padding: 1rem; }
.settings-grid div { display: flex; flex-direction: column; gap: .2rem; padding: .65rem; background: #f8f9fa; border-radius: .375rem; }
.settings-grid span { color: #6c757d; font-size: .75em; }
.settings-grid code { overflow-wrap: anywhere; }
.tool-calls { flex: 0 0 auto; max-height: 32%; overflow: auto; margin-bottom: 1rem; padding: .75rem; background: #fff3cd; border: 1px solid #ffecb5; border-radius: .375rem; }
.tool-calls-title { font-weight: 700; margin-bottom: .5rem; }
.tool-call { margin-top: .6rem; padding: .7rem; background: rgba(255,255,255,.7); border-radius: .25rem; }
.tool-call-heading { display: flex; flex-wrap: wrap; gap: .4rem .75rem; align-items: baseline; }
.tool-call-heading code { overflow-wrap: anywhere; color: #6c3d00; }
.tool-result { margin-top: .35rem; color: #495057; }
.technical-details { margin-top: .45rem; font-size: .78em; }
.technical-details pre { margin: .35rem 0 0; white-space: pre-wrap; overflow-wrap: anywhere; }
@media (max-width: 991.98px) {
  :global(body) { min-width: 0; overflow: auto; }
  .app-shell { height: auto; min-height: 100vh; }
  .app-toolbar { flex-wrap: wrap; }
  .workspace-input, .session-select, .pdf-input { width: 100%; }
  .workspace-main, .workspace-row { height: auto; }
  .workspace-row { display: grid; grid-template-columns: 1fr; }
  .panel-column { min-height: 360px; }
  .code-editor { min-height: 420px; }
}
</style>
