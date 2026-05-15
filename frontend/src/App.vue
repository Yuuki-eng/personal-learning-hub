<template>
  <transition name="app-crossfade" mode="out-in">
    <GameMode v-if="gameVisible" @close="gameVisible = false" />
    <div v-else class="app-wrapper">
      <ParticleBackground />
      <TopBarButtons @focus="focusVisible = true" @game="gameVisible = true" />
      <FocusMode :visible="focusVisible" @close="focusVisible = false" />
      <div class="app-shell">
        <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
          <div class="sidebar-header">
            <div class="logo-area" @click="sidebarCollapsed = !sidebarCollapsed">
              <div class="logo-mark pixel-border">
                <span class="logo-glyph">&gt;_</span>
              </div>
              <transition name="fade">
                <span v-if="!sidebarCollapsed" class="logo-text">Hub</span>
              </transition>
            </div>
          </div>

          <nav class="sidebar-nav">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
            >
              <span class="nav-icon" v-html="item.icon"></span>
              <transition name="fade">
                <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
              </transition>
            </router-link>
          </nav>

          <div class="sidebar-footer">
            <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
              </span>
              <transition name="fade">
                <span v-if="!sidebarCollapsed" class="nav-label">{{ t('common.settings') }}</span>
              </transition>
            </router-link>
          </div>
        </aside>

        <main ref="mainEl" class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
          <transition name="hint-fade">
            <div v-if="scrollHint" class="scroll-hint-indicator" :class="scrollDirection">
              <div class="scroll-hint-arrow" :class="scrollDirection">
                <svg v-if="scrollDirection === 'up'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 6l5 5H5z"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 14l-5-5h10z"/></svg>
              </div>
              <span class="scroll-hint-text">{{ pageNameMap[scrollHint] || scrollHint }}</span>
            </div>
          </transition>
        </main>

        <MiniPlayer />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MiniPlayer from './components/MiniPlayer.vue'
import ParticleBackground from './components/ParticleBackground.vue'
import TopBarButtons from './components/TopBarButtons.vue'
import FocusMode from './components/FocusMode.vue'
import GameMode from './components/GameMode.vue'
import { useLocaleStore } from './stores/locale'

const route = useRoute()
const router = useRouter()
const sidebarCollapsed = ref(false)
const focusVisible = ref(false)
const gameVisible = ref(false)
const localeStore = useLocaleStore()
const t = localeStore.t

const pageOrder = ['/', '/blog', '/plan', '/countdown', '/music', '/files', '/ai']
const scrollHint = ref('')
const scrollDirection = ref('down')
const mainEl = ref(null)

const pageNameMap = computed(() => ({
  '/': t('common.home'),
  '/blog': t('common.blog'),
  '/plan': t('common.plan'),
  '/countdown': t('common.countdown'),
  '/music': t('common.music'),
  '/files': t('common.files'),
  '/ai': t('common.ai'),
}))

function getPageIndex() {
  return pageOrder.findIndex(p => p === '/' ? route.path === '/' : route.path.startsWith(p))
}

let navigating = false
let edgeHold = null
let edgeAccum = 0
let edgeDir = null
const EDGE_HOLD_MS = 250

function clearEdge() {
  if (edgeHold) { clearTimeout(edgeHold); edgeHold = null }
  edgeAccum = 0
  edgeDir = null
  scrollHint.value = ''
}

function triggerNavigate(dir) {
  const idx = getPageIndex()
  const targetIdx = dir === 'down' ? idx + 1 : idx - 1
  if (targetIdx < 0 || targetIdx >= pageOrder.length) return
  const target = pageOrder[targetIdx]
  navigating = true
  scrollHint.value = ''
  clearEdge()
  router.push(target).then(() => {
    nextTick(() => {
      if (mainEl.value) {
        mainEl.value.scrollTop = dir === 'down' ? 0 : mainEl.value.scrollHeight
      }
      setTimeout(() => { navigating = false }, 400)
    })
  })
}

function onWheel(e) {
  if (navigating) return
  const el = mainEl.value
  if (!el) return

  const idx = getPageIndex()
  if (idx < 0) return

  const scrollableHeight = el.scrollHeight - el.clientHeight
  const edgeTolerance = Math.min(50, scrollableHeight * 0.15 + 8)
  const atBottom = scrollableHeight - el.scrollTop <= edgeTolerance
  const atTop = el.scrollTop <= edgeTolerance
  const isScrollable = scrollableHeight > 20

  if (e.deltaY > 0) {
    if (isScrollable && !atBottom) {
      clearEdge()
      return
    }
    if (idx >= pageOrder.length - 1) { clearEdge(); return }
    const dir = 'down'
    const target = pageOrder[idx + 1]
    if (edgeDir !== dir) { clearEdge(); edgeDir = dir }
    scrollHint.value = target
    scrollDirection.value = dir
    edgeAccum += e.deltaY
    if (!edgeHold) {
      edgeHold = setTimeout(() => {
        edgeHold = null
        triggerNavigate(dir)
      }, EDGE_HOLD_MS)
    }
  } else if (e.deltaY < 0) {
    if (isScrollable && !atTop) {
      clearEdge()
      return
    }
    if (idx <= 0) { clearEdge(); return }
    const dir = 'up'
    const target = pageOrder[idx - 1]
    if (edgeDir !== dir) { clearEdge(); edgeDir = dir }
    scrollHint.value = target
    scrollDirection.value = dir
    edgeAccum += e.deltaY
    if (!edgeHold) {
      edgeHold = setTimeout(() => {
        edgeHold = null
        triggerNavigate(dir)
      }, EDGE_HOLD_MS)
    }
  }
}

