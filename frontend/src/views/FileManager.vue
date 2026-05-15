<template>
  <div class="files-page page-enter">
    <div v-animate="'fade-up'" class="files-top">
      <div>
        <h1 class="page-title">Files</h1>
        <p class="page-desc">Your learning materials and resources</p>
      </div>
      <div class="files-actions">
        <button class="btn-secondary" @click="showNewFolder = true">New Folder</button>
        <label class="btn-primary upload-label">
          Upload
          <input type="file" multiple @change="handleUpload" style="display:none" />
        </label>
      </div>
    </div>

    <div v-animate="{ name: 'scale-in', delay: 80 }" class="storage-banner glass-bar">
      <div class="storage-left">
        <div class="storage-num">{{ formatSize(storage.total_size) }}</div>
        <div class="storage-meta">
          {{ storage.total_files }} files · {{ storage.total_folders }} folders
        </div>
      </div>
      <div class="storage-bar-visual">
        <div class="storage-bar-track">
          <div class="storage-bar-fill" :style="{ width: storagePct + '%' }"></div>
        </div>
        <span class="storage-bar-label">{{ storagePct }}% used</span>
      </div>
      <div class="storage-path">
        <span class="path-icon">📁</span>
        <span class="path-text">Stored locally at: <code>backend/data/uploads/</code></span>
      </div>
    </div>

    <div class="security-notice glass-bar">
      <div class="sec-icon">🔒</div>
      <div class="sec-body">
        <div class="sec-title">Privacy & Security</div>
        <div class="sec-text">
          Files are stored <strong>locally on your server</strong> — not in any cloud.
          No third party has access. Data never leaves your machine unless you explicitly share it.
          Access is restricted to this application only.
        </div>
      </div>
    </div>

    <div class="breadcrumb" v-if="breadcrumbs.length > 0">
      <span class="crumb" @click="navigateTo(null)">~/</span>
      <template v-for="(bc, i) in breadcrumbs" :key="bc.id">
        <span class="crumb" :class="{ current: i === breadcrumbs.length - 1 }" @click="navigateTo(bc.id)">{{ bc.name }}/</span>
      </template>
    </div>

    <div v-if="uploading" class="upload-progress">
      <div class="upload-bar">
        <div class="upload-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <span>Uploading... {{ uploadProgress }}%</span>
    </div>

    <div v-if="files.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <p>Empty folder</p>
      <label class="empty-link">
        Upload files →
        <input type="file" multiple @change="handleUpload" style="display:none" />
      </label>
    </div>

    <div v-else class="file-grid">
      <div
        v-for="file in files"
        :key="file.id"
        class="file-card"
        :class="{ folder: file.is_folder, preview: !file.is_folder && isImage(file.mime_type) }"
        @dblclick="file.is_folder ? navigateTo(file.id) : null"
      >
        <div class="file-preview" v-if="!file.is_folder && isImage(file.mime_type)">
          <img :src="`/api/files/${file.id}/stream`" :alt="file.name" loading="lazy" />
        </div>
        <div class="file-preview video-thumb" v-else-if="!file.is_folder && isVideo(file.mime_type)">
          <video :src="`/api/files/${file.id}/stream`" preload="metadata" muted></video>
          <div class="play-overlay">
            <svg viewBox="0 0 24 24" fill="white"><polygon points="5 3 19 12 5 21"/></svg>
          </div>
        </div>
        <div class="file-icon" v-else>
          <svg v-if="file.is_folder" viewBox="0 0 24 24" fill="var(--color-warm-300)" stroke="var(--color-warm-400)" stroke-width="1">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="var(--color-ink-300)" stroke-width="1.5" stroke-linecap="round">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-meta">
            <span v-if="!file.is_folder">{{ formatSize(file.file_size) }}</span>
            <span v-if="!file.is_folder && file.mime_type" class="file-type">{{ shortMime(file.mime_type) }}</span>
          </div>
        </div>
        <div class="file-actions">
          <a v-if="!file.is_folder" :href="`/api/files/${file.id}/download`" class="icon-btn" @click.stop title="Download">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </a>
          <button class="icon-btn" @click.stop="handleRename(file)" title="Rename">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="icon-btn danger" @click.stop="handleDelete(file)" title="Delete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <el-dialog v-model="showNewFolder" title="New Folder" width="380px">
      <input v-model="newFolderName" type="text" class="form-input" placeholder="Folder name" @keyup.enter="createFolderAction" />
      <template #footer>
        <button class="btn-secondary" @click="showNewFolder = false">Cancel</button>
        <button class="btn-primary" @click="createFolderAction">Create</button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRename" title="Rename" width="380px">
      <input v-model="renameTo" type="text" class="form-input" placeholder="New name" @keyup.enter="renameAction" />
      <template #footer>
        <button class="btn-secondary" @click="showRename = false">Cancel</button>
        <button class="btn-primary" @click="renameAction">Rename</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getFiles, uploadFile, createFolder, deleteFile, renameFile, getStorage } from '../api/files'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref([])
