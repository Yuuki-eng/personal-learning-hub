<template>
  <div class="home-viz-wrapper">
    <div class="home-viz" :class="{ active: player.isPlaying }">
      <canvas ref="canvasRef" class="home-viz-canvas"></canvas>
      <div class="viz-bottom">
        <div class="viz-song-info" v-if="player.currentSong">
          <div class="viz-title">{{ player.currentSong.name }}</div>
          <div class="viz-artist">{{ player.currentSong.artist }}</div>
        </div>
        <div class="viz-song-info" v-else>
          <div class="viz-title dim">Press play to start</div>
        </div>
        <div class="viz-controls">
          <button class="viz-ctrl main" @click="playRecommended" :disabled="loading" title="Random play">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>
            </svg>
          </button>
          <button class="viz-ctrl" v-if="player.currentSong" @click="player.togglePlay()">
            <svg v-if="!player.isPlaying" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          </button>
          <button class="viz-ctrl" v-if="player.currentSong" @click="player.nextSong()">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>
        </div>
      </div>
    </div>
    <LyricsPanel v-if="player.currentSong" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { usePlayerStore } from '../stores/player'
import { searchMusic } from '../api/music'
import LyricsPanel from './LyricsPanel.vue'

const player = usePlayerStore()
const canvasRef = ref(null)
const loading = ref(false)
let animFrame = null

const SEARCH_KEYWORDS = ['lofi', 'chill', 'piano', 'acoustic', 'ambient', 'jazz', 'study']

watch(() => player.currentSong?.id, (newId) => {
  if (newId) player.fetchLyrics()
}, { immediate: true })

watch(() => player.currentTime, (time) => {
  player.updateLyricIndex(time)
})

async function playRecommended() {
  if (loading.value) return
  loading.value = true
  try {
    const kw = SEARCH_KEYWORDS[Math.floor(Math.random() * SEARCH_KEYWORDS.length)]
    const res = await searchMusic(kw, 10)
    const songs = (res?.result?.songs || []).map(s => ({
      id: s.id,
      name: s.name,
      artist: s.artists?.map(a => a.name).join(', ') || 'Unknown',
      duration: s.duration,
      album: s.album?.name || '',
    }))
    if (songs.length > 0) {
      const startIdx = Math.floor(Math.random() * songs.length)
      player.setPlaylist(songs, startIdx)
      player.isPlaying = true
    }
  } catch (e) {
    console.warn('Failed to load recommendations:', e)
  } finally {
    loading.value = false
  }
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.offsetWidth
  const h = canvas.offsetHeight
  canvas.width = w * 2
  canvas.height = h * 2
  ctx.scale(2, 2)
  ctx.clearRect(0, 0, w, h)

  const analyser = player.analyser
  if (!analyser || !player.isPlaying) {
    drawIdle(ctx, w, h)
    animFrame = requestAnimationFrame(draw)
    return
  }

  const bufLen = analyser.frequencyBinCount
  const freq = new Uint8Array(bufLen)
  const wave = new Uint8Array(bufLen)
  analyser.getByteFrequencyData(freq)
  analyser.getByteTimeDomainData(wave)

  const cx = w / 2
  const cy = h * 0.42
  const avg = freq.reduce((a, b) => a + b, 0) / bufLen / 255
  const pulseR = 35 + avg * 28

  for (let ring = 3; ring >= 0; ring--) {
    const r = pulseR + ring * 16
    const alpha = 0.05 - ring * 0.01
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(212, 148, 79, ${Math.max(0, alpha)})`
    ctx.fill()
  }

  const barCount = 40
  for (let i = 0; i < barCount; i++) {
    const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2
    const val = freq[Math.floor(i * bufLen / barCount)] / 255
    const barLen = val * 40 + 2
    const innerR = pulseR + 6
    const x1 = cx + Math.cos(angle) * innerR
    const y1 = cy + Math.sin(angle) * innerR
    const x2 = cx + Math.cos(angle) * (innerR + barLen)
    const y2 = cy + Math.sin(angle) * (innerR + barLen)
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = `rgba(200, 122, 50, ${0.15 + val * 0.5})`
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.stroke()
  }

  ctx.beginPath()
  ctx.arc(cx, cy, pulseR, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(200, 122, 50, 0.1)'
  ctx.fill()

  const waveY = h * 0.78
  const wavePoints = Math.min(bufLen, 80)
  ctx.beginPath()
  for (let i = 0; i < wavePoints; i++) {
    const x = (i / wavePoints) * w
    const v = wave[Math.floor(i * bufLen / wavePoints)] / 128.0
    const y = waveY + (v - 1) * 18
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.strokeStyle = 'rgba(212, 148, 79, 0.2)'
  ctx.lineWidth = 1.5
  ctx.stroke()

  animFrame = requestAnimationFrame(draw)
}

function drawIdle(ctx, w, h) {
  const cx = w / 2
  const cy = h * 0.42
  const t = Date.now() * 0.001

  for (let i = 0; i < 4; i++) {
    const r = 32 + i * 14 + Math.sin(t + i) * 3
    const alpha = 0.03 + Math.sin(t * 0.5 + i * 0.8) * 0.015
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(212, 148, 79, ${Math.max(0, alpha)})`
    ctx.fill()
  }

  ctx.beginPath()
  ctx.arc(cx, cy, 28, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(200, 122, 50, 0.06)'
  ctx.fill()

  const waveY = h * 0.78
  ctx.beginPath()
  for (let i = 0; i < 60; i++) {
    const x = (i / 60) * w
    const y = waveY + Math.sin(t * 0.7 + i * 0.15) * 4
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.strokeStyle = 'rgba(212, 148, 79, 0.08)'
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
.home-viz-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.home-viz {
  position: relative;
  width: 100%;
  height: 240px;
  overflow: hidden;
  background: var(--color-surface-elevated);
  transition: all 0.4s ease;
}

.home-viz.active {
  background: linear-gradient(180deg, var(--color-surface-elevated), rgba(240, 212, 176, 0.08));
}

.home-viz-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.viz-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 14px 18px;
  z-index: 1;
}

.viz-song-info {
  max-width: 60%;
}

.viz-artist {
  font-size: 10px;
  color: var(--color-ink-400);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-family: 'Courier New', monospace;
}

.viz-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-ink-800);
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.viz-title.dim {
  color: var(--color-ink-300);
  font-weight: 500;
  font-size: 13px;
}

.viz-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.viz-ctrl {
  width: 34px;
  height: 34px;
  border: 1.5px solid var(--color-ink-300);
  background: var(--color-surface-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-ink-600);
  transition: all 0.12s ease;
  box-shadow: 1px 1px 0 var(--color-ink-200);
}

.viz-ctrl.main {
  width: 38px;
  height: 38px;
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-color: var(--color-ink-800);
  box-shadow: 2px 2px 0 var(--color-ink-400);
}

.viz-ctrl:hover:not(:disabled) {
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-color: var(--color-ink-800);
  box-shadow: 2px 2px 0 var(--color-ink-400);
  transform: translate(-1px, -1px);
}

.viz-ctrl:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.viz-ctrl svg {
  width: 14px;
  height: 14px;
}

.viz-ctrl.main svg {
  width: 16px;
  height: 16px;
}
</style>
