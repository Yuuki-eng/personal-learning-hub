<template>
  <div class="countdown-page page-enter">
    <div v-animate="'fade-up'" class="cd-top">
      <div>
        <h1 class="page-title">Countdown</h1>
        <p class="page-desc">Track important dates and milestones</p>
      </div>
      <button class="btn-primary" @click="showDialog = true">New Countdown</button>
    </div>

    <div v-if="countdowns.length === 0" v-animate="'scale-in'" class="empty-state">
      <div class="empty-visual">
        <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
          <circle cx="32" cy="32" r="28"/>
          <path d="M32 16v18l10 6"/>
        </svg>
      </div>
      <p>No countdowns yet</p>
      <p class="empty-hint">Create one to start tracking important dates</p>
    </div>

    <div v-else class="cd-grid">
      <div v-for="(cd, i) in countdowns" :key="cd.id"
        v-animate="{ name: 'scale-in', delay: i * 80 }"
        class="cd-card"
        :style="{ '--accent': cd.color || '#e8927c' }">
        <div class="cd-card-header">
          <div class="cd-color-dot" :style="{ background: cd.color || '#e8927c' }"></div>
          <div class="cd-card-actions">
            <button class="icon-btn" @click="editItem(cd)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
            <button class="icon-btn danger" @click="handleDelete(cd.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            </button>
          </div>
        </div>
        <h3 class="cd-card-title">{{ cd.title }}</h3>
        <p v-if="cd.description" class="cd-card-desc">{{ cd.description }}</p>
        <div class="cd-card-date">{{ formatTarget(cd.target_datetime) }}</div>
        <div class="cd-card-timer" :class="{ passed: getTimeLeft(cd.target_datetime).total <= 0 }">
          <template v-if="getTimeLeft(cd.target_datetime).total > 0">
            <div class="timer-block">
              <span class="timer-num">{{ getTimeLeft(cd.target_datetime).days }}</span>
              <span class="timer-label">Days</span>
            </div>
            <div class="timer-sep">:</div>
            <div class="timer-block">
              <span class="timer-num">{{ pad(getTimeLeft(cd.target_datetime).hours) }}</span>
              <span class="timer-label">Hours</span>
            </div>
            <div class="timer-sep">:</div>
            <div class="timer-block">
              <span class="timer-num">{{ pad(getTimeLeft(cd.target_datetime).minutes) }}</span>
              <span class="timer-label">Min</span>
            </div>
            <div class="timer-sep">:</div>
            <div class="timer-block">
              <span class="timer-num">{{ pad(getTimeLeft(cd.target_datetime).seconds) }}</span>
              <span class="timer-label">Sec</span>
            </div>
          </template>
          <template v-else>
            <div class="passed-text">Passed {{ getPassedDays(cd.target_datetime) }} days ago</div>
          </template>
        </div>
      </div>
    </div>

    <el-dialog v-model="showDialog" :title="editing ? 'Edit Countdown' : 'New Countdown'" width="440px">
      <div class="dialog-form">
        <div class="form-group">
          <label>Title</label>
          <input v-model="form.title" type="text" class="form-input" placeholder="Event name" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <input v-model="form.description" type="text" class="form-input" placeholder="Optional" />
        </div>
        <div class="form-group">
          <label>Target Date & Time</label>
          <input v-model="form.target_datetime" type="datetime-local" class="form-input" />
        </div>
        <div class="form-group">
          <label>Color</label>
          <div class="color-options">
            <button v-for="c in colorOptions" :key="c" class="color-dot"
              :style="{ background: c }" :class="{ selected: form.color === c }"
              @click="form.color = c"></button>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="showDialog = false">Cancel</button>
        <button class="btn-primary" @click="handleSave">{{ editing ? 'Update' : 'Create' }}</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getCountdowns, createCountdown, updateCountdown, deleteCountdown } from '../api/countdown'
import { ElMessage, ElMessageBox } from 'element-plus'

const countdowns = ref([])
const showDialog = ref(false)
const editing = ref(null)
let timer = null

const form = ref({
  title: '', description: '', target_datetime: '', color: '#e8927c'
})

const colorOptions = ['#e8927c', '#658a4e', '#c87a32', '#5b8def', '#9d6bbf', '#d4446a']

function pad(n) { return String(n).padStart(2, '0') }

function getTimeLeft(target) {
  const diff = new Date(target) - new Date()
  if (diff <= 0) return { total: 0, days: 0, hours: 0, minutes: 0, seconds: 0 }
  return {
    total: diff,
    days: Math.floor(diff / 86400000),
    hours: Math.floor((diff % 86400000) / 3600000),
    minutes: Math.floor((diff % 3600000) / 60000),
    seconds: Math.floor((diff % 60000) / 1000),
  }
}

