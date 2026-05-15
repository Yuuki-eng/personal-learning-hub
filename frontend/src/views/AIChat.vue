<template>
  <div class="ai-page page-enter">
    <div class="ai-layout">
      <aside class="ai-sidebar">
        <button class="new-chat-btn" @click="createNewSession">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          New Chat
        </button>
        <div class="session-list">
          <div v-for="s in sessions" :key="s.id" class="session-item" :class="{ active: currentSession?.id === s.id }"
            @click="selectSession(s)">
            <div class="session-title">{{ s.title }}</div>
            <button class="session-delete" @click.stop="deleteSession(s.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div v-if="sessions.length === 0" class="no-sessions">No conversations yet</div>
        </div>
      </aside>

      <div class="ai-chat-area">
        <div class="messages-container" ref="messagesRef">
          <div v-if="messages.length === 0" class="welcome-ai">
            <div class="welcome-icon">
              <svg viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="var(--color-warm-300)" stroke-width="1.5" fill="var(--color-warm-50)"/>
                <circle cx="17" cy="20" r="2.5" fill="var(--color-ink-600)"/>
                <circle cx="31" cy="20" r="2.5" fill="var(--color-ink-600)"/>
                <path d="M16 30c2 4 8 6 12 0" stroke="var(--color-ink-500)" stroke-width="1.5" stroke-linecap="round" fill="none"/>
              </svg>
            </div>
            <h3>AI Learning Assistant</h3>
            <p>Ask me anything about your studies. I can help with explanations, generate learning graphs, and remember our conversation context.</p>
            <div class="quick-prompts">
              <button v-for="p in quickPrompts" :key="p" class="quick-prompt" @click="sendMessage(p)">{{ p }}</button>
            </div>
          </div>

          <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
            <div class="msg-avatar">
              <svg v-if="msg.role === 'user'" viewBox="0 0 24 24" fill="var(--color-ink-600)"><circle cx="12" cy="8" r="4"/><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="var(--color-warm-400)" stroke-width="1.5" fill="var(--color-warm-50)"/>
                <circle cx="9" cy="10" r="1.5" fill="var(--color-ink-500)"/>
                <circle cx="15" cy="10" r="1.5" fill="var(--color-ink-500)"/>
                <path d="M8 15c1.5 2 4.5 2 6 0" stroke="var(--color-ink-400)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
              </svg>
            </div>
            <div class="msg-content">
              <div class="msg-text" v-html="formatMessage(msg.content)"></div>
              <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
            </div>
          </div>

          <div v-if="streaming" class="message assistant">
            <div class="msg-avatar">
              <svg viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="var(--color-warm-400)" stroke-width="1.5" fill="var(--color-warm-50)"/>
                <circle cx="9" cy="10" r="1.5" fill="var(--color-ink-500)"/>
                <circle cx="15" cy="10" r="1.5" fill="var(--color-ink-500)"/>
                <path d="M8 15c1.5 2 4.5 2 6 0" stroke="var(--color-ink-400)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
              </svg>
            </div>
            <div class="msg-content">
              <div class="msg-text" v-html="formatMessage(streamBuffer)"></div>
              <span class="typing-cursor"></span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-row">
            <textarea v-model="inputText" class="chat-input" placeholder="Type your message..."
              rows="1" @keydown.enter.exact.prevent="handleSend" @input="autoResize"></textarea>
            <button class="send-btn" @click="handleSend" :disabled="!inputText.trim() || streaming">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>
          <div class="input-hint">Enter to send, Shift+Enter for new line</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { getSessions, createSession, getMessages, deleteSession as apiDeleteSession, streamChat } from '../api/ai'

const sessions = ref([])
const currentSession = ref(null)
const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamBuffer = ref('')
const messagesRef = ref(null)

const quickPrompts = [
  'Generate my learning graph',
  'Analyze my study progress',
  'What should I focus on next?',
  'Summarize my recent blog posts',
]

async function fetchSessions() {
  sessions.value = await getSessions()
}

async function createNewSession() {
  const s = await createSession('New Chat')
  sessions.value.unshift(s)
  currentSession.value = s
  messages.value = []
}

async function selectSession(s) {
  currentSession.value = s
  messages.value = await getMessages(s.id)
  await scrollToBottom()
}

async function deleteSession(id) {
  await apiDeleteSession(id)
  sessions.value = sessions.value.filter(s => s.id !== id)
  if (currentSession.value?.id === id) {
    currentSession.value = null
    messages.value = []
  }
}

async function handleSend() {
  if (!inputText.value.trim() || streaming.value) return
  await sendMessage(inputText.value.trim())
  inputText.value = ''
}

async function sendMessage(content) {
  if (!currentSession.value) {
    await createNewSession()
  }

  const userMsg = {
    id: Date.now(),
    role: 'user',
    content,
    created_at: new Date().toISOString(),
  }
  messages.value.push(userMsg)
  await scrollToBottom()

  streaming.value = true
  streamBuffer.value = ''

  streamChat(
    currentSession.value.id,
    content,
    (token) => {
      streamBuffer.value += token
      scrollToBottom()
    },
    (error) => {
      streamBuffer.value += `\n\n[Error: ${error}]`
      streaming.value = false
      finalizeStream()
    },
    async () => {
      streaming.value = false
      finalizeStream()
      await fetchSessions()
    }
  )
}

