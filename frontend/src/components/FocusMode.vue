<template>
  <teleport to="body">
    <transition name="focus-overlay">
      <div v-if="visible" class="focus-overlay" @keydown.esc="close" tabindex="0" ref="overlayRef">
        <div class="focus-glass-bg"></div>
        <div class="focus-dark-overlay"></div>

        <div class="focus-close liquid-btn" @click="close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>

        <div class="focus-settings-trigger liquid-btn" @click="settingsOpen = !settingsOpen" :class="{ active: settingsOpen }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </div>

        <transition name="settings-slide">
          <div v-if="settingsOpen" class="focus-settings-panel">
            <div class="setting-group">
              <label class="setting-label">{{ t('focus.brightness') }}</label>
              <div class="setting-slider-row">
                <input type="range" min="0" max="100" step="1" v-model.number="brightness" class="setting-slider" />
                <span class="setting-val">{{ brightness }}%</span>
              </div>
              <div class="brightness-indicator">
                <span class="brightness-label-dim">{{ t('focus.dark') }}</span>
                <span class="brightness-label-frost">{{ t('focus.frosted') }}</span>
              </div>
            </div>
            <div class="setting-group">
              <label class="setting-label">{{ t('focus.visStyle') || 'Visualizer Style' }}</label>
              <div class="style-chips">
                <button class="style-chip" :class="{ active: visStyle === 'bars' }" @click="visStyle = 'bars'">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><rect x="2" y="12" width="3" height="10" rx="1"/><rect x="7" y="8" width="3" height="14" rx="1"/><rect x="12" y="5" width="3" height="17" rx="1"/><rect x="17" y="10" width="3" height="12" rx="1"/></svg>
                  {{ t('focus.bars') || 'Bars' }}
                </button>
                <button class="style-chip" :class="{ active: visStyle === 'wave' }" @click="visStyle = 'wave'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12c2-4 4 4 6 0s4 4 6 0 4 4 6 0"/></svg>
                  {{ t('focus.wave') || 'Wave' }}
                </button>
                <button class="style-chip" :class="{ active: visStyle === 'circular' }" @click="visStyle = 'circular'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/></svg>
                  {{ t('focus.circular') || 'Circle' }}
                </button>
              </div>
            </div>
            <div class="setting-group">
              <label class="setting-label">{{ t('focus.visOpacity') || 'Visualizer Opacity' }}</label>
              <div class="setting-slider-row">
                <input type="range" min="0.1" max="1" step="0.05" v-model.number="visOpacity" class="setting-slider" />
                <span class="setting-val">{{ Math.round(visOpacity * 100) }}%</span>
              </div>
            </div>
            <div class="setting-group">
              <label class="setting-label">{{ t('focus.glow') || 'Glow Intensity' }}</label>
              <div class="setting-slider-row">
                <input type="range" min="0" max="1" step="0.05" v-model.number="glowIntensity" class="setting-slider" />
                <span class="setting-val">{{ Math.round(glowIntensity * 100) }}%</span>
              </div>
            </div>
            <div class="setting-group">
              <label class="setting-label">{{ t('focus.colorTheme') || 'Color Theme' }}</label>
              <div class="theme-dots">
                <button v-for="th in themes" :key="th.name" class="theme-dot" :style="{ background: th.preview }" :class="{ active: colorTheme === th.name }" @click="colorTheme = th.name"></button>
              </div>
            </div>
          </div>
        </transition>

        <div class="focus-center" :class="{ 'circular-mode': visStyle === 'circular' }">
          <div class="focus-timer-wrap" @click="openEditor">
            <transition name="timer-switch" mode="out-in">
              <div v-if="!showEditor" key="display" class="focus-timer-display">
                <span class="timer-digits">{{ displayTime }}</span>
                <span class="timer-edit-hint">{{ t('focus.clickToEdit') || 'click to edit' }}</span>
              </div>
              <div v-else key="editor" class="focus-timer-editor" @click.stop>
                <div class="editor-row">
                  <div class="editor-col">
                    <button class="spin-btn" @click.stop="adjustHour(1)">&#9650;</button>
                    <input type="number" min="0" max="23" v-model.number="editH" class="editor-input" @wheel.prevent="editH = Math.max(0, Math.min(23, editH + ($event.deltaY < 0 ? 1 : -1)))" @click.stop />
                    <button class="spin-btn" @click.stop="adjustHour(-1)"><svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 10L2 4h8z"/></svg></button>
                    <span class="editor-label">H</span>
                  </div>
                  <span class="editor-sep">:</span>
                  <div class="editor-col">
                    <button class="spin-btn" @click.stop="adjustMin(1)"><svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 2L10 8H2z"/></svg></button>
                    <input type="number" min="0" max="59" v-model.number="editM" class="editor-input" @wheel.prevent="editM = Math.max(0, Math.min(59, editM + ($event.deltaY < 0 ? 1 : -1)))" @click.stop />
                    <button class="spin-btn" @click.stop="adjustMin(-1)"><svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 10L2 4h8z"/></svg></button>
                    <span class="editor-label">M</span>
                  </div>
                  <span class="editor-sep">:</span>
                  <div class="editor-col">
                    <button class="spin-btn" @click.stop="adjustSec(1)"><svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 2L10 8H2z"/></svg></button>
                    <input type="number" min="0" max="59" v-model.number="editS" class="editor-input" @wheel.prevent="editS = Math.max(0, Math.min(59, editS + ($event.deltaY < 0 ? 1 : -1)))" @click.stop />
                    <button class="spin-btn" @click.stop="adjustSec(-1)"><svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 10L2 4h8z"/></svg></button>
                    <span class="editor-label">S</span>
                  </div>
                </div>
                <div class="editor-actions">
                  <button class="editor-btn confirm" @click.stop="confirmTime">{{ t('focus.confirm') }}</button>
                  <button class="editor-btn" @click.stop="showEditor = false">{{ t('common.cancel') }}</button>
                </div>
              </div>
            </transition>
          </div>

          <div class="focus-mode-label">
            <span class="mode-chip" :class="{ active: mode === 'countdown' }" @click="mode = 'countdown'">{{ t('focus.countdown') }}</span>
            <span class="mode-chip" :class="{ active: mode === 'stopwatch' }" @click="mode = 'stopwatch'">{{ t('focus.stopwatch') }}</span>
          </div>

          <div class="spectrum-wrap" :class="{ circular: visStyle === 'circular' }">
            <canvas ref="spectrumCanvas" class="focus-spectrum"></canvas>
          </div>

          <div class="focus-actions">
            <button class="focus-action-btn" :class="{ running }" @click="toggleTimer">
              <svg v-if="!running" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
              <span>{{ running ? t('focus.pause') : t('focus.start') }}</span>
            </button>
            <button class="focus-action-btn" @click="resetTimer">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 105.64-11.36L1 10"/>
              </svg>
              <span>{{ t('focus.reset') }}</span>
            </button>
            <button class="focus-action-btn" :class="{ active: musicActive }" @click="toggleMusic">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
              </svg>
              <span>{{ t('focus.music') }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount, nextTick } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { usePlayerStore } from '../stores/player'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['close'])