function getPassedDays(target) {
  const diff = new Date() - new Date(target)
  return Math.floor(diff / 86400000)
}

function formatTarget(d) {
  return new Date(d).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function editItem(cd) {
  editing.value = cd
  form.value = {
    title: cd.title,
    description: cd.description || '',
    target_datetime: new Date(cd.target_datetime).toISOString().slice(0, 16),
    color: cd.color || '#e8927c',
  }
  showDialog.value = true
}

async function handleSave() {
  if (!form.value.title.trim() || !form.value.target_datetime) {
    ElMessage.warning('Title and date required')
    return
  }
  try {
    const data = { ...form.value, target_datetime: new Date(form.value.target_datetime).toISOString() }
    if (editing.value) {
      await updateCountdown(editing.value.id, data)
      ElMessage.success('Updated')
    } else {
      await createCountdown(data)
      ElMessage.success('Created')
    }
    showDialog.value = false
    editing.value = null
    form.value = { title: '', description: '', target_datetime: '', color: '#e8927c' }
    await fetch()
  } catch {}
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('Delete?', 'Confirm', { type: 'warning' })
    await deleteCountdown(id)
    await fetch()
  } catch {}
}

async function fetch() {
  countdowns.value = await getCountdowns()
}

onMounted(() => {
  fetch()
  timer = setInterval(() => {}, 1000)
})

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.countdown-page { max-width: 900px; }

.cd-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title { font-size: 28px; font-weight: 700; color: var(--color-ink-900); letter-spacing: -0.02em; }
.page-desc { color: var(--color-ink-400); font-size: 14px; margin-top: 4px; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-visual { width: 64px; height: 64px; margin: 0 auto 16px; color: var(--color-ink-200); }
.empty-state p { color: var(--color-ink-500); font-size: 15px; }
.empty-hint { color: var(--color-ink-300); font-size: 13px; margin-top: 4px; }

.cd-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 700px) { .cd-grid { grid-template-columns: 1fr; } }

.cd-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-top: 3px solid var(--accent);
  border-radius: 14px;
  padding: 20px;
  transition: transform 0.25s, box-shadow 0.25s;
  animation: fadeSlideUp 0.4s ease both;
}

.cd-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(26, 22, 20, 0.06);
}

.cd-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cd-color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.cd-card-actions { display: flex; gap: 2px; }

.icon-btn {
  width: 28px; height: 28px; border: none; background: transparent;
  border-radius: 7px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--color-ink-300); transition: all 0.2s;
}
.icon-btn:hover { background: var(--color-ink-50); color: var(--color-ink-600); }
.icon-btn.danger:hover { background: #fef2f2; color: #b91c1c; }
.icon-btn svg { width: 14px; height: 14px; }

.cd-card-title { font-size: 17px; font-weight: 600; color: var(--color-ink-800); margin-bottom: 4px; }
.cd-card-desc { font-size: 13px; color: var(--color-ink-400); margin-bottom: 8px; }
.cd-card-date { font-size: 12px; color: var(--color-ink-300); margin-bottom: 14px; }

.cd-card-timer {
  display: flex;
  align-items: center;
  gap: 4px;
}

.timer-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--color-ink-50);
  border-radius: 10px;
  padding: 8px 12px;
  min-width: 52px;
}

.timer-num {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-ink-800);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.timer-label {
  font-size: 10px;
  color: var(--color-ink-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 2px;
}

.timer-sep {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-ink-200);
  padding-bottom: 14px;
}

.cd-card-timer.passed .timer-block { background: var(--color-warm-50); }

.passed-text {
  font-size: 14px;
  color: var(--color-ink-400);
  font-style: italic;
}

.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 13px; font-weight: 500; color: var(--color-ink-600); }
.form-input {
  padding: 8px 12px; border: 1px solid var(--color-ink-200); border-radius: 10px;
  font-size: 14px; color: var(--color-ink-800); outline: none; transition: border-color 0.2s;
}
.form-input:focus { border-color: var(--color-warm-400); }

.color-options { display: flex; gap: 8px; }
.color-dot {
  width: 28px; height: 28px; border-radius: 50%; border: 2px solid transparent;
  cursor: pointer; transition: all 0.2s;
}
.color-dot:hover { transform: scale(1.15); }
.color-dot.selected { border-color: var(--color-ink-800); box-shadow: 0 0 0 2px var(--color-surface-elevated), 0 0 0 4px var(--color-ink-800); }

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