async function finalizeStream() {
  if (streamBuffer.value) {
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: streamBuffer.value,
      created_at: new Date().toISOString(),
    })
    streamBuffer.value = ''
    await scrollToBottom()
  }
}

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^# (.*$)/gm, '<h2>$1</h2>')
    .replace(/\n/g, '<br>')
}

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

onMounted(fetchSessions)
</script>

<style scoped>
.ai-page { height: calc(100vh - 100px); display: flex; flex-direction: column; }

.ai-layout {
  display: flex;
  flex: 1;
  gap: 0;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 16px;
  overflow: hidden;
  height: 100%;
}

.ai-sidebar {
  width: 240px;
  background: var(--color-ink-50);
  border-right: 1px solid var(--color-ink-100);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px;
  padding: 10px;
  border: 1px dashed var(--color-ink-300);
  border-radius: 10px;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink-600);
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover { background: var(--color-surface-elevated); border-color: var(--color-warm-400); color: var(--color-warm-600); }
.new-chat-btn svg { width: 16px; height: 16px; }

.session-list { flex: 1; overflow-y: auto; padding: 0 8px; }

.session-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 10px;
  border-radius: 9px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 2px;
}

.session-item:hover { background: rgba(0,0,0,0.04); }
.session-item.active { background: var(--color-surface-elevated); box-shadow: 0 1px 3px rgba(0,0,0,0.04); }

.session-title {
  flex: 1;
  font-size: 13px;
  color: var(--color-ink-700);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-delete {
  width: 22px; height: 22px; border: none; background: transparent;
  border-radius: 5px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--color-ink-300); opacity: 0; transition: all 0.15s;
}
.session-item:hover .session-delete { opacity: 1; }
.session-delete:hover { background: #fef2f2; color: #b91c1c; }
.session-delete svg { width: 13px; height: 13px; }

.no-sessions { text-align: center; padding: 20px; font-size: 12px; color: var(--color-ink-300); }

.ai-chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-ai {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}

.welcome-icon { width: 56px; height: 56px; margin-bottom: 16px; }
.welcome-ai h3 { font-size: 18px; font-weight: 600; color: var(--color-ink-800); margin-bottom: 8px; }
.welcome-ai p { font-size: 14px; color: var(--color-ink-400); max-width: 400px; line-height: 1.6; }

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
  justify-content: center;
}

.quick-prompt {
  padding: 7px 14px;
  border: 1px solid var(--color-ink-200);
  border-radius: 10px;
  background: var(--color-surface-elevated);
  font-size: 13px;
  color: var(--color-ink-600);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-prompt:hover { border-color: var(--color-warm-300); color: var(--color-warm-600); background: var(--color-warm-50); }

.message {
  display: flex;
  gap: 10px;
  max-width: 80%;
  animation: fadeSlideUp 0.3s ease;
}

.message.user { align-self: flex-end; flex-direction: row-reverse; }
.message.assistant { align-self: flex-start; }

.msg-avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.msg-avatar svg { width: 28px; height: 28px; }

.msg-content {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
}

.message.user .msg-content {
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-bottom-right-radius: 4px;
}

.message.assistant .msg-content {
  background: var(--color-ink-50);
  color: var(--color-ink-800);
  border-bottom-left-radius: 4px;
}

.msg-text :deep(code) {
  background: rgba(0,0,0,0.06);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
}

.message.user .msg-text :deep(code) {
  background: rgba(255,255,255,0.15);
}

.msg-text :deep(h2), .msg-text :deep(h3), .msg-text :deep(h4) {
  margin: 8px 0 4px;
  font-weight: 600;
}

.msg-time {
  font-size: 11px;
  color: var(--color-ink-300);
  margin-top: 4px;
}

.message.user .msg-time { text-align: right; }

.typing-cursor {
  display: inline-block;
  width: 6px;
  height: 16px;
  background: var(--color-warm-400);
  border-radius: 1px;
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

.input-area {
  padding: 16px 20px;
  border-top: 1px solid var(--color-ink-100);
  background: var(--color-surface-elevated);
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--color-ink-200);
  border-radius: 12px;
  font-size: 14px;
  color: var(--color-ink-800);
  outline: none;
  resize: none;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.2s;
  background: var(--color-ink-50);
}

.chat-input:focus { border-color: var(--color-warm-400); background: var(--color-surface-elevated); }
.chat-input::placeholder { color: var(--color-ink-300); }

.send-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--color-ink-800);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-surface-elevated);
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover { background: var(--color-ink-900); transform: translateY(-1px); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.send-btn svg { width: 18px; height: 18px; }

.input-hint {
  font-size: 11px;
  color: var(--color-ink-300);
  margin-top: 6px;
}

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
