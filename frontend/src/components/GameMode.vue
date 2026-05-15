<template>
  <div class="game-scene" @keydown.esc="close" tabindex="0" ref="sceneRef">
    <canvas ref="gameCanvas" class="game-canvas"></canvas>

    <div class="game-close" @click="close">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </div>

    <div v-if="scene === 'menu'" class="game-ui game-menu">
      <h1 class="game-title">{{ t('game.title') }}</h1>
      <button class="game-start-btn" @click="showModes = true">{{ t('game.start') }}</button>
      <transition name="modes-pop">
        <div v-if="showModes" class="game-modes">
          <button class="mode-btn" @click="enterLevelSelect">
            <span class="mode-icon">🏰</span>
            <span class="mode-name">{{ t('game.levelMode') }}</span>
            <span class="mode-desc">{{ t('game.levelDesc') }}</span>
          </button>
          <button class="mode-btn" @click="enterTimeChallenge">
            <span class="mode-icon">⏱️</span>
            <span class="mode-name">{{ t('game.timeMode') }}</span>
            <span class="mode-desc">{{ t('game.timeDesc') }}</span>
          </button>
          <button class="mode-btn" @click="enterFreeMode">
            <span class="mode-icon">🌿</span>
            <span class="mode-name">{{ t('game.freeMode') }}</span>
            <span class="mode-desc">{{ t('game.freeDesc') }}</span>
          </button>
        </div>
      </transition>
    </div>

    <div v-else-if="scene === 'levels'" class="game-ui game-levels">
      <div class="levels-header">
        <button class="back-btn" @click="scene = 'menu'; showModes = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
          {{ t('common.back') }}
        </button>
        <h2 class="levels-title">{{ t('game.selectLevel') }}</h2>
      </div>
      <div class="levels-grid">
        <button
          v-for="lv in 20"
          :key="lv"
          class="level-cell"
          :class="{ locked: lv > maxUnlocked, current: lv === maxUnlocked }"
          :style="{ '--lv-hue': (lv / 20) * 120 }"
          @click="startLevel(lv)"
        >
          <span class="level-num">{{ lv }}</span>
          <span v-if="lv <= maxUnlocked" class="level-check">✓</span>
        </button>
      </div>
    </div>

    <div v-else-if="scene === 'playing' && gameMode !== 'free'" class="game-ui game-hud">
      <div class="hud-left">
        <span class="hud-label">{{ t('game.score') }}</span>
        <span class="hud-value">{{ score }}</span>
      </div>
      <div v-if="gameMode === 'level'" class="hud-center">
        <span class="hud-label">{{ t('game.level') }} {{ currentLevel }}</span>
        <span class="hud-sub">{{ captured }}/{{ getLevelTarget(currentLevel) }}</span>
      </div>
      <div v-else class="hud-center">
        <span class="hud-label">{{ t('game.target') }}</span>
        <span class="hud-sub">{{ captured }}/{{ timeTarget }}</span>
      </div>
      <div class="hud-right">
        <span class="hud-label">{{ t('game.time') }}</span>
        <span class="hud-value" :class="{ urgent: timeLeft <= 5 && timeLeft > 0 }">{{ formatTime(timeLeft) }}</span>
      </div>
    </div>

    <transition name="score-pop">
      <div v-if="scorePop" class="score-pop" :style="{ left: scorePopX + 'px', top: scorePopY + 'px' }">
        +{{ scorePopVal }}
      </div>
    </transition>

    <div v-if="scene === 'result'" class="game-ui game-result">
      <div class="result-card" :class="{ win: resultWin, lose: !resultWin }">
        <div class="result-icon">{{ resultWin ? '🎉' : '💫' }}</div>
        <h2 class="result-title">{{ resultWin ? t('game.win') : t('game.lose') }}</h2>
        <div class="result-score">
          <span class="result-score-label">{{ t('game.score') }}</span>
          <span class="result-score-value">{{ score }}</span>
        </div>
        <div v-if="gameMode === 'time' && resultWin" class="result-round">{{ t('game.round') }} {{ timeRound }}</div>
        <div class="result-actions">
          <button v-if="gameMode === 'time' && resultWin" class="result-btn primary" @click="timeContinue">{{ t('game.continue') }}</button>
          <button v-if="gameMode === 'time' && resultWin" class="result-btn" @click="close">{{ t('game.exit') }}</button>
          <button v-if="gameMode === 'time' && !resultWin" class="result-btn primary" @click="timeRestart">{{ t('game.restart') }}</button>
          <button v-if="gameMode === 'time' && !resultWin" class="result-btn" @click="close">{{ t('game.exit') }}</button>
          <button v-if="gameMode === 'level' && resultWin" class="result-btn primary" @click="nextLevel">{{ t('game.nextLevel') }}</button>
          <button v-if="gameMode === 'level'" class="result-btn" @click="scene = 'levels'">{{ t('game.backLevels') }}</button>
          <button v-if="gameMode === 'level'" class="result-btn" @click="startLevel(currentLevel)">{{ t('game.retry') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useLocaleStore } from '../stores/locale'

const emit = defineEmits(['close'])

const localeStore = useLocaleStore()
const t = localeStore.t

const sceneRef = ref(null)
const gameCanvas = ref(null)
const scene = ref('menu')
const showModes = ref(false)
const gameMode = ref('')
const currentLevel = ref(1)
const maxUnlocked = ref(parseInt(localStorage.getItem('gameMaxLevel') || '1'))
const score = ref(0)
const captured = ref(0)
const timeLeft = ref(0)
const timeTarget = ref(0)
const timeRound = ref(1)
const timeBaseScore = ref(0)
const resultWin = ref(false)
const scorePop = ref(false)
const scorePopVal = ref(0)
const scorePopX = ref(0)
const scorePopY = ref(0)

let animFrame = null
let gameTimer = null
let popTimer = null
let particles = []
let mouseX = -1000
let mouseY = -1000
let canvasW = 0
let canvasH = 0
let ambientOsc = null
let ambientGain = null
let ambientCtx = null
let initialized = false

const CAPTURE_RADIUS = 45
const ATTRACT_RADIUS = 160

function getLevelConfig(lv) {
  return {
    targets: 5 + lv * 2,
    particleCount: 30 + lv * 5,
    targetSpeed: 0.4 + lv * 0.12,
    bgSpeed: 0.2 + lv * 0.03,
    captureRadius: Math.max(25, CAPTURE_RADIUS - lv * 1.2),
    attractRadius: Math.max(80, ATTRACT_RADIUS - lv * 4),
    time: Math.max(20, 45 - lv),
  }
}

function getLevelTarget(lv) {
  return getLevelConfig(lv).targets
}

function formatTime(s) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

function initParticles(w, h, count, speed, addTarget, targetCount) {
  particles = []
  const bgColors = [[200,122,50],[120,160,110],[170,100,90],[180,160,100],[150,130,120]]
  const targetColors = [[232,146,124],[255,200,80],[168,197,143]]

  for (let i = 0; i < count; i++) {
    const c = bgColors[Math.floor(Math.random() * bgColors.length)]
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * speed * 2,
      vy: (Math.random() - 0.5) * speed * 2,
      r: 1.5 + Math.random() * 2,
      color: c,
      baseAlpha: 0.15 + Math.random() * 0.2,
      phase: Math.random() * Math.PI * 2,
      isTarget: false,
      captured: false,
      pulsePhase: Math.random() * Math.PI * 2,
    })
  }

  if (addTarget && targetCount) {
    for (let i = 0; i < targetCount; i++) {
      const c = targetColors[Math.floor(Math.random() * targetColors.length)]
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * speed * 3,
        vy: (Math.random() - 0.5) * speed * 3,
        r: 4 + Math.random() * 3,
        color: c,
        baseAlpha: 0.7,
        phase: Math.random() * Math.PI * 2,
        isTarget: true,
        captured: false,
        pulsePhase: Math.random() * Math.PI * 2,
      })
    }
  }
}