const localeStore = useLocaleStore()
const t = localeStore.t
const player = usePlayerStore()

const mode = ref('stopwatch')
const running = ref(false)
const seconds = ref(0)
const editH = ref(0)
const editM = ref(25)
const editS = ref(0)
const showEditor = ref(false)
const musicActive = ref(false)
const spectrumCanvas = ref(null)
const overlayRef = ref(null)
const settingsOpen = ref(false)

const brightness = ref(0)
const visOpacity = ref(0.8)
const glowIntensity = ref(0.6)
const visStyle = ref('bars')
const colorTheme = ref('warm')

const themes = [
  { name: 'warm', preview: 'linear-gradient(135deg, #e8927c, #ffc864)', hStart: 15, hEnd: 50 },
  { name: 'ocean', preview: 'linear-gradient(135deg, #5b9bd5, #7ec8e3)', hStart: 195, hEnd: 215 },
  { name: 'forest', preview: 'linear-gradient(135deg, #6baa75, #a8c58f)', hStart: 100, hEnd: 140 },
  { name: 'violet', preview: 'linear-gradient(135deg, #9b7dd4, #c9a0dc)', hStart: 260, hEnd: 290 },
]

const currentTheme = computed(() => themes.find(th => th.name === colorTheme.value) || themes[0])

