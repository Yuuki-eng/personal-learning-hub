<template>
  <div class="visualizer-container">
    <canvas ref="canvasRef" class="visualizer-canvas"></canvas>
    <div class="visualizer-controls">
      <button v-for="mode in modes" :key="mode.value"
        class="mode-btn" :class="{ active: currentMode === mode.value }"
        @click="currentMode = mode.value">
        {{ mode.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { usePlayerStore } from '../stores/player'

const player = usePlayerStore()
const canvasRef = ref(null)
const currentMode = ref('bars')
let animFrame = null

const modes = [
  { value: 'bars', label: 'Bars' },
  { value: 'wave', label: 'Wave' },
  { value: 'circle', label: 'Circle' },
]

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const analyser = player.analyser
  if (!analyser) {
    animFrame = requestAnimationFrame(draw)
    return
  }

  canvas.width = canvas.offsetWidth * 2
  canvas.height = canvas.offsetHeight * 2
  ctx.scale(2, 2)

  const w = canvas.offsetWidth
  const h = canvas.offsetHeight

  ctx.clearRect(0, 0, w, h)

  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  analyser.getByteFrequencyData(dataArray)

  if (currentMode.value === 'bars') {
    drawBars(ctx, w, h, dataArray, bufferLength)
  } else if (currentMode.value === 'wave') {
    const waveData = new Uint8Array(bufferLength)
    analyser.getByteTimeDomainData(waveData)
    drawWave(ctx, w, h, waveData, bufferLength)
  } else {
    drawCircle(ctx, w, h, dataArray, bufferLength)
  }

  animFrame = requestAnimationFrame(draw)
}

function drawBars(ctx, w, h, data, len) {
  const barCount = Math.min(len, 64)
  const barWidth = (w / barCount) * 0.7
  const gap = (w / barCount) * 0.3

  for (let i = 0; i < barCount; i++) {
    const val = data[i] / 255
    const barH = val * h * 0.85

    const gradient = ctx.createLinearGradient(0, h - barH, 0, h)
    gradient.addColorStop(0, 'rgba(200, 122, 50, 0.9)')
    gradient.addColorStop(1, 'rgba(200, 122, 50, 0.2)')

    ctx.fillStyle = gradient
    const x = i * (barWidth + gap) + gap / 2
    ctx.beginPath()
    ctx.roundRect(x, h - barH, barWidth, barH, [barWidth / 2, barWidth / 2, 0, 0])
    ctx.fill()
  }
}

function drawWave(ctx, w, h, data, len) {
  ctx.lineWidth = 2
  ctx.strokeStyle = 'rgba(200, 122, 50, 0.8)'
  ctx.beginPath()

  const sliceWidth = w / len
  let x = 0

  for (let i = 0; i < len; i++) {
    const v = data[i] / 128.0
    const y = (v * h) / 2
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
    x += sliceWidth
  }

  ctx.stroke()

  ctx.lineTo(w, h / 2)
  ctx.lineTo(0, h / 2)
  ctx.closePath()
  ctx.fillStyle = 'rgba(200, 122, 50, 0.05)'
  ctx.fill()
}

function drawCircle(ctx, w, h, data, len) {
  const cx = w / 2
  const cy = h / 2
  const radius = Math.min(w, h) * 0.3
  const barCount = Math.min(len, 64)

  for (let i = 0; i < barCount; i++) {
    const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2
    const val = data[i] / 255
    const barLen = val * radius * 0.8 + 4

    const x1 = cx + Math.cos(angle) * radius
    const y1 = cy + Math.sin(angle) * radius
    const x2 = cx + Math.cos(angle) * (radius + barLen)
    const y2 = cy + Math.sin(angle) * (radius + barLen)

    ctx.strokeStyle = `rgba(200, 122, 50, ${0.3 + val * 0.7})`
    ctx.lineWidth = 2.5
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()
  }

  ctx.beginPath()
  ctx.arc(cx, cy, radius - 2, 0, Math.PI * 2)
  ctx.strokeStyle = 'rgba(200, 122, 50, 0.15)'
  ctx.lineWidth = 1
  ctx.stroke()
}

onMounted(() => {
  animFrame = requestAnimationFrame(draw)
})

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
})
</script>

<style scoped>
.visualizer-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
}

.visualizer-canvas {
  flex: 1;
  width: 100%;
}

.visualizer-controls {
  position: absolute;
  top: 8px;
  right: 12px;
  display: flex;
  gap: 4px;
}

.mode-btn {
  padding: 3px 10px;
  font-size: 11px;
  border: 1px solid var(--color-ink-200);
  background: var(--color-surface-elevated);
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-ink-500);
  transition: all 0.2s;
}

.mode-btn:hover {
  border-color: var(--color-ink-300);
  color: var(--color-ink-700);
}

.mode-btn.active {
  background: var(--color-warm-100);
  border-color: var(--color-warm-300);
  color: var(--color-warm-700);
}
</style>