function onMouseMove(e) {
  const canvas = gameCanvas.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  mouseX = e.clientX - rect.left
  mouseY = e.clientY - rect.top
}

function showScorePop(val, x, y) {
  scorePopVal.value = val
  scorePopX.value = x
  scorePopY.value = y
  scorePop.value = true
  clearTimeout(popTimer)
  popTimer = setTimeout(() => { scorePop.value = false }, 700)
}

function drawGrid(ctx, w, h) {
  ctx.strokeStyle = 'rgba(200, 170, 140, 0.06)'
  ctx.lineWidth = 0.5
  const step = 40
  for (let x = 0; x < w; x += step) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke()
  }
  for (let y = 0; y < h; y += step) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke()
  }
}

function draw() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = window.innerWidth
  const h = window.innerHeight

  if (canvas.width !== w * 2 || canvas.height !== h * 2) {
    canvas.width = w * 2
    canvas.height = h * 2
    canvasW = w
    canvasH = h
  }
  ctx.setTransform(2, 0, 0, 2, 0, 0)

  ctx.fillStyle = 'rgba(26, 25, 22, 1)'
  ctx.fillRect(0, 0, w, h)

  drawGrid(ctx, w, h)

  const capR = gameMode.value === 'level' ? getLevelConfig(currentLevel.value).captureRadius : CAPTURE_RADIUS
  const attR = gameMode.value === 'level' ? getLevelConfig(currentLevel.value).attractRadius : ATTRACT_RADIUS

  for (const p of particles) {
    if (p.captured) continue

    p.phase += 0.008
    p.pulsePhase += 0.03

    const dx = mouseX - p.x
    const dy = mouseY - p.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    const attractR = p.isTarget ? attR : 100
    const attractForce = p.isTarget ? 0.06 : 0.015
    if (dist < attractR && dist > 0) {
      const force = (1 - dist / attractR) * attractForce
      p.vx += (dx / dist) * force
      p.vy += (dy / dist) * force
    }

    if (p.isTarget && scene.value === 'playing') {
      p.vx += (Math.random() - 0.5) * 0.08
      p.vy += (Math.random() - 0.5) * 0.08
    }

    p.x += p.vx
    p.y += p.vy
    p.vx *= 0.985
    p.vy *= 0.985

    if (p.x < -20) p.x = w + 20
    if (p.x > w + 20) p.x = -20
    if (p.y < -20) p.y = h + 20
    if (p.y > h + 20) p.y = -20

    if (p.isTarget && scene.value === 'playing' && dist < capR && dist > 0) {
      p.captured = true
      const pts = 10 + (gameMode.value === 'level' ? currentLevel.value * 2 : timeRound.value)
      score.value += pts
      captured.value++
      showScorePop(pts, p.x, p.y - 20)

      if (gameMode.value === 'level' && captured.value >= getLevelTarget(currentLevel.value)) {
        endGame(true)
      }

      const remaining = particles.filter(pp => pp.isTarget && !pp.captured).length
      if (remaining === 0 && gameMode.value !== 'level') {
        spawnMoreTargets(5 + timeRound.value * 2)
      }
      continue
    }

    const pulse = Math.sin(p.pulsePhase) * 0.15
    let alpha = p.baseAlpha + Math.sin(p.phase) * 0.05 + pulse

    if (p.isTarget) {
      const glowAlpha = 0.15 + Math.sin(p.pulsePhase) * 0.1
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${p.color[0]}, ${p.color[1]}, ${p.color[2]}, ${glowAlpha * 0.3})`
      ctx.fill()

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r * 1.8, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${p.color[0]}, ${p.color[1]}, ${p.color[2]}, ${glowAlpha * 0.5})`
      ctx.fill()

      alpha = 0.7 + Math.sin(p.pulsePhase) * 0.2
    }

    if (dist < (p.isTarget ? attR : 100)) {
      alpha += 0.1 * (1 - dist / (p.isTarget ? attR : 100))
    }

    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${p.color[0]}, ${p.color[1]}, ${p.color[2]}, ${Math.max(0.03, Math.min(1, alpha))})`
    ctx.fill()
  }

  for (let i = 0; i < particles.length; i++) {
    if (particles[i].captured) continue
    for (let j = i + 1; j < particles.length; j++) {
      if (particles[j].captured) continue
      const a = particles[i]
      const b = particles[j]
      const ddx = a.x - b.x
      const ddy = a.y - b.y
      const d = Math.sqrt(ddx * ddx + ddy * ddy)
      const connDist = a.isTarget || b.isTarget ? 100 : 130
      if (d < connDist) {
        const lineAlpha = (1 - d / connDist) * (a.isTarget || b.isTarget ? 0.12 : 0.06)
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = `rgba(200, 170, 140, ${lineAlpha})`
        ctx.lineWidth = 0.5
        ctx.stroke()
      }
    }
  }

  if (mouseX > 0 && mouseY > 0 && scene.value === 'playing') {
    ctx.beginPath()
    ctx.arc(mouseX, mouseY, capR, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(232, 146, 124, 0.15)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])
    ctx.stroke()
    ctx.setLineDash([])

    const grad = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, attR)
    grad.addColorStop(0, 'rgba(232, 146, 124, 0.04)')
    grad.addColorStop(1, 'rgba(232, 146, 124, 0)')
    ctx.beginPath()
    ctx.arc(mouseX, mouseY, attR, 0, Math.PI * 2)
    ctx.fillStyle = grad
    ctx.fill()
  }

  animFrame = requestAnimationFrame(draw)
}

function spawnMoreTargets(count) {
  const targetColors = [[232,146,124],[255,200,80],[168,197,143]]
  const speed = gameMode.value === 'level'
    ? getLevelConfig(currentLevel.value).targetSpeed
    : 0.6 + timeRound.value * 0.1
  for (let i = 0; i < count; i++) {
    const c = targetColors[Math.floor(Math.random() * targetColors.length)]
    particles.push({
      x: Math.random() * canvasW,
      y: Math.random() * canvasH,
      vx: (Math.random() - 0.5) * speed * 3,
      vy: (Math.random() - 0.5) * speed * 3,
      r: 4 + Math.random() * 3,
      color: c,
      baseAlpha: 0.7,
      phase: Math.random() * Math.PI * 2,
      isTarget: true,
      captured: false,
      pulsePhase: Math.random() * Math.PI * 2,
    })
  }
}

function enterLevelSelect() {
  scene.value = 'levels'
  const w = canvasW || window.innerWidth
  const h = canvasH || window.innerHeight
  initParticles(w, h, 50, 0.3, false, 0)
}

function enterTimeChallenge() {
  gameMode.value = 'time'
  timeRound.value = 1
  timeBaseScore.value = 0
  startTimeRound()
}

function startTimeRound() {
  score.value = timeBaseScore.value
  captured.value = 0
  timeTarget.value = timeRound.value * 15 + 10
  timeLeft.value = 25 + timeRound.value * 5
  const w = canvasW || window.innerWidth
  const h = canvasH || window.innerHeight
  const bgCount = 25 + timeRound.value * 3
  const tgtCount = timeRound.value * 8 + 12
  initParticles(w, h, bgCount, 0.25 + timeRound.value * 0.05, true, tgtCount)
  scene.value = 'playing'
  clearInterval(gameTimer)
  gameTimer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) endGame(captured.value >= timeTarget.value)
  }, 1000)
}

function startLevel(lv) {
  if (lv > maxUnlocked.value) return
  gameMode.value = 'level'
  currentLevel.value = lv
  score.value = 0
  captured.value = 0
  const cfg = getLevelConfig(lv)
  timeLeft.value = cfg.time
  const w = canvasW || window.innerWidth
  const h = canvasH || window.innerHeight
  initParticles(w, h, cfg.particleCount, cfg.bgSpeed, true, cfg.targets)
  scene.value = 'playing'
  clearInterval(gameTimer)
  gameTimer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) endGame(false)
  }, 1000)
}

function enterFreeMode() {
  gameMode.value = 'free'
  const w = canvasW || window.innerWidth
  const h = canvasH || window.innerHeight
  initParticles(w, h, 80, 0.5, false, 0)
  scene.value = 'playing'
  startAmbientMusic()
}

function startAmbientMusic() {
  stopAmbientMusic()
  try {
    ambientCtx = new (window.AudioContext || window.webkitAudioContext)()
    const ctx = ambientCtx
    const masterGain = ctx.createGain()
    masterGain.gain.value = 0.08
    masterGain.connect(ctx.destination)
    ambientGain = masterGain

    const notes = [261.63, 329.63, 392.00, 523.25, 440.00, 349.23, 293.66, 369.99]
    let noteIdx = 0

    function playNote() {
      if (!ambientCtx) return
      const osc = ctx.createOscillator()
      const noteGain = ctx.createGain()
      osc.type = 'sine'
      osc.frequency.value = notes[noteIdx % notes.length]
      noteGain.gain.setValueAtTime(0, ctx.currentTime)
      noteGain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.8)
      noteGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 3.5)
      osc.connect(noteGain)
      noteGain.connect(masterGain)
      osc.start(ctx.currentTime)
      osc.stop(ctx.currentTime + 4)
      noteIdx++
      ambientOsc = setTimeout(playNote, 3200)
    }

    const pad = ctx.createOscillator()
    const padGain = ctx.createGain()
    pad.type = 'sine'
    pad.frequency.value = 130.81
    padGain.gain.value = 0.04
    pad.connect(padGain)
    padGain.connect(masterGain)
    pad.start()
    ambientOsc = pad

    playNote()
  } catch (e) {
    console.warn('Ambient music failed:', e)
  }
}

function stopAmbientMusic() {
  if (ambientOsc) {
    if (typeof ambientOsc === 'number') clearTimeout(ambientOsc)
    else try { ambientOsc.stop() } catch {}
    ambientOsc = null
  }
  if (ambientCtx) {
    try { ambientCtx.close() } catch {}
    ambientCtx = null
  }
  ambientGain = null
}

function endGame(win) {
  clearInterval(gameTimer)
  gameTimer = null
  if (gameMode.value === 'free') return

  if (gameMode.value === 'level') {
    resultWin.value = win
    if (win && currentLevel.value >= maxUnlocked.value) {
      maxUnlocked.value = Math.min(20, currentLevel.value + 1)
      localStorage.setItem('gameMaxLevel', maxUnlocked.value.toString())
    }
  } else {
    resultWin.value = win
    if (win) timeBaseScore.value = score.value
  }
  scene.value = 'result'
}

function nextLevel() {
  if (currentLevel.value < 20) startLevel(currentLevel.value + 1)
  else scene.value = 'levels'
}

function timeContinue() {
  timeRound.value++
  startTimeRound()
}

function timeRestart() {
  timeRound.value = 1
  timeBaseScore.value = 0
  startTimeRound()
}

function close() {
  clearInterval(gameTimer)
  clearTimeout(popTimer)
  gameTimer = null
  stopAmbientMusic()
  scene.value = 'menu'
  showModes.value = false
  emit('close')
}

function initScene() {
  if (initialized) return
  initialized = true
  scene.value = 'menu'
  showModes.value = false
  window.addEventListener('mousemove', onMouseMove)
  animFrame = requestAnimationFrame(draw)
  nextTick(() => {
    const w = window.innerWidth
    const h = window.innerHeight
    initParticles(w, h, 50, 0.3, false, 0)
    if (sceneRef.value) sceneRef.value.focus()
  })
}

function teardownScene() {
  clearInterval(gameTimer)
  gameTimer = null
  stopAmbientMusic()
  window.removeEventListener('mousemove', onMouseMove)
  if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null }
  initialized = false
}

onMounted(() => {
  initScene()
})

onBeforeUnmount(() => {
  teardownScene()
  clearTimeout(popTimer)
})
</script>

<style scoped>
.game-scene {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: rgba(26, 25, 22, 1);
  outline: none;
  overflow: hidden;
  animation: gameSceneIn 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes gameSceneIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.game-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.game-close {
  position: absolute;
  top: 20px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255,255,255,0.5);
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  transition: color 0.2s, transform 0.2s, background 0.2s;
  z-index: 20;
}
.game-close:hover { color: rgba(255,255,255,0.9); transform: scale(1.1); background: rgba(255,255,255,0.12); }
.game-close svg { width: 20px; height: 20px; }

.game-ui {
  position: relative;
  z-index: 10;
  pointer-events: auto;
}

.game-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 32px;
}

.game-title {
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 48px;
  font-weight: 300;
  color: rgba(255,255,255,0.8);
  letter-spacing: -0.02em;
  text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}

.game-start-btn {
  padding: 14px 44px;
  border-radius: 10px;
  border: 1.5px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(12px);
  color: rgba(255,255,255,0.8);
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}
.game-start-btn:hover {
  transform: translateY(-2px);
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.35);
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.game-modes {
  display: flex;
  gap: 14px;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 22px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 150px;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}
.mode-btn:hover {
  transform: translateY(-3px);
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.25);
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
}
.mode-icon { font-size: 28px; }
.mode-name { font-size: 15px; font-weight: 700; color: rgba(255,255,255,0.85); }
.mode-desc { font-size: 11px; color: rgba(255,255,255,0.45); text-align: center; }

.modes-pop-enter-active { transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1); }
.modes-pop-leave-active { transition: all 0.2s ease; }
.modes-pop-enter-from { opacity: 0; transform: translateY(20px) scale(0.95); }
.modes-pop-leave-to { opacity: 0; transform: translateY(10px); }

.game-levels {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 24px;
  padding: 40px;
}

.levels-header {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  max-width: 480px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.15s;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}
.back-btn:hover { color: rgba(255,255,255,0.85); }
.back-btn svg { width: 18px; height: 18px; }

.levels-title {
  font-size: 20px;
  font-weight: 700;
  color: rgba(255,255,255,0.8);
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}

.levels-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  width: 100%;
  max-width: 480px;
}

.level-cell {
  aspect-ratio: 1;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.level-cell:hover {
  transform: translateY(-2px);
  background: rgba(255,255,255,0.1);
  border-color: hsla(var(--lv-hue), 60%, 55%, 0.5);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.level-cell.locked { opacity: 0.3; cursor: not-allowed; }
.level-cell.locked:hover { transform: none; box-shadow: none; background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
.level-cell.current { border-color: rgba(232, 146, 124, 0.6); }

.level-num { font-size: 20px; font-weight: 700; color: rgba(255,255,255,0.8); z-index: 1; font-family: 'SF Mono', monospace; }
.level-check { font-size: 11px; color: rgba(168, 197, 143, 0.8); z-index: 1; }

.game-hud {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 24px;
  pointer-events: none;
}

.hud-left, .hud-center, .hud-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.hud-left { align-items: flex-start; }
.hud-right { align-items: flex-end; }

.hud-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}
.hud-value {
  font-family: 'SF Mono', monospace;
  font-size: 28px;
  font-weight: 700;
  color: rgba(255,255,255,0.85);
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.hud-value.urgent { color: #ff6b6b; animation: pulse 0.5s infinite alternate; }
.hud-sub {
  font-family: 'SF Mono', monospace;
  font-size: 14px;
  color: rgba(255,255,255,0.5);
}

@keyframes pulse { from { opacity: 1; } to { opacity: 0.5; } }

.score-pop {
  position: absolute;
  font-family: 'SF Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  color: rgba(232, 146, 124, 0.9);
  pointer-events: none;
  z-index: 15;
  text-shadow: 0 1px 6px rgba(0,0,0,0.4);
}
.score-pop-enter-active { animation: popFloat 0.7s ease-out forwards; }
@keyframes popFloat {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(-36px) scale(1.2); }
}

.game-result {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
}

.result-card {
  background: rgba(26, 25, 22, 0.9);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  padding: 36px 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  min-width: 300px;
  border: 1px solid rgba(255,255,255,0.1);
  animation: resultIn 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.result-card.win { border-color: rgba(168, 197, 143, 0.4); }
.result-card.lose { border-color: rgba(232, 146, 124, 0.4); }

@keyframes resultIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.result-icon { font-size: 42px; }
.result-title { font-size: 22px; font-weight: 700; color: rgba(255,255,255,0.85); font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace; }
.result-score { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.result-score-label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.08em; font-family: 'SF Mono', monospace; }
.result-score-value { font-family: 'SF Mono', monospace; font-size: 40px; font-weight: 700; color: rgba(232, 146, 124, 0.9); }
.result-round { font-size: 13px; color: rgba(255,255,255,0.4); font-family: 'SF Mono', monospace; }

.result-actions { display: flex; gap: 10px; margin-top: 8px; }

.result-btn {
  padding: 9px 22px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
}
.result-btn:hover { background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.85); transform: translateY(-1px); }
.result-btn.primary {
  background: rgba(232, 146, 124, 0.2);
  color: rgba(232, 146, 124, 0.9);
  border-color: rgba(232, 146, 124, 0.4);
}
.result-btn.primary:hover { background: rgba(232, 146, 124, 0.3); }

@media (max-width: 768px) {
  .game-title { font-size: 32px; }
  .game-modes { flex-direction: column; }
  .mode-btn { min-width: 200px; }
  .levels-grid { grid-template-columns: repeat(4, 1fr); max-width: 340px; }
  .hud-value { font-size: 22px; }
  .result-card { padding: 24px 28px; min-width: 260px; }
}
</style>
