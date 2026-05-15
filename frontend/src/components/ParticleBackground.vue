<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animFrame = null
let particles = []
let ripples = []
let mouseX = -1000
let mouseY = -1000

const PARTICLE_COUNT = 50
const CONNECT_DIST = 130
const MOUSE_RADIUS = 180

function initParticles(w, h) {
  particles = []
  const colors = [
    [200, 122, 50],
    [120, 160, 110],
    [170, 100, 90],
    [180, 160, 100],
    [210, 150, 70],
  ]
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const c = colors[Math.floor(Math.random() * colors.length)]
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r: 1.5 + Math.random() * 2.5,
      color: c,
      baseAlpha: 0.25 + Math.random() * 0.3,
      phase: Math.random() * Math.PI * 2,
      wobbleSpeed: 0.005 + Math.random() * 0.01,
    })
  }
}

function addRipple(x, y) {
  ripples.push({
    x, y,
    radius: 0,
    maxRadius: 80 + Math.random() * 40,
    alpha: 0.35,
    speed: 1.5 + Math.random() * 0.5,
  })
  if (ripples.length > 6) ripples.shift()
}

let lastMouseTime = 0
function onMouseMove(e) {
  mouseX = e.clientX
  mouseY = e.clientY
  const now = Date.now()
  if (now - lastMouseTime > 200) {
    lastMouseTime = now
  }
}

function onMouseClick(e) {
  addRipple(e.clientX, e.clientY)
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = window.innerWidth
  const h = window.innerHeight

  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w
    canvas.height = h
    if (particles.length === 0) initParticles(w, h)
  }

  ctx.clearRect(0, 0, w, h)

  const time = Date.now()

  for (const p of particles) {
    p.phase += p.wobbleSpeed
    const wobbleX = Math.sin(p.phase) * 0.3
    const wobbleY = Math.cos(p.phase * 0.7) * 0.2

    const dx = mouseX - p.x
    const dy = mouseY - p.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (dist < MOUSE_RADIUS && dist > 0) {
      const force = (1 - dist / MOUSE_RADIUS) * 0.8
      p.vx += (dx / dist) * force * 0.05
      p.vy += (dy / dist) * force * 0.05
    }

    p.x += p.vx + wobbleX
    p.y += p.vy + wobbleY

    p.vx *= 0.98
    p.vy *= 0.98

    if (p.x < -20) p.x = w + 20
    if (p.x > w + 20) p.x = -20
    if (p.y < -20) p.y = h + 20
    if (p.y > h + 20) p.y = -20

    const proximityAlpha = dist < MOUSE_RADIUS ? 0.15 * (1 - dist / MOUSE_RADIUS) : 0
    const alpha = p.baseAlpha + Math.sin(time * 0.001 + p.phase) * 0.08 + proximityAlpha

    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${p.color[0]}, ${p.color[1]}, ${p.color[2]}, ${Math.max(0.05, alpha)})`
    ctx.fill()
  }

  for (let i = particles.length - 1; i >= 0; i--) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i]
      const b = particles[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const d = Math.sqrt(dx * dx + dy * dy)
      if (d < CONNECT_DIST) {
        const lineAlpha = (1 - d / CONNECT_DIST) * 0.07
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = `rgba(200, 170, 140, ${lineAlpha})`
        ctx.lineWidth = 0.6
        ctx.stroke()
      }
    }
  }

  for (let i = ripples.length - 1; i >= 0; i--) {
    const r = ripples[i]
    r.radius += r.speed
    r.alpha *= 0.97

    if (r.alpha < 0.01 || r.radius > r.maxRadius) {
      ripples.splice(i, 1)
      continue
    }

    ctx.beginPath()
    ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2)
    ctx.strokeStyle = `rgba(200, 150, 80, ${r.alpha})`
    ctx.lineWidth = 1.5
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(r.x, r.y, r.radius * 0.6, 0, Math.PI * 2)
    ctx.strokeStyle = `rgba(200, 150, 80, ${r.alpha * 0.4})`
    ctx.lineWidth = 0.8
    ctx.stroke()
  }

  if (mouseX > 0 && mouseY > 0) {
    const gradient = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, MOUSE_RADIUS)
    gradient.addColorStop(0, 'rgba(200, 150, 80, 0.06)')
    gradient.addColorStop(0.5, 'rgba(200, 150, 80, 0.02)')
    gradient.addColorStop(1, 'rgba(200, 150, 80, 0)')
    ctx.beginPath()
    ctx.arc(mouseX, mouseY, MOUSE_RADIUS, 0, Math.PI * 2)
    ctx.fillStyle = gradient
    ctx.fill()
  }

  animFrame = requestAnimationFrame(draw)
}

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('click', onMouseClick)
  animFrame = requestAnimationFrame(draw)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('click', onMouseClick)
  if (animFrame) cancelAnimationFrame(animFrame)
})
</script>

<style scoped>
.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
