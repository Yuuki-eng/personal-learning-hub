<template>
  <div class="lyrics-panel" :class="{ 'lyrics-expanded': expanded }">
    <div class="lyrics-header">
      <button class="lyrics-mode-btn" @click="mode = mode === 'scroll' ? 'list' : 'scroll'" :title="mode === 'scroll' ? 'Switch to list view' : 'Switch to auto-scroll'">
        <span v-if="mode === 'scroll'">📜</span>
        <span v-else>📋</span>
      </button>
      <button class="lyrics-expand-btn" @click="expanded = !expanded">
        {{ expanded ? '▼' : '▲' }}
      </button>
    </div>
    <div class="lyrics-container" ref="lyricsContainer">
      <div v-if="!lyrics.length" class="lyrics-empty">
        {{ noLyricsText }}
      </div>
      <template v-else>
        <div
          v-for="(line, i) in lyrics"
          :key="i"
          class="lyrics-line"
          :class="{
            'lyrics-active': i === currentLyricIndex,
            'lyrics-past': i < currentLyricIndex,
          }"
          :ref="el => { if (i === currentLyricIndex) activeLineEl = el }"
          @click="seekToLyric(line.time)"
        >
          {{ line.text }}
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { usePlayerStore } from '../stores/player'
import { useLocaleStore } from '../stores/locale'

const player = usePlayerStore()
const localeStore = useLocaleStore()
const t = localeStore.t

const lyricsContainer = ref(null)
const activeLineEl = ref(null)
const mode = ref('scroll')
const expanded = ref(false)

const noLyricsText = computed(() => t('music.noLyrics') || 'No lyrics available')

const lyrics = computed(() => player.lyrics)
const currentLyricIndex = computed(() => player.currentLyricIndex)

watch(currentLyricIndex, async () => {
  if (mode.value !== 'scroll') return
  await nextTick()
  if (activeLineEl.value && lyricsContainer.value) {
    activeLineEl.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    })
  }
})

function seekToLyric(time) {
  const el = player.audioElement
  if (el) {
    el.currentTime = time
  }
}
</script>

<style scoped>
.lyrics-panel {
  position: relative;
  height: 120px;
  overflow: hidden;
  transition: height 0.3s ease;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid var(--color-ink-100);
}

.lyrics-expanded {
  height: 280px;
}

.lyrics-header {
  position: absolute;
  top: 4px;
  right: 8px;
  z-index: 2;
  display: flex;
  gap: 4px;
}

.lyrics-mode-btn,
.lyrics-expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 6px;
  opacity: 0.5;
  transition: opacity 0.2s;
  color: var(--color-ink-500);
}

.lyrics-mode-btn:hover,
.lyrics-expand-btn:hover {
  opacity: 1;
}

.lyrics-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px 12px;
  scroll-behavior: smooth;
  mask-image: linear-gradient(
    to bottom,
    transparent 0%,
    black 15%,
    black 85%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0%,
    black 15%,
    black 85%,
    transparent 100%
  );
}

.lyrics-container::-webkit-scrollbar {
  width: 3px;
}

.lyrics-container::-webkit-scrollbar-track {
  background: transparent;
}

.lyrics-container::-webkit-scrollbar-thumb {
  background: var(--color-ink-200);
  border-radius: 3px;
}

.lyrics-empty {
  text-align: center;
  color: var(--color-ink-300);
  font-size: 13px;
  padding-top: 30px;
  font-family: 'Courier New', monospace;
}

.lyrics-line {
  text-align: center;
  padding: 5px 8px;
  font-size: 13px;
  color: var(--color-ink-400);
  cursor: pointer;
  transition: all 0.3s ease;
  line-height: 1.6;
  border-radius: 6px;
}

.lyrics-line:hover {
  background: var(--color-ink-50);
  color: var(--color-ink-600);
}

.lyrics-active {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-warm-600);
  transform: scale(1.02);
}

.lyrics-past {
  color: var(--color-ink-300);
  opacity: 0.6;
}
</style>
