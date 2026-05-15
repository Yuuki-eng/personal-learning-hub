<template>
  <div class="plan-page page-enter">
    <div v-animate="'fade-up'" class="plan-top">
      <div>
        <h1 class="page-title">Plans</h1>
        <p class="page-desc">Track your learning goals and progress</p>
      </div>
      <button class="btn-primary" @click="showDialog = true">New Plan</button>
    </div>

    <div v-animate="{ name: 'fade-up', delay: 80 }" class="plan-tabs">
      <button v-for="tab in tabs" :key="tab.value" class="tab-btn" :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value">
        {{ tab.label }}
        <span class="tab-count">{{ getCount(tab.value) }}</span>
      </button>
    </div>

    <div v-if="filteredPlans.length === 0" class="empty-state">
      <p>No {{ activeTab === 'all' ? '' : activeTab }} plans</p>
    </div>

    <div v-else class="plan-list">
      <div v-for="(plan, i) in filteredPlans" :key="plan.id"
        v-animate="{ name: 'fade-left', delay: i * 60 }"
        class="plan-card" :class="plan.status">
        <div class="plan-card-header">
          <div class="plan-status-dot" :class="plan.status"></div>
          <div class="plan-card-meta">
            <span class="plan-priority" :class="plan.priority">{{ plan.priority }}</span>
            <span v-if="plan.deadline" class="plan-deadline" :class="{ urgent: isUrgent(plan), overdue: isOverdue(plan) }">
              {{ formatDeadline(plan) }}
            </span>
          </div>
          <div class="plan-card-actions">
            <select v-model="plan.status" @change="handleStatusChange(plan)" class="status-select">
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
            <button class="icon-btn" @click="editPlan(plan)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
            <button class="icon-btn danger" @click="handleDelete(plan.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            </button>
          </div>
        </div>
        <h3 class="plan-title">{{ plan.title }}</h3>
        <p v-if="plan.description" class="plan-desc">{{ plan.description }}</p>
        <div class="plan-progress-bar">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: plan.progress + '%' }"></div>
          </div>
          <span class="progress-text">{{ plan.progress }}%</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="showDialog" :title="editingPlan ? 'Edit Plan' : 'New Plan'" width="480px" :close-on-click-modal="false">
      <div class="dialog-form">
        <div class="form-group">
          <label>Title</label>
          <input v-model="form.title" type="text" class="form-input" placeholder="What do you want to learn?" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" class="form-textarea" rows="3" placeholder="Details..."></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Priority</label>
            <select v-model="form.priority" class="form-input">
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div class="form-group">
            <label>Deadline</label>
            <input v-model="form.deadline" type="date" class="form-input" />
          </div>
        </div>
        <div class="form-group" v-if="editingPlan">
          <label>Progress ({{ form.progress }}%)</label>
          <input v-model.number="form.progress" type="range" min="0" max="100" class="range-input" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="showDialog = false">Cancel</button>
        <button class="btn-primary" @click="handleSave" :disabled="saving">{{ saving ? 'Saving...' : (editingPlan ? 'Update' : 'Create') }}</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getPlans, createPlan, updatePlan, deletePlan, updatePlanStatus } from '../api/plan'
import { ElMessage, ElMessageBox } from 'element-plus'

const plans = ref([])
const activeTab = ref('all')
const showDialog = ref(false)
const editingPlan = ref(null)
const saving = ref(false)

const form = ref({
  title: '', description: '', priority: 'medium', deadline: '', progress: 0,
})

const tabs = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'Active' },
  { value: 'completed', label: 'Done' },
]

const filteredPlans = computed(() => {
  if (activeTab.value === 'all') return plans.value
  return plans.value.filter(p => p.status === activeTab.value)
})

function getCount(tab) {
  if (tab === 'all') return plans.value.length
  return plans.value.filter(p => p.status === tab).length
}

const now = ref(Date.now())
let timer = null

function formatDeadline(plan) {
  if (!plan.deadline) return ''
  const deadline = new Date(plan.deadline)
  const diff = deadline - now.value

  if (diff <= 0) {
    const absDiff = Math.abs(diff)
    if (absDiff < 60000) return 'Just passed'
    if (absDiff < 3600000) return `Passed ${Math.floor(absDiff / 60000)}m ago`
    if (absDiff < 86400000) return `Passed ${Math.floor(absDiff / 3600000)}h ago`
    return `Passed ${Math.floor(absDiff / 86400000)}d ago`
  }

  if (diff < 86400000) {
    const h = Math.floor(diff / 3600000)
    const m = Math.floor((diff % 3600000) / 60000)
    const s = Math.floor((diff % 60000) / 1000)
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const days = Math.floor(diff / 86400000)
  const h = Math.floor((diff % 86400000) / 3600000)
  return `${days}d ${h}h left`
}

function isUrgent(plan) {
  if (!plan.deadline || plan.status === 'completed') return false
  const diff = new Date(plan.deadline) - now.value
  return diff > 0 && diff < 86400000
}

function isOverdue(plan) {
  if (!plan.deadline || plan.status === 'completed') return false
  return new Date(plan.deadline) < now.value
}

function editPlan(plan) {
  editingPlan.value = plan
  form.value = {
    title: plan.title,
    description: plan.description || '',
    priority: plan.priority,
    deadline: plan.deadline || '',
    progress: plan.progress,
  }
  showDialog.value = true
}

async function handleSave() {
  if (saving.value) return
  if (!form.value.title.trim()) { ElMessage.warning('Title required'); return }
  saving.value = true
  try {
    if (editingPlan.value) {
      await updatePlan(editingPlan.value.id, form.value)
      ElMessage.success('Updated')
    } else {
      await createPlan(form.value)
      ElMessage.success('Created')
    }
    showDialog.value = false
    editingPlan.value = null
    form.value = { title: '', description: '', priority: 'medium', deadline: '', progress: 0 }
    await fetchPlans()
  } catch {}
  saving.value = false
}

async function handleStatusChange(plan) {
  try {
    await updatePlanStatus(plan.id, plan.status)
    if (plan.status === 'completed') plan.progress = 100
  } catch {}
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('Delete this plan?', 'Confirm', { type: 'warning' })
    await deletePlan(id)
    await fetchPlans()
  } catch {}
}