const overlayOpacity = computed(() => {
  return 1 - brightness.value / 100
})
const glassOpacity = computed(() => {
  const b = brightness.value / 100
  return Math.max(0, (b - 0.3) / 0.7)
})

let timerId = null
let rafId = null
let smoothData = null

const displayTime = computed(() => {
  const s = Math.max(0, Math.floor(seconds.value))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
})

function adjustHour(d) { editH.value = Math.max(0, Math.min(23, editH.value + d)) }
function adjustMin(d) { editM.value = Math.max(0, Math.min(59, editM.value + d)) }
function adjustSec(d) { editS.value = Math.max(0, Math.min(59, editS.value + d)) }

function confirmTime() {
  const total = editH.value * 3600 + editM.value * 60 + editS.value
  seconds.value = total
  showEditor.value = false
  if (running.value) {
    clearInterval(timerId)
    timerId = null
    running.value = false
  }
  if (total > 0) {
    mode.value = 'countdown'
  } else {
    mode.value = 'stopwatch'
  }
}

function openEditor() {
  if (showEditor.value) return
  if (running.value) return
  showEditor.value = true
}

function toggleTimer() {
  if (running.value) {
    clearInterval(timerId)
    timerId = null
    running.value = false
  } else {
    running.value = true
    timerId = setInterval(() => {
      if (mode.value === 'stopwatch') {
        seconds.value++
      } else {
        if (seconds.value <= 0) {
          clearInterval(timerId)
          timerId = null
          running.value = false
          return
        }
        seconds.value--
      }
    }, 1000)
  }
}

function resetTimer() {
  running.value = false
  if (timerId) { clearInterval(timerId); timerId = null }
  seconds.value = mode.value === 'countdown' ? (editH.value * 3600 + editM.value * 60 + editS.value) : 0
}

function toggleMusic() {
  musicActive.value = !musicActive.value
  if (musicActive.value && player.currentSong) {
    player.togglePlay()
  } else if (!musicActive.value) {
    if (player.isPlaying) player.togglePlay()
  }
}

function resizeCanvas() {
  const canvas = spectrumCanvas.value
  if (!canvas) return
  const dpr = window.devicePixelRatio || 1
  const parent = canvas.parentElement
  if (!parent) return
  const w = parent.clientWidth
  const h = parent.clientHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'
}

function drawSpectrum() {
  const canvas = spectrumCanvas.value
  if (!canvas) { rafId = requestAnimationFrame(drawSpectrum); return }

  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const w = canvas.width / dpr
  const h = canvas.height / dpr

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, w, h)

  const analyser = player.analyser
  const barCount = 48
  let data

  if (analyser) {
    const bufLen = analyser.frequencyBinCount
    const rawData = new Uint8Array(bufLen)
    analyser.getByteFrequencyData(rawData)
    if (!smoothData || smoothData.length !== barCount) smoothData = new Float32Array(barCount)
    const step = Math.floor(bufLen / barCount)
    data = new Float32Array(barCount)
    for (let i = 0; i < barCount; i++) {
      let sum = 0
      for (let j = 0; j < step; j++) sum += rawData[i * step + j]
      const raw = (sum / step) / 255
      smoothData[i] += (raw - smoothData[i]) * 0.15
      data[i] = smoothData[i]
    }
  } else {
    if (!smoothData || smoothData.length !== barCount) smoothData = new Float32Array(barCount)
    const t = performance.now() / 1000
    data = new Float32Array(barCount)
    for (let i = 0; i < barCount; i++) {
      const raw = 0.08 + 0.06 * Math.sin(t * 0.5 + i * 0.3) + 0.04 * Math.sin(t * 1.3 + i * 0.5)
      smoothData[i] += (raw - smoothData[i]) * 0.08
      data[i] = smoothData[i]
    }
  }

  const th = currentTheme.value
  const alpha = visOpacity.value
  const glow = glowIntensity.value

  if (visStyle.value === 'bars') {
    drawBars(ctx, w, h, data, th, alpha, glow)
  } else if (visStyle.value === 'wave') {
    drawWave(ctx, w, h, data, th, alpha, glow)
  } else {
    drawCircular(ctx, w, h, data, th, alpha, glow)
  }

  rafId = requestAnimationFrame(drawSpectrum)
}

