<template>
  <div class="mini-player" v-if="player.currentSong">
    <div class="mini-player-progress">
      <div class="mini-player-progress-bar" :style="{ width: progressPercent + '%' }"></div>
    </div>
    <div class="mini-player-inner">
      <div class="mini-player-info">
        <div class="mini-player-cover" @click="player.showFullPlayer = !player.showFullPlayer">
          <span class="cover-note">♪</span>
        </div>
        <div class="mini-player-meta">
          <div class="mini-player-title">{{ player.currentSong?.name || 'Unknown' }}</div>
          <div class="mini-player-artist">{{ player.currentSong?.artist || 'Unknown' }}</div>
        </div>
      </div>

      <div class="mini-player-controls">
        <button class="ctrl-btn" @click="player.prevSong()">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/></svg>
        </button>
        <button class="ctrl-btn play-btn" @click="handlePlayPause">
          <svg v-if="!player.isPlaying" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
          </svg>
        </button>
        <button class="ctrl-btn" @click="player.nextSong()">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
        </button>
      </div>

      <div class="mini-player-right">
        <button class="ctrl-btn small" @click="player.showVisualizer = !player.showVisualizer"
          :class="{ active: player.showVisualizer }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="8" width="2" height="8"/><rect x="8" y="4" width="2" height="16"/>
            <rect x="12" y="6" width="2" height="12"/><rect x="16" y="10" width="2" height="4"/>
          </svg>
        </button>
        <div class="volume-control">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="vol-icon">
            <path d="M11 5L6 9H2v6h4l5 4V5z"/>
          </svg>
          <input type="range" min="0" max="1" step="0.01" v-model.number="player.volume" class="volume-slider" />
        </div>
        <button class="ctrl-btn small" @click="player.toggleRepeat()" :title="player.repeat">
          <svg v-if="player.repeat === 'off'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
          <svg v-else-if="player.repeat === 'all'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/><text x="10" y="15" font-size="8" fill="currentColor" stroke="none" font-weight="bold">1</text></svg>
        </button>
        <button class="ctrl-btn small" @click="player.toggleShuffle()" :class="{ active: player.shuffle }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
        </button>
      </div>
    </div>

    <audio
      ref="audioRef"
      :src="audioSrc"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoaded"
      @ended="onEnded"
      @canplay="onCanPlay"
      crossorigin="anonymous"
    ></audio>

    <transition name="slide-up">
      <div v-if="player.showVisualizer" class="visualizer-overlay">
        <AudioVisualizer />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { usePlayerStore } from '../stores/player'
import { getMusicUrl, getStreamUrl } from '../api/music'
import AudioVisualizer from './AudioVisualizer.vue'

const player = usePlayerStore()
const audioRef = ref(null)
const audioSrc = ref('')
const progressPercent = ref(0)
let audioConnected = false

watch(() => player.isPlaying, async (val) => {
  await nextTick()
  if (!audioRef.value) return
  if (val) {
    try { await audioRef.value.play() } catch {}
  } else {
    audioRef.value.pause()
  }
})

watch(() => player.volume, (val) => {
  if (audioRef.value) audioRef.value.volume = val
})

watch(() => player.currentSong, async (song) => {
  if (!song) return
  try {
    const data = await getMusicUrl(song.id)
    const rawUrl = data?.data?.[0]?.url
    if (rawUrl) {
      audioSrc.value = getStreamUrl(rawUrl)
      await nextTick()
      if (audioRef.value) {
        audioRef.value.volume = player.volume
        if (!audioConnected && audioRef.value) {
          try {
            player.initAudioContext()
            player.connectAudioSource(audioRef.value)
            audioConnected = true
          } catch {}
        }
        if (player.isPlaying) {
          try { await audioRef.value.play() } catch {}
        }
      }
    }
  } catch {}
}, { immediate: true })

function onTimeUpdate() {
  if (!audioRef.value) return
  player.currentTime = audioRef.value.currentTime
  if (player.duration > 0) {
    progressPercent.value = (audioRef.value.currentTime / player.duration) * 100
  }
}

function onLoaded() {
  if (audioRef.value) {
    player.duration = audioRef.value.duration
  }
}

function onCanPlay() {
  if (!audioConnected && audioRef.value) {
    try {
      player.initAudioContext()
      player.connectAudioSource(audioRef.value)
      audioConnected = true
    } catch {}
  }
}

function onEnded() {
  if (player.repeat === 'one') {
    audioRef.value.currentTime = 0
    audioRef.value.play()
  } else {
    player.nextSong()
  }
}

function handlePlayPause() {
  player.togglePlay()
}
</script>

<style scoped>
.mini-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  border-top: 2px solid var(--color-ink-200);
  z-index: 200;
  backdrop-filter: blur(20px) saturate(1.2);
  background: rgba(250, 248, 244, 0.94);
}

.mini-player-progress {
  height: 3px;
  background: var(--color-ink-100);
  position: absolute;
  top: -3px;
  left: 0;
  right: 0;
}

.mini-player-progress-bar {
  height: 100%;
  background: var(--color-warm-400);
  transition: width 0.3s linear;
}

.mini-player-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 24px;
  gap: 16px;
}

.mini-player-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.mini-player-cover {
  width: 36px;
  height: 36px;
  background: var(--color-ink-800);
  border: 2px solid var(--color-ink-800);
  box-shadow: 2px 2px 0 var(--color-ink-400);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
}

.cover-note {
  font-size: 16px;
  color: var(--color-warm-300);
}

.mini-player-meta {
  min-width: 0;
}

.mini-player-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-ink-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
  font-family: 'Courier New', monospace;
}

.mini-player-artist {
  font-size: 10px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
  letter-spacing: 0.04em;
}

.mini-player-controls {
  display: flex;
  align-items: center;
  gap: 2px;
}

.ctrl-btn {
  background: none;
  border: 1.5px solid transparent;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-ink-500);
  transition: all 0.12s;
}

.ctrl-btn:hover {
  color: var(--color-ink-800);
  border-color: var(--color-ink-300);
}

.ctrl-btn svg {
  width: 16px;
  height: 16px;
}

.ctrl-btn.play-btn {
  width: 36px;
  height: 36px;
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-color: var(--color-ink-800);
  box-shadow: 2px 2px 0 var(--color-ink-400);
}

.ctrl-btn.play-btn:hover {
  background: var(--color-warm-600);
  border-color: var(--color-warm-600);
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 var(--color-ink-400);
}

.ctrl-btn.play-btn svg {
  width: 18px;
  height: 18px;
}

.ctrl-btn.small {
  width: 28px;
  height: 28px;
}

.ctrl-btn.small svg {
  width: 14px;
  height: 14px;
}

.ctrl-btn.active {
  color: var(--color-warm-500);
  border-color: var(--color-warm-300);
}

.mini-player-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 6px;
}

.vol-icon {
  width: 14px;
  height: 14px;
  color: var(--color-ink-400);
}

.volume-slider {
  width: 70px;
  height: 3px;
  accent-color: var(--color-warm-400);
  cursor: pointer;
}

.visualizer-overlay {
  background: var(--color-surface-elevated);
  border-top: 2px solid var(--color-ink-200);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