async function fetchPlans() {
  plans.value = await getPlans()
}

onMounted(() => {
  fetchPlans()
  timer = setInterval(() => { now.value = Date.now() }, 1000)
})

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.plan-page { max-width: 800px; }

.plan-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title { font-size: 28px; font-weight: 700; color: var(--color-ink-900); letter-spacing: -0.02em; }
.page-desc { color: var(--color-ink-400); font-size: 14px; margin-top: 4px; }

.plan-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: var(--color-ink-50);
  border-radius: 12px;
  padding: 4px;
  width: fit-content;
}

.tab-btn {
  padding: 7px 16px;
  border: none;
  border-radius: 9px;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink-500);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover { color: var(--color-ink-700); }

.tab-btn.active {
  background: var(--color-surface-elevated);
  color: var(--color-ink-800);
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.tab-count {
  font-size: 11px;
  background: var(--color-ink-100);
  padding: 1px 6px;
  border-radius: 5px;
}

.tab-btn.active .tab-count { background: var(--color-warm-100); color: var(--color-warm-700); }

.empty-state {
  text-align: center;
  padding: 50px;
  color: var(--color-ink-400);
}

.plan-list { display: flex; flex-direction: column; gap: 10px; }

.plan-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 14px;
  padding: 18px 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.plan-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}

.plan-card.completed { opacity: 0.7; }
.plan-card.completed .plan-title { text-decoration: line-through; color: var(--color-ink-400); }

.plan-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.plan-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.plan-status-dot.pending { background: var(--color-ink-300); }
.plan-status-dot.in_progress { background: var(--color-warm-400); animation: breathe 2s infinite; }
.plan-status-dot.completed { background: var(--color-sage-500); }

@keyframes breathe { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.plan-card-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.plan-priority {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.plan-priority.high { background: #fef2f2; color: #b91c1c; }
.plan-priority.medium { background: #fffbeb; color: #b45309; }
.plan-priority.low { background: #f0fdf4; color: #15803d; }

.plan-deadline { font-size: 12px; color: var(--color-ink-400); }

.plan-deadline.urgent {
  color: #b45309;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  background: #fef3c7;
  padding: 1px 6px;
  border-radius: 4px;
}

.plan-deadline.overdue {
  color: #b91c1c;
  font-weight: 600;
  font-size: 11px;
  background: #fef2f2;
  padding: 1px 6px;
  border-radius: 4px;
}

.plan-card-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-select {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--color-ink-200);
  border-radius: 8px;
  background: var(--color-surface-elevated);
  color: var(--color-ink-600);
  cursor: pointer;
  outline: none;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-ink-400);
  transition: all 0.2s;
}

.icon-btn:hover { background: var(--color-ink-50); color: var(--color-ink-700); }
.icon-btn.danger:hover { background: #fef2f2; color: #b91c1c; }
.icon-btn svg { width: 15px; height: 15px; }

.plan-title { font-size: 15px; font-weight: 600; color: var(--color-ink-800); margin-bottom: 4px; }
.plan-desc { font-size: 13px; color: var(--color-ink-400); margin-bottom: 10px; line-height: 1.5; }

.plan-progress-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-track {
  flex: 1;
  height: 4px;
  background: var(--color-ink-100);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-warm-400);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-ink-500);
  min-width: 35px;
  text-align: right;
}

.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 13px; font-weight: 500; color: var(--color-ink-600); }
.form-input {
  padding: 8px 12px;
  border: 1px solid var(--color-ink-200);
  border-radius: 10px;
  font-size: 14px;
  color: var(--color-ink-800);
  outline: none;
  transition: border-color 0.2s;
}
.form-input:focus { border-color: var(--color-warm-400); }
.form-textarea {
  padding: 8px 12px;
  border: 1px solid var(--color-ink-200);
  border-radius: 10px;
  font-size: 14px;
  color: var(--color-ink-800);
  outline: none;
  resize: vertical;
  font-family: inherit;
}
.form-textarea:focus { border-color: var(--color-warm-400); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.range-input {
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  background: var(--color-ink-100);
  border-radius: 3px;
  outline: none;
}
.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-warm-500);
  cursor: pointer;
}
</style>