function drawBars(ctx, w, h, data, th, alpha, glow) {
  const count = data.length
  const totalBarW = w * 0.85
  const barW = (totalBarW / count) * 0.7
  const gap = (totalBarW / count) * 0.3
  const startX = (w - totalBarW) / 2

  for (let layer = 2; layer >= 0; layer--) {
    for (let i = 0; i < count; i++) {
      const val = data[i]
      const maxH = h * 0.85
      const barH = Math.max(3, val * maxH)
      const x = startX + i * (barW + gap)
      const hueLerp = i / count
      const hue = th.hStart + (th.hEnd - th.hStart) * hueLerp
      const layerAlpha = layer === 0 ? alpha * 0.9 : layer === 1 ? alpha * 0.35 : alpha * 0.12
      const layerOffset = layer * 6
      const layerH = barH * (1 - layer * 0.15)
      const y = h - layerOffset

      const gradient = ctx.createLinearGradient(x, y - layerH, x, y)
      gradient.addColorStop(0, `hsla(${hue}, 75%, 65%, ${layerAlpha})`)
      gradient.addColorStop(0.6, `hsla(${hue}, 65%, 50%, ${layerAlpha * 0.7})`)
      gradient.addColorStop(1, `hsla(${hue}, 55%, 35%, ${layerAlpha * 0.3})`)

      ctx.fillStyle = gradient
      ctx.beginPath()
      const radius = Math.min(4, barW / 2)
      const bx = x
      const by = y - layerH
      const bw = barW
      const bh = layerH
      if (bw > 0 && bh > 0) {
        ctx.moveTo(bx + radius, by)
        ctx.lineTo(bx + bw - radius, by)
        ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + radius)
        ctx.lineTo(bx + bw, by + bh)
        ctx.lineTo(bx, by + bh)
        ctx.lineTo(bx, by + radius)
        ctx.quadraticCurveTo(bx, by, bx + radius, by)
        ctx.closePath()
        ctx.fill()
      }

      if (layer === 0 && glow > 0 && val > 0.3) {
        ctx.shadowBlur = 12 * glow * val
        ctx.shadowColor = `hsla(${hue}, 80%, 60%, ${glow * val * 0.4})`
        ctx.fillStyle = `hsla(${hue}, 80%, 70%, ${alpha * val * 0.15})`
        ctx.fillRect(x - 2, y - layerH - 4, barW + 4, layerH + 8)
        ctx.shadowBlur = 0
      }
    }
  }
}

function drawWave(ctx, w, h, data, th, alpha, glow) {
  const count = data.length
  const points = []
  for (let i = 0; i < count; i++) {
    const x = (i / (count - 1)) * w
    const val = data[i]
    const y = h * 0.5 - val * h * 0.4
    points.push({ x, y, val })
  }

  for (let layer = 2; layer >= 0; layer--) {
    const layerAlpha = layer === 0 ? alpha * 0.8 : layer === 1 ? alpha * 0.25 : alpha * 0.08
    const layerOffset = layer * 10

    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y + layerOffset)
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1]
      const curr = points[i]
      const cpx = (prev.x + curr.x) / 2
      ctx.quadraticCurveTo(prev.x, prev.y + layerOffset, cpx, (prev.y + curr.y) / 2 + layerOffset)
    }
    ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y + layerOffset)
    ctx.lineTo(w, h + 20)
    ctx.lineTo(0, h + 20)
    ctx.closePath()

    const gradient = ctx.createLinearGradient(0, 0, 0, h)
    const hueMid = (th.hStart + th.hEnd) / 2
    gradient.addColorStop(0, `hsla(${th.hStart}, 70%, 60%, ${layerAlpha})`)
    gradient.addColorStop(0.5, `hsla(${hueMid}, 60%, 50%, ${layerAlpha * 0.6})`)
    gradient.addColorStop(1, `hsla(${th.hEnd}, 50%, 35%, ${layerAlpha * 0.2})`)
    ctx.fillStyle = gradient
    ctx.fill()

    if (layer === 0) {
      ctx.beginPath()
      ctx.moveTo(points[0].x, points[0].y)
      for (let i = 1; i < points.length; i++) {
        const prev = points[i - 1]
        const curr = points[i]
        const cpx = (prev.x + curr.x) / 2
        ctx.quadraticCurveTo(prev.x, prev.y, cpx, (prev.y + curr.y) / 2)
      }

      if (glow > 0) {
        ctx.shadowBlur = 20 * glow
        ctx.shadowColor = `hsla(${hueMid}, 80%, 60%, ${glow * 0.5})`
      }
      ctx.strokeStyle = `hsla(${hueMid}, 80%, 65%, ${alpha * 0.6})`
      ctx.lineWidth = 2
      ctx.stroke()
      ctx.shadowBlur = 0
    }
  }
}