function bindWheel() {
  const el = mainEl.value
  if (el) {
    el.removeEventListener('wheel', onWheel)
    el.addEventListener('wheel', onWheel, { passive: true })
  }
}

onMounted(() => {
  nextTick(bindWheel)
})
onUnmounted(() => {
  const el = mainEl.value
  if (el) el.removeEventListener('wheel', onWheel)
  clearEdge()
})

watch(() => route.path, () => {
  nextTick(() => {
    bindWheel()
    if (mainEl.value) mainEl.value.scrollTop = 0
  })
})

const navItems = computed(() => [
  {
    path: '/',
    label: t('common.home'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
  },
  {
    path: '/blog',
    label: t('common.blog'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>'
  },
  {
    path: '/plan',
    label: t('common.plan'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>'
  },
  {
    path: '/countdown',
    label: t('common.countdown'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
  },
  {
    path: '/music',
    label: t('common.music'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
  },
  {
    path: '/files',
    label: t('common.files'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>'
  },
  {
    path: '/ai',
    label: t('common.ai'),
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 014 4v1h1a3 3 0 013 3v1a3 3 0 01-3 3h-1v4a4 4 0 01-8 0v-4H7a3 3 0 01-3-3v-1a3 3 0 013-3h1V6a4 4 0 014-4z"/></svg>'
  },
])

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  min-height: 100dvh;
}

.app-crossfade-enter-active {
  transition: opacity 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.app-crossfade-leave-active {
  transition: opacity 0.2s ease;
}
.app-crossfade-enter-from,
.app-crossfade-leave-to {
  opacity: 0;
}

.app-shell {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  position: relative;
  z-index: 1;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 210px;
  background: rgba(250, 248, 244, 0.92);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  border-right: 2px solid var(--color-ink-200);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  overflow: hidden;
}

.sidebar.collapsed {
  width: 62px;
}

.sidebar-header {
  padding: 22px 14px 6px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px;
  transition: background 0.15s;
}

.logo-area:hover {
  background: var(--color-ink-50);
}

.logo-mark {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-ink-800);
}

.logo-glyph {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-warm-50);
  letter-spacing: -0.05em;
}

.logo-text {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: var(--color-ink-800);
  font-family: 'Courier New', monospace;
}

.sidebar-nav {
  flex: 1;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  color: var(--color-ink-500);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.02em;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  position: relative;
  border: 1.5px solid transparent;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, var(--color-warm-200) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.6s ease, height 0.6s ease, opacity 0.4s ease;
  opacity: 0;
  z-index: -1;
  pointer-events: none;
}

.nav-item:hover::before {
  width: 250%;
  height: 250%;
  opacity: 0.5;
}

.nav-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s ease;
  z-index: 1;
  pointer-events: none;
}

.nav-item:hover::after {
  left: 100%;
}

.nav-item:hover {
  color: var(--color-ink-800);
  background: rgba(255, 255, 255, 0.5);
  border-color: var(--color-ink-100);
  transform: translateX(3px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.nav-item.active {
  color: var(--color-warm-50);
  background: var(--color-ink-800);
  border-color: var(--color-ink-800);
  box-shadow: 2px 2px 0 var(--color-ink-400);
}

.nav-item.active:hover {
  transform: translateX(3px);
  box-shadow: 3px 3px 0 var(--color-ink-400);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.sidebar-footer {
  padding: 10px 8px 16px;
  border-top: 2px solid var(--color-ink-200);
}

.main-content {
  margin-left: 210px;
  flex: 1;
  padding: 64px 40px 120px;
  height: 100vh;
  height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  transition: margin-left 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  max-width: 100%;
  scroll-behavior: smooth;
}

.main-content.sidebar-collapsed {
  margin-left: 62px;
}

.page-enter-active {
  transition: opacity 0.4s cubic-bezier(0.22, 1, 0.36, 1), transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.scroll-hint-indicator {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 0 40px;
  pointer-events: none;
}
.scroll-hint-arrow {
  color: rgba(0, 0, 0, 0.25);
}
.scroll-hint-arrow.down {
  animation: bounceDown 1.2s ease-in-out infinite;
}
.scroll-hint-arrow.up {
  animation: bounceUp 1.2s ease-in-out infinite;
}
.scroll-hint-text {
  font-family: 'SF Mono', 'Courier New', monospace;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(0, 0, 0, 0.2);
}
@keyframes bounceDown {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(6px); }
}
@keyframes bounceUp {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.hint-fade-enter-active { transition: opacity 0.3s; }
.hint-fade-leave-active { transition: opacity 0.15s; }
.hint-fade-enter-from,
.hint-fade-leave-to { opacity: 0; }

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .sidebar {
    width: 62px;
  }
  .main-content {
    margin-left: 62px;
    padding: 20px 16px 120px;
  }
}
</style>