const currentFolder = ref(null)
const breadcrumbs = ref([])
const storage = ref({ total_files: 0, total_folders: 0, total_size: 0 })
const uploading = ref(false)
const uploadProgress = ref(0)
const showNewFolder = ref(false)
const newFolderName = ref('')
const showRename = ref(false)
const renameTo = ref('')
const renameTarget = ref(null)

const MAX_STORAGE = 10 * 1024 * 1024 * 1024
const storagePct = computed(() => {
  if (!storage.value.total_size) return 0
  return Math.min(100, Math.round((storage.value.total_size / MAX_STORAGE) * 100))
})

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function isVideo(mime) { return mime?.startsWith('video/') }
function isImage(mime) { return mime?.startsWith('image/') }

function shortMime(mime) {
  if (!mime) return ''
  const parts = mime.split('/')
  return parts[1]?.toUpperCase()?.substring(0, 5) || ''
}

async function fetchFiles() {
  files.value = await getFiles(currentFolder.value)
}

async function fetchStorage() {
  storage.value = await getStorage()
}

async function navigateTo(folderId) {
  currentFolder.value = folderId
  if (folderId === null) {
    breadcrumbs.value = []
  } else {
    const folder = files.value.find(f => f.id === folderId)
    if (folder) {
      const idx = breadcrumbs.value.findIndex(b => b.id === folderId)
      if (idx >= 0) {
        breadcrumbs.value = breadcrumbs.value.slice(0, idx + 1)
      } else {
        breadcrumbs.value.push({ id: folder.id, name: folder.name })
      }
    }
  }
  await fetchFiles()
}

async function handleUpload(e) {
  const fileList = e.target.files
  if (!fileList?.length) return
  uploading.value = true
  try {
    for (let i = 0; i < fileList.length; i++) {
      uploadProgress.value = Math.round(((i + 1) / fileList.length) * 100)
      await uploadFile(fileList[i], currentFolder.value)
    }
    ElMessage.success(`${fileList.length} file(s) uploaded`)
    await fetchFiles()
    await fetchStorage()
  } catch {
    ElMessage.error('Upload failed')
  }
  uploading.value = false
  uploadProgress.value = 0
  e.target.value = ''
}

async function createFolderAction() {
  if (!newFolderName.value.trim()) return
  await createFolder(newFolderName.value.trim(), currentFolder.value)
  showNewFolder.value = false
  newFolderName.value = ''
  await fetchFiles()
}

function handleRename(file) {
  renameTarget.value = file
  renameTo.value = file.name
  showRename.value = true
}

async function renameAction() {
  if (!renameTo.value.trim() || !renameTarget.value) return
  try {
    await renameFile(renameTarget.value.id, renameTo.value.trim())
    showRename.value = false
    await fetchFiles()
  } catch {
    ElMessage.error('Rename failed')
  }
}

async function handleDelete(file) {
  try {
    await ElMessageBox.confirm(`Delete "${file.name}"?`, 'Confirm', { type: 'warning' })
    await deleteFile(file.id)
    ElMessage.success('Deleted')
    await fetchFiles()
    await fetchStorage()
  } catch {}
}

onMounted(async () => {
  await fetchFiles()
  await fetchStorage()
})
</script>

<style scoped>
.files-page { max-width: 1000px; }

.files-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-ink-900);
  letter-spacing: -0.02em;
  font-family: 'Courier New', monospace;
}

.page-desc {
  color: var(--color-ink-400);
  font-size: 13px;
  margin-top: 4px;
  font-family: 'Courier New', monospace;
}

.files-actions { display: flex; gap: 8px; }
.upload-label { cursor: pointer; display: inline-flex; align-items: center; }