function drawCircular(ctx, w, h, data, th, alpha, glow) {
  const cx = w / 2
  const cy = h / 2
  const baseR = Math.min(w, h) * 0.28
  const count = data.length

  for (let layer = 2; layer >= 0; layer--) {
    const layerAlpha = layer === 0 ? alpha * 0.85 : layer === 1 ? alpha * 0.25 : alpha * 0.08
    const layerR = baseR - layer * 8

    ctx.beginPath()
    ctx.arc(cx, cy, layerR, 0, Math.PI * 2)
    ctx.strokeStyle = `rgba(255, 255, 255, ${layerAlpha * 0.08})`
    ctx.lineWidth = 1
    ctx.stroke()

    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2 - Math.PI / 2
      const val = data[i]
      const maxLen = baseR * 0.9
      const len = Math.max(2, val * maxLen)

      const x1 = cx + Math.cos(angle) * layerR
      const y1 = cy + Math.sin(angle) * layerR
      const x2 = cx + Math.cos(angle) * (layerR + len)
      const y2 = cy + Math.sin(angle) * (layerR + len)

      const hueLerp = i / count
      const hue = th.hStart + (th.hEnd - th.hStart) * hueLerp

      if (layer === 0) {
        const gradient = ctx.createLinearGradient(x1, y1, x2, y2)
        gradient.addColorStop(0, `hsla(${hue}, 65%, 55%, ${layerAlpha * 0.3})`)
        gradient.addColorStop(1, `hsla(${hue}, 80%, 65%, ${layerAlpha})`)
        ctx.strokeStyle = gradient
        if (glow > 0 && val > 0.3) {
          ctx.shadowBlur = 8 * glow * val
          ctx.shadowColor = `hsla(${hue}, 80%, 60%, ${glow * val * 0.5})`
        }
      } else {
        ctx.strokeStyle = `hsla(${hue}, 60%, 50%, ${layerAlpha})`
      }

      ctx.lineWidth = layer === 0 ? 2.5 : 1.5
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.stroke()
      ctx.shadowBlur = 0
    }
  }

  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2
    const val = data[i]
    if (val < 0.25) continue
    const tipR = baseR + val * baseR * 0.9
    const tx = cx + Math.cos(angle) * tipR
    const ty = cy + Math.sin(angle) * tipR
    const hueLerp = i / count
    const hue = th.hStart + (th.hEnd - th.hStart) * hueLerp

    const dotGrad = ctx.createRadialGradient(tx, ty, 0, tx, ty, 3 + val * 3)
    dotGrad.addColorStop(0, `hsla(${hue}, 80%, 70%, ${alpha * val * 0.7})`)
    dotGrad.addColorStop(1, `hsla(${hue}, 80%, 60%, 0)`)
    ctx.fillStyle = dotGrad
    ctx.beginPath()
    ctx.arc(tx, ty, 3 + val * 3, 0, Math.PI * 2)
    ctx.fill()
  }
}

function onVisibilityChange() {
  if (document.hidden) {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null }
  } else if (props.visible) {
    rafId = requestAnimationFrame(drawSpectrum)
  }
}

function close() {
  running.value = false
  settingsOpen.value = false
  if (timerId) { clearInterval(timerId); timerId = null }
  if (rafId) { cancelAnimationFrame(rafId); rafId = null }
  emit('close')
}

watch(() => props.visible, (v) => {
  if (v) {
    settingsOpen.value = false
    showEditor.value = false
    nextTick(() => {
      resizeCanvas()
      overlayRef.value?.focus()
      rafId = requestAnimationFrame(drawSpectrum)
    })
  } else {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null }
  }
})

