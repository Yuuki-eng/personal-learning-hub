<template>
  <div class="settings-page page-enter">
    <h1 class="page-title">{{ t('settings.title') }}</h1>
    <p class="page-desc">{{ t('settings.desc') }}</p>

    <div class="settings-grid">
      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.aiConfig') }}</h2>
        <p class="section-desc">Connect to any OpenAI-compatible API</p>
        <div class="form-group">
          <label>{{ t('settings.provider') }}</label>
          <select v-model="form.api_base_url" class="form-input" @change="onProviderChange">
            <option v-for="p in providers" :key="p.url" :value="p.url">{{ p.name }}</option>
            <option value="custom">{{ t('settings.customUrl') }}</option>
          </select>
        </div>
        <div class="form-group" v-if="form.api_base_url === 'custom'">
          <label>{{ t('settings.customApiUrl') }}</label>
          <input v-model="customUrl" type="text" class="form-input" :placeholder="t('settings.customApiPlaceholder')" />
        </div>
        <div class="form-group">
          <label>{{ t('settings.apiKey') }}</label>
          <input v-model="form.api_key" type="password" class="form-input" placeholder="sk-..." />
        </div>
        <div class="form-group">
          <label>{{ t('settings.model') }}</label>
          <input v-model="form.model_name" type="text" class="form-input" placeholder="e.g. deepseek-chat, gpt-4o-mini" />
        </div>
        <div class="form-group">
          <label>{{ t('settings.embedModel') }}</label>
          <input v-model="form.embedding_model" type="text" class="form-input" placeholder="text-embedding-3-small" />
        </div>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.sysPrompt') }}</h2>
        <textarea v-model="form.system_prompt" class="form-textarea" rows="6"
          placeholder="You are a personal learning assistant..."></textarea>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.userProfile') }}</h2>
        <textarea v-model="form.user_profile" class="form-textarea" rows="4"
          placeholder="I'm a CS student in my 3rd year..."></textarea>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.ragDocs') }}</h2>
        <p class="section-desc">{{ t('settings.ragDesc') }}</p>
        <div class="upload-area">
          <label class="upload-dropzone" :class="{ disabled: uploading }">
            <template v-if="uploading">
              <div class="upload-spinner"></div>
              <span>{{ t('common.loading') }}</span>
            </template>
            <template v-else>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span>{{ t('settings.dragDoc') }}</span>
            </template>
            <input type="file" accept=".pdf,.txt,.md" @change="handleDocUpload" style="display:none" :disabled="uploading" />
          </label>
        </div>
        <div v-if="docs.length > 0" class="doc-list">
          <div v-for="doc in docs" :key="doc.name" class="doc-item">
            <div class="doc-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--color-ink-400)" stroke-width="1.5" stroke-linecap="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <div class="doc-info">
              <div class="doc-name">{{ doc.name }}</div>
              <div class="doc-meta">{{ doc.chunks_count }} chunks</div>
            </div>
            <button class="icon-btn danger" @click="handleDeleteDoc(doc.name)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            </button>
          </div>
        </div>
        <div v-else class="no-docs">{{ t('settings.noDocs') }}</div>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.musicCookie') }}</h2>
        <p class="section-desc">
          {{ t('settings.musicCookieDesc') }}
          <span v-if="hasMusicCookie" style="color: var(--color-sage-500);">✓ {{ t('settings.cookieConfigured') }}</span>
          <span v-else style="color: var(--color-coral-500);">✗ {{ t('settings.noCookie') }}</span>
        </p>
        <div class="cookie-steps">
          <ol>
            <li>{{ t('settings.cookieStep1') }}</li>
            <li>{{ t('settings.cookieStep2') }}</li>
            <li>{{ t('settings.cookieStep3') }}</li>
            <li>{{ t('settings.cookieStep4') }}</li>
          </ol>
        </div>
        <div class="form-group">
          <label>{{ t('settings.cookieValue') }}</label>
          <input v-model="musicCookie" type="password" class="form-input" :placeholder="t('settings.cookiePlaceholder')" />
        </div>
        <div class="cookie-actions">
          <button class="btn-primary" @click="handleCookieSave" :disabled="cookieSaving">
            {{ cookieSaving ? '...' : t('settings.saveCookie') }}
          </button>
          <button class="btn-secondary" @click="musicCookie = ''; handleCookieSave()" :disabled="cookieSaving">
            {{ t('settings.clear') }}
          </button>
        </div>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.customUrls') }}</h2>
        <p class="section-desc">{{ t('settings.customUrlsDesc') }}</p>
        <div class="url-add-row">
          <input
            v-model="newUrl"
            type="text"
            class="form-input"
            :placeholder="t('settings.urlPlaceholder')"
            @keydown.enter="addUrl"
          />
          <button class="btn-primary" @click="addUrl" :disabled="!newUrl.trim()">{{ t('settings.addUrl') }}</button>
        </div>
        <p v-if="urlError" class="url-error">{{ urlError }}</p>
        <div v-if="customUrls.length > 0" class="url-list">
          <div v-for="(url, idx) in customUrls" :key="url" class="url-item"
            draggable="true"
            @dragstart="onDragStart(idx, $event)"
            @dragover.prevent="onDragOver(idx, $event)"
            @drop="onDrop(idx)"
            @dragend="dragIdx = -1"
          >
            <span class="url-drag-handle">⠿</span>
            <span class="url-text">{{ url }}</span>
            <button class="icon-btn danger" @click="removeUrl(idx)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <div v-else class="no-docs">{{ t('settings.noUrls') }}</div>
      </div>

      <div class="setting-section">
        <h2 class="section-title">{{ t('settings.language') }}</h2>
        <p class="section-desc">{{ t('settings.languageDesc') }}</p>
        <div class="lang-options">
          <button class="lang-btn" :class="{ active: localeStore.current === 'en' }" @click="localeStore.setLocale('en')">English</button>
          <button class="lang-btn" :class="{ active: localeStore.current === 'zh' }" @click="localeStore.setLocale('zh')">中文</button>
          <button class="lang-btn" :class="{ active: localeStore.current === 'ja' }" @click="localeStore.setLocale('ja')">日本語</button>
        </div>
      </div>
    </div>

    <div class="save-bar">
      <transition name="fade">
        <span v-if="saved" class="saved-msg">{{ t('settings.saved') }}</span>
      </transition>
      <button class="btn-primary" @click="handleSave" :disabled="saving">
        {{ saving ? '...' : t('settings.saveSettings') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAISettings, updateAISettings, getDocuments, uploadDocument, deleteDocument } from '../api/ai'
import { getMusicCookieStatus, setMusicCookie } from '../api/music'
import { useLocaleStore } from '../stores/locale'
import { ElMessage } from 'element-plus'

const localeStore = useLocaleStore()
const t = localeStore.t

const form = ref({
  api_key: '',
  api_base_url: 'https://api.deepseek.com',
  model_name: 'deepseek-chat',
  system_prompt: '',
  user_profile: '',
  embedding_model: 'text-embedding-3-small',
})

const customUrl = ref('')
const saving = ref(false)
const saved = ref(false)
const docs = ref([])
const musicCookie = ref('')
const hasMusicCookie = ref(false)
const cookieSaving = ref(false)
const uploading = ref(false)

const newUrl = ref('')
const urlError = ref('')
const customUrls = ref([])
const dragIdx = ref(-1)
const dragOverIdx = ref(-1)

const providers = [
  { name: 'DeepSeek', url: 'https://api.deepseek.com' },
  { name: 'OpenAI', url: 'https://api.openai.com/v1' },
  { name: 'Zhipu AI (GLM)', url: 'https://open.bigmodel.cn/api/paas/v4' },
  { name: 'Qwen (Tongyi)', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  { name: 'Moonshot (Kimi)', url: 'https://api.moonshot.cn/v1' },
  { name: 'SiliconFlow', url: 'https://api.siliconflow.cn/v1' },
]

function onProviderChange() {
  if (form.value.api_base_url === 'custom') return
  const modelMap = {
    'https://api.deepseek.com': 'deepseek-chat',
    'https://api.openai.com/v1': 'gpt-4o-mini',
    'https://open.bigmodel.cn/api/paas/v4': 'glm-4-flash',
    'https://dashscope.aliyuncs.com/compatible-mode/v1': 'qwen-plus',
    'https://api.moonshot.cn/v1': 'moonshot-v1-8k',
    'https://api.siliconflow.cn/v1': 'Qwen/Qwen2.5-7B-Instruct',
  }
  form.value.model_name = modelMap[form.value.api_base_url] || ''
}

function isValidUrl(str) {
  try {
    const u = new URL(str)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch { return false }
}

function saveUrls() {
  localStorage.setItem('customJumpUrls', JSON.stringify(customUrls.value))
}

function addUrl() {
  urlError.value = ''
  const url = newUrl.value.trim()
  if (!url) return
  if (!isValidUrl(url)) {
    urlError.value = t('settings.urlInvalid')
    return
  }
  if (customUrls.value.includes(url)) {
    urlError.value = t('settings.urlDuplicate')
    return
  }
  customUrls.value.push(url)
  saveUrls()
  newUrl.value = ''
}

function removeUrl(idx) {
  customUrls.value.splice(idx, 1)
  saveUrls()
}

function onDragStart(idx, e) {
  dragIdx.value = idx
  e.dataTransfer.effectAllowed = 'move'
}

function onDragOver(idx, e) {
  dragOverIdx.value = idx
}

function onDrop(idx) {
  if (dragIdx.value < 0 || dragIdx.value === idx) return
  const item = customUrls.value.splice(dragIdx.value, 1)[0]
  customUrls.value.splice(idx, 0, item)
  saveUrls()
  dragIdx.value = -1
}

async function handleSave() {
  saving.value = true
  try {
    const data = { ...form.value }
    if (data.api_base_url === 'custom') {
      data.api_base_url = customUrl.value
    }
    await updateAISettings(data)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch {}
  saving.value = false
}

async function handleDocUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    await uploadDocument(file)
    ElMessage.success(t('settings.docIndexed'))
    docs.value = await getDocuments()
  } catch (err) {
    const detail = err.response?.data?.detail
    ElMessage.error(detail || t('common.error'))
  }
  uploading.value = false
  e.target.value = ''
}

async function handleDeleteDoc(name) {
  try {
    await deleteDocument(name)
    docs.value = await getDocuments()
    ElMessage.success(t('settings.docRemoved'))
  } catch {}
}

async function handleCookieSave() {
  cookieSaving.value = true
  try {
    await setMusicCookie(musicCookie.value)
    hasMusicCookie.value = !!musicCookie.value
    ElMessage.success(musicCookie.value ? t('settings.cookieSaved') : t('settings.cookieCleared'))
  } catch {
    ElMessage.error(t('settings.cookieFailed'))
  }
  cookieSaving.value = false
}

onMounted(async () => {
  try {
    const stored = localStorage.getItem('customJumpUrls')
    if (stored) customUrls.value = JSON.parse(stored)
  } catch {}

  try {
    const [s, d, cs] = await Promise.all([getAISettings(), getDocuments(), getMusicCookieStatus()])
    form.value = {
      api_key: s.api_key || '',
      api_base_url: s.api_base_url || 'https://api.deepseek.com',
      model_name: s.model_name || 'deepseek-chat',
      system_prompt: s.system_prompt || '',
      user_profile: s.user_profile || '',
      embedding_model: s.embedding_model || 'text-embedding-3-small',
    }
    const isKnown = providers.some(p => p.url === form.value.api_base_url)
    if (!isKnown) {
      customUrl.value = form.value.api_base_url
      form.value.api_base_url = 'custom'
    }
    docs.value = d
    hasMusicCookie.value = cs.hasCookie || false
  } catch {}
})
</script>

<style scoped>
.settings-page { max-width: 720px; }

.page-title { font-size: 28px; font-weight: 700; color: var(--color-ink-900); letter-spacing: -0.02em; }
.page-desc { color: var(--color-ink-400); font-size: 14px; margin-top: 4px; margin-bottom: 32px; }

.settings-grid { display: flex; flex-direction: column; gap: 28px; }

.setting-section {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 14px;
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-ink-800);
  margin-bottom: 4px;
}

.section-desc {
  font-size: 13px;
  color: var(--color-ink-400);
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 14px;
}

.form-group label { font-size: 13px; font-weight: 500; color: var(--color-ink-600); }

.form-input {
  padding: 9px 12px;
  border: 1.5px solid var(--color-ink-200);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  background: var(--color-surface-base);
  color: var(--color-ink-800);
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus { outline: none; border-color: var(--color-warm-500); }

select.form-input { cursor: pointer; }

.form-textarea {
  padding: 10px 12px;
  border: 1.5px solid var(--color-ink-200);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  background: var(--color-surface-base);
  color: var(--color-ink-800);
  resize: vertical;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.form-textarea:focus { outline: none; border-color: var(--color-warm-500); }

.upload-area { margin-bottom: 16px; }

.upload-dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  border: 2px dashed var(--color-ink-200);
  border-radius: 10px;
  cursor: pointer;
  color: var(--color-ink-400);
  font-size: 13px;
  transition: border-color 0.2s, color 0.2s;
}
.upload-dropzone:hover { border-color: var(--color-warm-500); color: var(--color-warm-500); }
.upload-dropzone.disabled { opacity: 0.6; cursor: not-allowed; pointer-events: none; }
.upload-dropzone svg { width: 28px; height: 28px; }

.upload-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-ink-200);
  border-top-color: var(--color-warm-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.doc-list { display: flex; flex-direction: column; gap: 8px; }

.doc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--color-ink-100);
  border-radius: 8px;
  background: var(--color-surface-base);
}