.storage-banner {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 14px 18px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.storage-left { min-width: 100px; }

.storage-num {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-ink-800);
  font-family: 'Courier New', monospace;
}

.storage-meta {
  font-size: 11px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
  margin-top: 2px;
}

.storage-bar-visual { flex: 1; min-width: 120px; }

.storage-bar-track {
  width: 100%;
  height: 5px;
  background: var(--color-ink-100);
  overflow: hidden;
}

.storage-bar-fill {
  height: 100%;
  background: var(--color-warm-400);
  transition: width 0.5s ease;
}

.storage-bar-label {
  font-size: 10px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
}

.storage-path {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-ink-400);
}

.path-text code {
  background: var(--color-ink-50);
  padding: 1px 5px;
  font-family: 'Courier New', monospace;
  font-size: 10px;
  border: 1px solid var(--color-ink-200);
}

.security-notice {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.sec-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }

.sec-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-ink-700);
  font-family: 'Courier New', monospace;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}

.sec-text {
  font-size: 12px;
  color: var(--color-ink-500);
  line-height: 1.5;
}

.sec-text strong { color: var(--color-sage-600); }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 16px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.crumb {
  color: var(--color-ink-400);
  cursor: pointer;
  transition: color 0.15s;
  padding: 2px 4px;
}

.crumb:hover { color: var(--color-warm-500); }
.crumb.current { color: var(--color-ink-700); font-weight: 600; }

.upload-progress {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--color-ink-500);
  font-family: 'Courier New', monospace;
}

.upload-bar {
  flex: 1;
  height: 4px;
  background: var(--color-ink-100);
  overflow: hidden;
}

.upload-fill {
  height: 100%;
  background: var(--color-warm-400);
  transition: width 0.3s;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-ink-400);
  border: 1.5px dashed var(--color-ink-200);
  background: var(--color-ink-50);
}

.empty-icon { font-size: 40px; margin-bottom: 8px; }

.empty-link {
  color: var(--color-warm-500);
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 12px;
}

.file-card {
  background: var(--color-surface-elevated);
  border: 1.5px solid var(--color-ink-200);
  box-shadow: 2px 2px 0 var(--color-ink-100);
  overflow: hidden;
  transition: all 0.15s ease;
  position: relative;
  cursor: default;
}

.file-card.folder { cursor: pointer; }

.file-card:hover {
  box-shadow: 3px 3px 0 var(--color-ink-300);
  transform: translate(-1px, -1px);
}

.file-preview {
  width: 100%;
  height: 120px;
  overflow: hidden;
  background: var(--color-ink-50);
  position: relative;
}

.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.25);
  opacity: 0;
  transition: opacity 0.2s;
}

.video-thumb:hover .play-overlay { opacity: 1; }

.play-overlay svg {
  width: 32px;
  height: 32px;
}

.file-icon {
  width: 36px;
  height: 36px;
  margin: 16px auto 8px;
}

.file-icon svg { width: 36px; height: 36px; }

.file-info {
  padding: 10px 12px;
}

.file-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-ink-700);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Courier New', monospace;
  margin-bottom: 3px;
}

.file-meta {
  font-size: 10px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
  display: flex;
  gap: 8px;
}

.file-type {
  color: var(--color-warm-500);
  font-weight: 700;
  letter-spacing: 0.04em;
}

.file-actions {
  position: absolute;
  top: 6px;
  right: 6px;
  display: flex;
  gap: 3px;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-card:hover .file-actions { opacity: 1; }

.icon-btn {
  width: 26px;
  height: 26px;
  border: 1.5px solid var(--color-ink-300);
  background: var(--color-surface-elevated);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-ink-500);
  transition: all 0.12s;
  box-shadow: 1px 1px 0 var(--color-ink-200);
  text-decoration: none;
}

.icon-btn:hover {
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-color: var(--color-ink-800);
}

.icon-btn.danger:hover {
  background: var(--color-coral-500);
  border-color: var(--color-coral-500);
}

.icon-btn svg { width: 12px; height: 12px; }

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid var(--color-ink-300);
  font-size: 13px;
  color: var(--color-ink-800);
  outline: none;
  font-family: 'Courier New', monospace;
  background: var(--color-surface-elevated);
}

.form-input:focus {
  border-color: var(--color-warm-400);
  box-shadow: 2px 2px 0 var(--color-warm-100);
}
</style>