watch(musicActive, (v) => {
  if (v && !rafId) rafId = requestAnimationFrame(drawSpectrum)
})

watch(visStyle, () => {
  nextTick(resizeCanvas)
})

document.addEventListener('visibilitychange', onVisibilityChange)

onBeforeUnmount(() => {
  if (timerId) clearInterval(timerId)
  if (rafId) cancelAnimationFrame(rafId)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.focus-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
  overflow: hidden;
}

.focus-glass-bg {
  position: absolute;
  inset: 0;
  background: rgba(18, 18, 18, 0.6);
  backdrop-filter: blur(8px) saturate(1.2);
  -webkit-backdrop-filter: blur(8px) saturate(1.2);
  opacity: v-bind('glassOpacity');
  transition: opacity 300ms cubic-bezier(0.22, 1, 0.36, 1);
}
.focus-glass-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 30% 20%, rgba(232, 146, 124, 0.04), transparent),
    radial-gradient(ellipse 60% 50% at 70% 80%, rgba(168, 197, 143, 0.03), transparent);
  pointer-events: none;
}

.focus-dark-overlay {
  position: absolute;
  inset: 0;
  background: #000000;
  opacity: v-bind('overlayOpacity');
  transition: opacity 300ms cubic-bezier(0.22, 1, 0.36, 1);
  pointer-events: none;
}

.liquid-btn {
  border: 0.5px solid rgba(255, 255, 255, 0.18);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.15),
    inset 0 -0.5px 0 rgba(255, 255, 255, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.2),
    0 0 0 0.5px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}
.liquid-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.03) 40%, transparent 100%);
  pointer-events: none;
}
.liquid-btn:hover {
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.22),
    inset 0 -0.5px 0 rgba(255, 255, 255, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.25),
    0 0 0 0.5px rgba(0, 0, 0, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
}
.liquid-btn:active {
  box-shadow:
    inset 0 1px 2px rgba(0, 0, 0, 0.15),
    0 0 0 0.5px rgba(0, 0, 0, 0.08);
  transform: scale(0.97);
}

.focus-close {
  position: absolute;
  top: 20px;
  right: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.65);
  background: rgba(255, 255, 255, 0.14);
  transition: all 0.2s;
  z-index: 20;
}
.focus-close:hover { color: rgba(255, 255, 255, 0.95); transform: scale(1.08); }
.focus-close svg { width: 22px; height: 22px; }

.focus-settings-trigger {
  position: absolute;
  top: 20px;
  left: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.65);
  background: rgba(255, 255, 255, 0.14);
  transition: all 0.25s;
  z-index: 20;
}
.focus-settings-trigger:hover,
.focus-settings-trigger.active { color: rgba(255, 255, 255, 0.95); }
.focus-settings-trigger.active { transform: rotate(90deg); }
.focus-settings-trigger svg { width: 22px; height: 22px; }

.focus-settings-panel {
  position: absolute;
  top: 74px;
  left: 24px;
  width: 280px;
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 0.5px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.12),
    0 8px 32px rgba(0, 0, 0, 0.25),
    0 0 0 0.5px rgba(0, 0, 0, 0.06);
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.focus-settings-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  border-radius: 16px 16px 0 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 100%);
  pointer-events: none;
}

.settings-slide-enter-active { transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1); }
.settings-slide-leave-active { transition: all 0.2s ease; }
.settings-slide-enter-from { opacity: 0; transform: translateY(-10px) scale(0.96); }
.settings-slide-leave-to { opacity: 0; transform: translateY(-6px); }

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.setting-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.setting-slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.12);
  outline: none;
}
.setting-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  border: none;
  box-shadow:
    0 1px 4px rgba(0, 0, 0, 0.3),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.5);
  transition: transform 0.15s;
}
.setting-slider::-webkit-slider-thumb:hover { transform: scale(1.25); }
.setting-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  border: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.setting-val {
  font-family: 'SF Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  min-width: 36px;
  text-align: right;
}

.brightness-indicator {
  display: flex;
  justify-content: space-between;
  padding: 0 2px;
}
.brightness-label-dim,
.brightness-label-frost {
  font-family: 'SF Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
}

.style-chips {
  display: flex;
  gap: 6px;
}