.doc-icon svg { width: 20px; height: 20px; }
.doc-info { flex: 1; }
.doc-name { font-size: 13px; font-weight: 600; color: var(--color-ink-700); }
.doc-meta { font-size: 11px; color: var(--color-ink-400); }

.icon-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: transparent;
  color: var(--color-ink-400);
  transition: background 0.15s, color 0.15s;
}
.icon-btn svg { width: 16px; height: 16px; }
.icon-btn:hover { background: var(--color-ink-100); color: var(--color-ink-700); }
.icon-btn.danger:hover { background: rgba(220, 80, 60, 0.1); color: #dc503c; }

.no-docs {
  font-size: 13px;
  color: var(--color-ink-400);
  text-align: center;
  padding: 12px;
}

.cookie-steps {
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--color-ink-500);
}
.cookie-steps ol { padding-left: 18px; margin: 0; }
.cookie-steps li { margin-bottom: 4px; }
.cookie-steps code {
  background: var(--color-ink-100);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
}
.cookie-steps a { color: var(--color-warm-500); text-decoration: none; }
.cookie-steps a:hover { text-decoration: underline; }

.cookie-actions { display: flex; gap: 10px; margin-top: 8px; }

.url-add-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.url-add-row .form-input { flex: 1; }

.url-error {
  font-size: 12px;
  color: #dc503c;
  margin: 0 0 8px;
}

