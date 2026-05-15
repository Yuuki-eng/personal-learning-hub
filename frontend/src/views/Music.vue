<template>
  <div class="music-page page-enter">
    <div v-animate="'fade-up'" class="music-top">
      <div>
        <h1 class="page-title">Music</h1>
        <p class="page-desc">Search and play music from Netease Cloud</p>
      </div>
    </div>

    <div v-animate="{ name: 'fade-up', delay: 80 }" class="search-section">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input v-model="keyword" type="text" class="search-input" placeholder="Search songs, artists..."
          @keyup.enter="doSearch" />
        <button class="search-btn" @click="doSearch" :disabled="!keyword.trim()">Search</button>
      </div>

      <div v-if="hotSearches.length" class="hot-tags">
        <span class="hot-label">Trending:</span>
        <button v-for="h in hotSearches.slice(0, 8)" :key="h.first" class="hot-tag" @click="keyword = h.first; doSearch()">
          {{ h.first }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Searching...</div>

    <div v-if="results.length > 0" class="results-section">
      <div class="results-header">
        <span class="results-count">{{ results.length }} results</span>
        <button class="btn-secondary small" @click="playAll">Play All</button>
      </div>

      <div class="song-list">
        <div v-for="(song, idx) in results" :key="song.id" class="song-item"
          :class="{ active: player.currentSong?.id === song.id }"
          @dblclick="playSong(song)">
          <div class="song-idx">{{ idx + 1 }}</div>
          <div class="song-info">
            <div class="song-name">{{ song.name }}</div>
            <div class="song-artist">{{ song.artists?.map(a => a.name).join(', ') || 'Unknown' }}</div>
          </div>
          <div class="song-album">{{ song.album?.name || '' }}</div>
          <div class="song-duration">{{ formatDuration(song.duration) }}</div>
          <div class="song-actions">
            <button class="play-btn-small" @click="playSong(song)">
              <svg v-if="player.currentSong?.id === song.id && player.isPlaying" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </button>
            <button class="add-btn-small" @click="player.addToPlaylist(formatSong(song))" title="Add to playlist">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M12 5v14M5 12h14"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && searched && results.length === 0" class="empty-state">
      <p>No results found</p>
    </div>

    <div v-if="!searched && results.length === 0" class="welcome-section">
      <div class="welcome-visual">
        <svg viewBox="0 0 80 80" fill="none">
          <circle cx="40" cy="40" r="36" stroke="var(--color-warm-200)" stroke-width="1.5"/>
          <circle cx="40" cy="40" r="12" fill="var(--color-warm-100)" stroke="var(--color-warm-300)" stroke-width="1"/>
          <circle cx="40" cy="40" r="3" fill="var(--color-warm-400)"/>
          <path d="M40 4C40 4 52 20 52 40S40 76 40 76" stroke="var(--color-warm-200)" stroke-width="0.8" opacity="0.5"/>
          <path d="M40 4C40 4 28 20 28 40S40 76 40 76" stroke="var(--color-warm-200)" stroke-width="0.8" opacity="0.5"/>
        </svg>
      </div>
      <h3>Discover Music</h3>
      <p>Search for your favorite songs and start listening</p>
      <p class="note">Note: Requires NeteaseCloudMusicApi service running on port 3000</p>
    </div>

    <div v-if="player.playlist.length > 0" class="playlist-section">
      <div class="playlist-header">
        <h3>Playlist ({{ player.playlist.length }})</h3>
        <div class="playlist-controls">
          <button class="ctrl-btn-sm" :class="{ active: player.shuffle }" @click="player.toggleShuffle()" title="Shuffle">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/>
              <polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/>
              <line x1="4" y1="4" x2="9" y2="9"/>
            </svg>
          </button>
          <button class="ctrl-btn-sm" @click="player.cycleRepeat()" :title="'Repeat: ' + player.repeat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/>
              <polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/>
            </svg>
            <span v-if="player.repeat !== 'off'" class="repeat-badge">{{ player.repeat === 'one' ? '1' : 'A' }}</span>
          </button>
        </div>
      </div>
      <div class="playlist-items">
        <div v-for="(s, i) in player.playlist" :key="s.id" class="playlist-item"
          :class="{ active: player.currentIndex === i }" @click="player.currentIndex = i; player.isPlaying = true">
          <span class="pl-idx">{{ i + 1 }}</span>
          <span class="pl-name">{{ s.name }}</span>
          <span class="pl-artist">{{ s.artist }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { searchMusic, getHotSearch, getRecommend } from '../api/music'
import { usePlayerStore } from '../stores/player'

const player = usePlayerStore()
const keyword = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const hotSearches = ref([])

function formatSong(song) {
  return {
    id: song.id,
    name: song.name,
    artist: song.artists?.map(a => a.name).join(', ') || 'Unknown',
    album: song.album?.name || '',
    duration: song.duration,
  }
}

function formatDuration(ms) {
  if (!ms) return ''
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${String(sec).padStart(2, '0')}`
}

async function doSearch() {
  if (!keyword.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const data = await searchMusic(keyword.value)
    results.value = data?.result?.songs || []
  } catch {
    results.value = []
  }
  loading.value = false
}

function playSong(song) {
  player.playSong(formatSong(song))
}

function playAll() {
  const songs = results.value.map(formatSong)
  player.setPlaylist(songs, 0)
  player.isPlaying = true
}

onMounted(async () => {
  try {
    const data = await getHotSearch()
    hotSearches.value = data?.result?.hots || []
  } catch {}
})
</script>

<style scoped>
.music-page { max-width: 900px; }

.music-top { margin-bottom: 28px; }
.page-title { font-size: 28px; font-weight: 700; color: var(--color-ink-900); letter-spacing: -0.02em; }
.page-desc { color: var(--color-ink-400); font-size: 14px; margin-top: 4px; }

.search-section { margin-bottom: 28px; }

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-200);
  border-radius: 14px;
  padding: 6px 8px 6px 16px;
  transition: border-color 0.2s;
}

.search-box:focus-within { border-color: var(--color-warm-400); }

.search-icon { width: 18px; height: 18px; color: var(--color-ink-300); flex-shrink: 0; }

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--color-ink-800);
  background: transparent;
  padding: 8px 0;
}

.search-input::placeholder { color: var(--color-ink-300); }

.search-btn {
  padding: 8px 18px;
  background: var(--color-ink-800);
  color: var(--color-surface-elevated);
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover { background: var(--color-ink-900); }
.search-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.hot-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.hot-label { font-size: 12px; color: var(--color-ink-400); }

.hot-tag {
  padding: 3px 10px;
  border: 1px solid var(--color-ink-200);
  border-radius: 8px;
  background: transparent;
  font-size: 12px;
  color: var(--color-ink-500);
  cursor: pointer;
  transition: all 0.2s;
}

.hot-tag:hover { background: var(--color-warm-50); border-color: var(--color-warm-300); color: var(--color-warm-700); }

.loading-state { text-align: center; padding: 40px; color: var(--color-ink-400); }

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.results-count { font-size: 13px; color: var(--color-ink-400); }

.btn-secondary.small { padding: 6px 12px; font-size: 12px; }

.song-list { display: flex; flex-direction: column; }

.song-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
}

.song-item:hover { background: var(--color-ink-50); }

.song-item.active { background: var(--color-warm-50); }

.song-item.active .song-name { color: var(--color-warm-600); }

.song-idx {
  width: 28px;
  font-size: 13px;
  color: var(--color-ink-300);
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.song-item.active .song-idx { color: var(--color-warm-500); }

.song-info { flex: 1; min-width: 0; }

.song-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-artist {
  font-size: 12px;
  color: var(--color-ink-400);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-album {
  font-size: 12px;
  color: var(--color-ink-400);
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-duration {
  font-size: 12px;
  color: var(--color-ink-300);
  font-variant-numeric: tabular-nums;
  min-width: 40px;
  text-align: right;
}

.song-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.song-item:hover .song-actions { opacity: 1; }

.play-btn-small, .add-btn-small {
  width: 28px; height: 28px;
  border: none; background: transparent; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--color-ink-500); transition: all 0.2s;
}

.play-btn-small:hover { background: var(--color-warm-100); color: var(--color-warm-600); }
.add-btn-small:hover { background: var(--color-ink-100); color: var(--color-ink-700); }
.play-btn-small svg, .add-btn-small svg { width: 16px; height: 16px; }

.empty-state { text-align: center; padding: 40px; color: var(--color-ink-400); }

.welcome-section {
  text-align: center;
  padding: 60px 20px;
}

.welcome-visual { width: 80px; height: 80px; margin: 0 auto 20px; }

.welcome-section h3 { font-size: 18px; color: var(--color-ink-700); margin-bottom: 6px; }
.welcome-section p { font-size: 14px; color: var(--color-ink-400); }
.welcome-section .note { font-size: 12px; color: var(--color-ink-300); margin-top: 12px; }

.playlist-section {
  margin-top: 32px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 14px;
  padding: 16px;
}

.playlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.playlist-header h3 { font-size: 14px; font-weight: 600; color: var(--color-ink-700); }

.playlist-controls { display: flex; gap: 4px; }

.ctrl-btn-sm {
  width: 28px; height: 28px; border: none; background: transparent;
  border-radius: 7px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--color-ink-400); transition: all 0.2s; position: relative;
}
.ctrl-btn-sm:hover { background: var(--color-ink-50); color: var(--color-ink-600); }
.ctrl-btn-sm.active { color: var(--color-warm-500); }
.ctrl-btn-sm svg { width: 15px; height: 15px; }

.repeat-badge {
  position: absolute; top: -2px; right: -2px;
  font-size: 8px; font-weight: 700;
  background: var(--color-warm-500); color: white;
  width: 12px; height: 12px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}

.playlist-items { display: flex; flex-direction: column; max-height: 300px; overflow-y: auto; }

.playlist-item {
  display: flex; align-items: center; gap: 10px;
  padding: 7px 10px; border-radius: 8px; cursor: pointer; transition: background 0.15s;
}
.playlist-item:hover { background: var(--color-ink-50); }
.playlist-item.active { background: var(--color-warm-50); }

.pl-idx { font-size: 12px; color: var(--color-ink-300); width: 20px; text-align: center; }
.pl-name { font-size: 13px; color: var(--color-ink-700); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pl-artist { font-size: 12px; color: var(--color-ink-400); }
</style>