.style-chip {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  border: 0.5px solid rgba(255, 255, 255, 0.12);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.1),
    0 1px 2px rgba(0, 0, 0, 0.12);
  color: rgba(255, 255, 255, 0.55);
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'SF Mono', monospace;
  position: relative;
  overflow: hidden;
}
.style-chip::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
  pointer-events: none;
}
.style-chip svg { width: 16px; height: 16px; position: relative; z-index: 1; }
.style-chip:hover { border-color: rgba(255, 255, 255, 0.22); color: rgba(255, 255, 255, 0.8); background: rgba(255, 255, 255, 0.16); }
.style-chip.active {
  background: rgba(232, 146, 124, 0.12);
  border-color: rgba(232, 146, 124, 0.35);
  color: rgba(232, 146, 124, 0.95);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.08),
    0 0 12px rgba(232, 146, 124, 0.1);
}

.theme-dots {
  display: flex;
  gap: 10px;
}

.theme-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: inset 0 0.5px 0 rgba(255, 255, 255, 0.2), 0 1px 3px rgba(0, 0, 0, 0.2);
}
.theme-dot:hover { transform: scale(1.15); border-color: rgba(255, 255, 255, 0.3); }
.theme-dot.active {
  border-color: rgba(255, 255, 255, 0.7);
  box-shadow: inset 0 0.5px 0 rgba(255, 255, 255, 0.3), 0 0 10px rgba(255, 255, 255, 0.15);
}

.focus-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
  z-index: 5;
  padding: 0 24px;
}

.focus-timer-wrap { cursor: pointer; user-select: none; }

.focus-timer-display { text-align: center; }

.timer-digits {
  font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 15vw;
  font-weight: 300;
  line-height: 1;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.04em;
  text-shadow: 0 0 100px rgba(255, 255, 255, 0.08);
}
.focus-timer-wrap:hover .timer-digits { opacity: 0.75; }

.timer-edit-hint {
  display: block;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.2);
  margin-top: 8px;
  transition: color 0.2s;
}
.focus-timer-wrap:hover .timer-edit-hint { color: rgba(255, 255, 255, 0.4); }

.focus-timer-editor { animation: scaleIn 0.3s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

.editor-row { display: flex; align-items: center; justify-content: center; gap: 8px; }
.editor-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }

.spin-btn {
  background: rgba(255, 255, 255, 0.14);
  border: 0.5px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 14px;
  cursor: pointer;
  padding: 6px 14px;
  transition: all 0.15s;
  box-shadow: inset 0 0.5px 0 rgba(255, 255, 255, 0.08);
  position: relative;
  overflow: hidden;
}
.spin-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06) 0%, transparent 100%);
  pointer-events: none;
}
.spin-btn:hover { color: rgba(255, 255, 255, 0.9); transform: scale(1.1); }
.spin-btn:active { transform: scale(0.93); }

.editor-input {
  width: 80px;
  height: 64px;
  background: rgba(255, 255, 255, 0.14);
  border: 0.5px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 42px;
  font-weight: 300;
  text-align: center;
  outline: none;
  -moz-appearance: textfield;
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.1),
    0 2px 6px rgba(0, 0, 0, 0.15);
}
.editor-input::-webkit-inner-spin-button,
.editor-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.editor-input:focus {
  border-color: rgba(232, 146, 124, 0.4);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.1),
    0 0 0 3px rgba(232, 146, 124, 0.12),
    0 2px 6px rgba(0, 0, 0, 0.15);
}

.editor-label { font-size: 11px; color: rgba(255, 255, 255, 0.35); text-transform: uppercase; letter-spacing: 0.1em; }
.editor-sep { font-size: 42px; font-weight: 300; color: rgba(255, 255, 255, 0.25); padding-bottom: 20px; }

.editor-actions { display: flex; justify-content: center; gap: 12px; margin-top: 20px; }

.editor-btn {
  padding: 10px 30px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.14);
  border: 0.5px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.12),
    0 1px 3px rgba(0, 0, 0, 0.18);
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'SF Mono', monospace;
  position: relative;
  overflow: hidden;
}
.editor-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}
.editor-btn.confirm {
  background: rgba(232, 146, 124, 0.15);
  border-color: rgba(232, 146, 124, 0.3);
  color: rgba(232, 146, 124, 0.95);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.08),
    0 0 12px rgba(232, 146, 124, 0.08),
    0 1px 3px rgba(0, 0, 0, 0.18);
}
.editor-btn:hover { color: rgba(255, 255, 255, 0.9); transform: translateY(-1px); }
.editor-btn:active { transform: scale(0.97); }