.url-list { display: flex; flex-direction: column; gap: 6px; }

.url-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--color-ink-100);
  border-radius: 8px;
  background: var(--color-surface-base);
  cursor: grab;
  transition: background 0.15s, box-shadow 0.15s;
}
.url-item:active { cursor: grabbing; }
.url-item[draggable="true"]:hover {
  background: var(--color-ink-50, rgba(0,0,0,0.02));
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.url-drag-handle {
  color: var(--color-ink-300);
  font-size: 16px;
  user-select: none;
  flex-shrink: 0;
}

.url-text {
  flex: 1;
  font-size: 13px;
  color: var(--color-ink-600);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lang-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.lang-btn {
  padding: 8px 20px;
  border: 1.5px solid var(--color-ink-200);
  border-radius: 8px;
  background: var(--color-surface-base);
  color: var(--color-ink-600);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.lang-btn:hover {
  border-color: var(--color-ink-300);
  color: var(--color-ink-800);
}
.lang-btn.active {
  border-color: var(--color-warm-500);
  color: var(--color-warm-500);
  background: rgba(212, 148, 79, 0.06);
}

.save-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--color-ink-100);
}

.saved-msg {
  font-size: 13px;
  color: var(--color-sage-500);
  font-weight: 500;
}

.btn-primary {
  padding: 9px 22px;
  border-radius: 8px;
  border: none;
  background: var(--color-ink-800);
  color: var(--color-surface-base);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
}
.btn-primary:hover { opacity: 0.85; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.4; cursor: default; transform: none; }

.btn-secondary {
  padding: 9px 22px;
  border-radius: 8px;
  border: 1.5px solid var(--color-ink-200);
  background: var(--color-surface-base);
  color: var(--color-ink-600);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-secondary:hover { border-color: var(--color-ink-300); color: var(--color-ink-800); }
.btn-secondary:disabled { opacity: 0.4; cursor: default; }

.fade-enter-active { transition: opacity 0.3s; }
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
