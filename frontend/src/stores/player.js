import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getLyric } from '../api/music'

export const usePlayerStore = defineStore('player', () => {
  const playlist = ref([])
  const currentIndex = ref(-1)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const volume = ref(0.7)
  const shuffle = ref(false)
  const repeat = ref('off')
  const showVisualizer = ref(false)
  const showFullPlayer = ref(false)
  const audioElement = ref(null)
  const audioContext = ref(null)
  const analyser = ref(null)
  const sourceNode = ref(null)
  const lyrics = ref([])
  const currentLyricIndex = ref(-1)

  const currentSong = computed(() => {
    if (currentIndex.value >= 0 && currentIndex.value < playlist.value.length) {
      return playlist.value[currentIndex.value]
    }
    return null
  })

  function setPlaylist(songs, startIndex = 0) {
    playlist.value = songs
    currentIndex.value = startIndex
    isPlaying.value = false
  }

  function addToPlaylist(song) {
    const exists = playlist.value.findIndex(s => s.id === song.id)
    if (exists === -1) {
      playlist.value.push(song)
    }
  }

  function playSong(song) {
    const idx = playlist.value.findIndex(s => s.id === song.id)
    if (idx !== -1) {
      currentIndex.value = idx
    } else {
      playlist.value.push(song)
      currentIndex.value = playlist.value.length - 1
    }
    isPlaying.value = true
  }

  function nextSong() {
    if (playlist.value.length === 0) return
    if (shuffle.value) {
      currentIndex.value = Math.floor(Math.random() * playlist.value.length)
    } else {
      currentIndex.value = (currentIndex.value + 1) % playlist.value.length
    }
    isPlaying.value = true
  }

  function prevSong() {
    if (playlist.value.length === 0) return
    currentIndex.value = (currentIndex.value - 1 + playlist.value.length) % playlist.value.length
    isPlaying.value = true
  }

  function togglePlay() {
    isPlaying.value = !isPlaying.value
  }

  function toggleShuffle() {
    shuffle.value = !shuffle.value
  }

  function toggleRepeat() {
    const modes = ['off', 'all', 'one']
    repeat.value = modes[(modes.indexOf(repeat.value) + 1) % modes.length]
  }

  function initAudioContext() {
    if (audioContext.value) return
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    audioContext.value = new AudioCtx()
    analyser.value = audioContext.value.createAnalyser()
    analyser.value.fftSize = 256
    analyser.value.smoothingTimeConstant = 0.8
  }

  function connectAudioSource(audioEl) {
    if (!audioContext.value) initAudioContext()
    if (sourceNode.value) {
      try { sourceNode.value.disconnect() } catch {}
    }
    sourceNode.value = audioContext.value.createMediaElementSource(audioEl)
    sourceNode.value.connect(analyser.value)
    analyser.value.connect(audioContext.value.destination)
  }

  function parseLrc(lrcStr) {
    if (!lrcStr) return []
    const lines = lrcStr.split('\n')
    const result = []
    const timeReg = /\[(\d{2}):(\d{2})\.(\d{2,3})\]/
    for (const line of lines) {
      const match = timeReg.exec(line)
      if (match) {
        const min = parseInt(match[1])
        const sec = parseInt(match[2])
        const ms = parseInt(match[3].padEnd(3, '0'))
        const time = min * 60 + sec + ms / 1000
        const text = line.replace(/\[\d{2}:\d{2}\.\d{2,3}\]/, '').trim()
        if (text) {
          result.push({ time, text })
        }
      }
    }
    return result
  }

  async function fetchLyrics() {
    const song = currentSong.value
    if (!song) { lyrics.value = []; currentLyricIndex.value = -1; return }
    try {
      const data = await getLyric(song.id)
      lyrics.value = parseLrc(data?.lrc?.lyric || '')
      currentLyricIndex.value = -1
    } catch {
      lyrics.value = []
      currentLyricIndex.value = -1
    }
  }

  function updateLyricIndex(time) {
    if (lyrics.value.length === 0) return
    let idx = -1
    for (let i = lyrics.value.length - 1; i >= 0; i--) {
      if (time >= lyrics.value[i].time) {
        idx = i
        break
      }
    }
    currentLyricIndex.value = idx
  }

  return {
    playlist, currentIndex, isPlaying, currentTime, duration,
    volume, shuffle, repeat, showVisualizer, showFullPlayer,
    audioElement, audioContext, analyser, sourceNode,
    lyrics, currentLyricIndex,
    currentSong,
    setPlaylist, addToPlaylist, playSong, nextSong, prevSong,
    togglePlay, toggleShuffle, toggleRepeat, initAudioContext, connectAudioSource,
    fetchLyrics, updateLyricIndex,
  }
})
