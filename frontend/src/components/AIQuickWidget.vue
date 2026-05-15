<template>
  <div class="ai-quick" :class="{ expanded }">
    <div class="ai-quick-header" @click="expanded = !expanded">
      <span class="ai-quick-icon">⌘</span>
      <transition name="fade">
        <span v-if="!expanded" class="ai-quick-hint">Ask AI</span>
      </transition>
      <transition name="fade">
        <span v-if="expanded" class="ai-quick-close">✕</span>
      </transition>
    </div>
    <transition name="slide-up">
      <div v-if="expanded" class="ai-quick-body">
        <div class="ai-quick-messages" ref="msgContainer">
          <div v-for="(msg, i) in messages" :key="i" class="ai-msg" :class="msg.role">
            <div class="ai-msg-text">{{ msg.content }}</div>
          </div>
          <div v-if="streaming" class="ai-msg assistant">
            <div class="ai-msg-text">{{ streamText }}<span class="cursor-blink">▌</span></div>
          </div>
        </div>
        <div class="ai-quick-input-row">
          <input
            v-model="inputText"
            class="ai-quick-input"
            placeholder="Quick ask anything..."
            @keydown.enter="sendMessage"
            :disabled="streaming"
          />
          <button class="ai-quick-send" @click="sendMessage" :disabled="!inputText.trim() || streaming">
            →
          </button>
        </div>
        <router-link to="/ai" class="ai-quick-full">Open full AI →</router-link>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { createSession, streamChat } from '../api/ai'

const expanded = ref(false)
const inputText = ref('')
const messages = ref([])
const streaming = ref(false)
const streamText = ref('')
const sessionId = ref(null)
const msgContainer = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || streaming.value) return

  inputText.value = ''
  messages.value.push({ role: 'user', content: text })
  scrollToBottom()

  try {
    if (!sessionId.value) {
      const session = await createSession('Quick Chat')
      sessionId.value = session.id
    }

    streaming.value = true
    streamText.value = ''

    await streamChat(
      sessionId.value,
      text,
      (chunk) => {
        streamText.value += chunk
        scrollToBottom()
      },
      (err) => {
        messages.value.push({ role: 'assistant', content: `Error: ${err}` })
        streamText.value = ''
        streaming.value = false
        scrollToBottom()
      },
      () => {
        messages.value.push({ role: 'assistant', content: streamText.value })
        streamText.value = ''
        streaming.value = false
        scrollToBottom()
      }
    )
  } catch {
    messages.value.push({ role: 'assistant', content: 'Failed to connect. Check AI settings.' })
    streaming.value = false
  }
}
</script>

<style scoped>
.ai-quick {
  position: fixed;
  bottom: 80px;
  right: 24px;
  z-index: 900;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.ai-quick.expanded {
  bottom: 80px;
}

.ai-quick-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border: 2px solid var(--color-ink-800);
  box-shadow: 3px 3px 0 var(--color-ink-400);
  cursor: pointer;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  transition: all 0.15s ease;
  user-select: none;
}

.ai-quick-header:hover {
  box-shadow: 4px 4px 0 var(--color-warm-500);
  transform: translate(-1px, -1px);
}

.ai-quick-icon {
  font-size: 16px;
}

.ai-quick-close {
  font-size: 12px;
  opacity: 0.7;
}

.ai-quick-body {
  width: 340px;
  margin-bottom: 6px;
  background: var(--color-surface-elevated);
  border: 2px solid var(--color-ink-800);
  box-shadow: 4px 4px 0 var(--color-ink-300);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-quick-messages {
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-msg {
  max-width: 85%;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}

.ai-msg.user {
  align-self: flex-end;
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-radius: 2px 2px 0 2px;
  font-family: 'Courier New', monospace;
}

.ai-msg.assistant {
  align-self: flex-start;
  background: var(--color-ink-50);
  color: var(--color-ink-800);
  border-radius: 2px 2px 2px 0;
  border: 1px solid var(--color-ink-200);
}

.cursor-blink {
  animation: pixelBlink 0.8s step-end infinite;
  color: var(--color-warm-500);
}

.ai-quick-input-row {
  display: flex;
  border-top: 2px solid var(--color-ink-200);
}

.ai-quick-input {
  flex: 1;
  padding: 10px 12px;
  border: none;
  outline: none;
  font-size: 13px;
  background: transparent;
  font-family: 'Courier New', monospace;
  color: var(--color-ink-800);
}

.ai-quick-input::placeholder {
  color: var(--color-ink-300);
}

.ai-quick-send {
  padding: 10px 14px;
  border: none;
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  font-size: 16px;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  transition: background 0.12s;
}

.ai-quick-send:hover:not(:disabled) {
  background: var(--color-warm-600);
}

.ai-quick-send:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ai-quick-full {
  display: block;
  text-align: center;
  padding: 6px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--color-ink-500);
  text-decoration: none;
  border-top: 1px solid var(--color-ink-100);
  transition: color 0.15s;
}

.ai-quick-full:hover {
  color: var(--color-warm-500);
  background: var(--color-ink-50);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
