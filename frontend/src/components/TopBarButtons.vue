<template>
  <div class="topbar-buttons">
    <div class="topbar-btn" @click="$emit('focus')" :data-tooltip="t('topbar.focusMode')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
      </svg>
    </div>

    <div class="topbar-btn" @click="$emit('game')" :data-tooltip="t('topbar.gameMode')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <rect x="2" y="6" width="20" height="12" rx="3"/>
        <line x1="7" y1="12" x2="11" y2="12"/><line x1="9" y1="10" x2="9" y2="14"/>
        <circle cx="16" cy="10" r="0.8" fill="currentColor"/><circle cx="18.5" cy="12" r="0.8" fill="currentColor"/>
      </svg>
    </div>

    <div class="topbar-btn" :class="{ loading: jumping }" @click="handleJump" :data-tooltip="jumpTooltip">
      <transition name="spin-fade" mode="out-in">
        <svg v-if="!jumping" key="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
          <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        <svg v-else key="loading" class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M12 2a10 10 0 019.95 9"/>
        </svg>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLocaleStore } from '../stores/locale'

const emit = defineEmits(['focus', 'game'])

const localeStore = useLocaleStore()
const t = localeStore.t

const jumping = ref(false)

const jumpUrls = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('customJumpUrls') || '[]')
  } catch { return [] }
})

const jumpTooltip = computed(() => {
  return jumpUrls.value.length > 0 ? t('topbar.openLink') : t('topbar.noLinks')
})

function handleJump() {
  const urls = jumpUrls.value
  if (urls.length === 0) {
    return
  }
  jumping.value = true
  const url = urls[0]
  setTimeout(() => {
    window.open(url, '_blank', 'noopener')
    jumping.value = false
  }, 500)
}
</script>

<style scoped>
.topbar-buttons {
  position: fixed;
  top: 16px;
  right: 24px;
  display: flex;
  gap: 16px;
  z-index: 200;
}

.topbar-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(250, 248, 244, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1.5px solid var(--color-ink-200);
  color: var(--color-ink-500);
  position: relative;
  transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s, color 0.2s, border-color 0.2s;
}
.topbar-btn svg {
  width: 18px;
  height: 18px;
}
.topbar-btn:hover {
  transform: scale(1.12);
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  color: var(--color-ink-800);
  border-color: var(--color-ink-300);
}
.topbar-btn:active {
  transform: scale(0.95);
}

.topbar-btn.disabled {
  opacity: 0.4;
  cursor: default;
  pointer-events: auto;
}
.topbar-btn.disabled:hover {
  transform: scale(1);
  box-shadow: none;
  color: var(--color-ink-500);
  border-color: var(--color-ink-200);
}

.topbar-btn::after {
  content: attr(data-tooltip);
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  white-space: nowrap;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-ink-700);
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-200);
  border-radius: 6px;
  padding: 4px 10px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 0.2s, transform 0.2s;
  transition-delay: 0s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.topbar-btn:hover::after {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.4s;
}

.spin-icon {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin-fade-enter-active { transition: opacity 0.15s, transform 0.15s; }
.spin-fade-leave-active { transition: opacity 0.1s, transform 0.1s; }
.spin-fade-enter-from { opacity: 0; transform: scale(0.8); }
.spin-fade-leave-to { opacity: 0; transform: scale(0.8); }

@media (max-width: 768px) {
  .topbar-buttons {
    top: 12px;
    right: 12px;
    gap: 10px;
  }
  .topbar-btn {
    width: 34px;
    height: 34px;
  }
}
</style>