.focus-mode-label { display: flex; gap: 8px; }

.mode-chip {
  padding: 7px 18px;
  border-radius: 24px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.14);
  border: 0.5px solid rgba(255, 255, 255, 0.12);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.1),
    0 1px 2px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  font-family: 'SF Mono', monospace;
  position: relative;
  overflow: hidden;
}
.mode-chip::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
  pointer-events: none;
}
.mode-chip:hover { border-color: rgba(255, 255, 255, 0.22); color: rgba(255, 255, 255, 0.8); }
.mode-chip.active {
  background: rgba(232, 146, 124, 0.12);
  border-color: rgba(232, 146, 124, 0.3);
  color: rgba(232, 146, 124, 0.95);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.06),
    0 0 10px rgba(232, 146, 124, 0.08);
}

.spectrum-wrap {
  width: 65vw;
  max-width: 900px;
  height: 140px;
  margin-top: 24px;
  position: relative;
}
.spectrum-wrap.circular {
  width: 50vw;
  max-width: 600px;
  height: 300px;
}
.focus-spectrum {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}

.focus-actions { display: flex; gap: 16px; margin-top: 8px; }

.focus-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.14);
  border: 0.5px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.12),
    inset 0 -0.5px 0 rgba(255, 255, 255, 0.04),
    0 2px 6px rgba(0, 0, 0, 0.18),
    0 0 0 0.5px rgba(0, 0, 0, 0.06);
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
  min-width: 120px;
  justify-content: center;
  font-family: 'SF Mono', monospace;
  position: relative;
  overflow: hidden;
}
.focus-action-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 40%, transparent 100%);
  pointer-events: none;
}
.focus-action-btn svg { width: 18px; height: 18px; position: relative; z-index: 1; }
.focus-action-btn span { position: relative; z-index: 1; }
.focus-action-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.18),
    inset 0 -0.5px 0 rgba(255, 255, 255, 0.06),
    0 4px 12px rgba(0, 0, 0, 0.22),
    0 0 0 0.5px rgba(0, 0, 0, 0.08);
  border-color: rgba(255, 255, 255, 0.22);
}
.focus-action-btn:active { transform: scale(0.97); }
.focus-action-btn.running {
  background: rgba(232, 146, 124, 0.1);
  border-color: rgba(232, 146, 124, 0.25);
  color: rgba(232, 146, 124, 0.95);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.06),
    0 0 16px rgba(232, 146, 124, 0.08),
    0 2px 6px rgba(0, 0, 0, 0.18);
}
.focus-action-btn.active {
  background: rgba(168, 197, 143, 0.1);
  border-color: rgba(168, 197, 143, 0.25);
  color: rgba(168, 197, 143, 0.95);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.06),
    0 0 16px rgba(168, 197, 143, 0.08),
    0 2px 6px rgba(0, 0, 0, 0.18);
}

.focus-overlay-enter-active { transition: opacity 0.35s cubic-bezier(0.22, 1, 0.36, 1); }
.focus-overlay-leave-active { transition: opacity 0.25s ease; }
.focus-overlay-enter-from, .focus-overlay-leave-to { opacity: 0; }

.timer-switch-enter-active { transition: opacity 0.25s cubic-bezier(0.22, 1, 0.36, 1), transform 0.25s cubic-bezier(0.22, 1, 0.36, 1); }
.timer-switch-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.timer-switch-enter-from { opacity: 0; transform: scale(0.97); }
.timer-switch-leave-to { opacity: 0; transform: scale(1.02); }

@media (max-width: 768px) {
  .timer-digits { font-size: 20vw; }
  .editor-input { width: 60px; height: 48px; font-size: 28px; }
  .editor-sep { font-size: 28px; }
  .spectrum-wrap { width: 90vw; height: 100px; }
  .spectrum-wrap.circular { width: 80vw; height: 250px; }
  .focus-actions { flex-direction: column; align-items: center; }
  .focus-settings-panel { width: 240px; left: 12px; }
}
</style>
