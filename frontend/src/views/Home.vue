<template>
  <div class="home-page page-enter">
    <header v-animate="'fade-up'" class="home-top">
      <div class="home-top-left">
        <div class="greeting-block">
          <h1 class="greeting-text">
            <span class="greeting-emoji">{{ greetingEmoji }}</span>
            {{ greetingText }}
          </h1>
          <p class="greeting-sub">{{ todayFormatted }}</p>
        </div>
        <WeatherWidget />
      </div>
      <div class="home-stats">
        <div v-for="(stat, i) in stats" :key="stat.label" class="stat-card"
          v-animate="{ name: 'scale-in', delay: i * 80 }"
          :style="{ '--accent': stat.color }">
          <span class="stat-num">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <div class="stat-bar">
            <div class="stat-bar-fill" :style="{ width: stat.pct + '%' }"></div>
          </div>
        </div>
      </div>
    </header>

    <section v-animate="{ name: 'blur-in', delay: 100 }" class="viz-section">
      <div class="viz-wrapper">
        <HomeVisualizer />
      </div>
    </section>

    <section class="countdown-section">
      <div v-animate="{ name: 'fade-left' }" class="countdown-header">
        <h2><span class="pixel-dot"></span> COUNTDOWNS</h2>
        <router-link to="/countdown" class="section-link">+ add</router-link>
      </div>
      <div v-if="countdowns.length === 0" v-animate="'fade-up'" class="empty-block">
        <router-link to="/countdown">Create your first countdown →</router-link>
      </div>
      <div v-else class="countdown-grid">
        <router-link
          v-for="(cd, i) in countdowns.slice(0, 6)"
          :key="cd.id"
          :to="'/countdown'"
          v-animate="{ name: 'scale-in', delay: i * 70 }"
          class="countdown-tile"
          :style="{ '--tile-color': cd.color || '#d4944f' }"
        >
          <div class="tile-label">{{ cd.title }}</div>
          <div class="tile-numbers" v-if="getTimeDiff(cd.target_datetime).total > 0">
            <template v-if="getTimeDiff(cd.target_datetime).days > 0">
              <span class="tile-num">{{ getTimeDiff(cd.target_datetime).days }}</span>
              <span class="tile-sep">d</span>
              <span class="tile-num">{{ pad(getTimeDiff(cd.target_datetime).hours) }}</span>
              <span class="tile-sep">:</span>
              <span class="tile-num">{{ pad(getTimeDiff(cd.target_datetime).minutes) }}</span>
            </template>
            <template v-else>
              <span class="tile-num">{{ pad(getTimeDiff(cd.target_datetime).hours) }}</span>
              <span class="tile-sep">:</span>
              <span class="tile-num">{{ pad(getTimeDiff(cd.target_datetime).minutes) }}</span>
              <span class="tile-sep">:</span>
              <span class="tile-num">{{ pad(getTimeDiff(cd.target_datetime).seconds) }}</span>
            </template>
          </div>
          <div class="tile-numbers" v-else>
            <span class="tile-passed">PASSED</span>
          </div>
          <div class="tile-units">D : H : M</div>
        </router-link>
      </div>
    </section>

    <div class="home-columns">
      <section v-animate="{ name: 'fade-left', delay: 80 }" class="col-plans">
        <div class="col-header">
          <h2><span class="pixel-dot"></span> PLANS</h2>
          <router-link to="/plan" class="section-link">view all →</router-link>
        </div>
        <div v-if="plans.length === 0" class="empty-block">
          <router-link to="/plan">Create your first plan →</router-link>
        </div>
        <div v-else class="plan-stack">
          <router-link v-for="(plan, i) in plans.slice(0, 5)" :key="plan.id"
            :to="'/plan'"
            v-animate="{ name: 'fade-left', delay: i * 60 }" class="plan-row">
            <div class="plan-status-dot" :class="plan.status"></div>
            <div class="plan-body">
              <div class="plan-name">{{ plan.title }}</div>
              <div class="plan-meta">
                <span class="tag-pixel" :class="plan.priority">{{ plan.priority }}</span>
                <span v-if="plan.deadline" class="plan-deadline">{{ formatDate(plan.deadline) }}</span>
              </div>
            </div>
            <div class="plan-progress-bar">
              <div class="plan-progress-fill" :style="{ width: plan.progress + '%' }"></div>
            </div>
            <span class="plan-pct">{{ plan.progress }}%</span>
          </router-link>
        </div>
      </section>

      <section v-animate="{ name: 'fade-right', delay: 120 }" class="col-blogs">
        <div class="col-header">
          <h2><span class="pixel-dot"></span> POSTS</h2>
          <router-link to="/blog" class="section-link">view all →</router-link>
        </div>
        <div v-if="blogs.length === 0" class="empty-block">
          <router-link to="/blog/new">Write your first post →</router-link>
        </div>
        <div v-else class="blog-stack">
          <router-link
            v-for="(blog, idx) in blogs.slice(0, 5)"
            :key="blog.id"
            :to="`/blog/${blog.id}`"
            v-animate="{ name: 'fade-right', delay: idx * 70 }"
            class="blog-row"
          >
            <div class="blog-row-cat">{{ blog.category || 'note' }}</div>
            <div class="blog-row-title">{{ blog.title }}</div>
            <div class="blog-row-meta">
              <span>{{ formatDate(blog.created_at) }}</span>
              <span>{{ blog.view_count }} views</span>
            </div>
          </router-link>
        </div>
      </section>
    </div>

    <AIQuickWidget />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getBlogs } from '../api/blog'
import { getPlans } from '../api/plan'
import { getCountdowns } from '../api/countdown'
import { getUsageStats } from '../api/ai'
import HomeVisualizer from '../components/HomeVisualizer.vue'
import WeatherWidget from '../components/WeatherWidget.vue'
import AIQuickWidget from '../components/AIQuickWidget.vue'

const blogs = ref([])
const plans = ref([])
const countdowns = ref([])
const usageStats = ref({})
const router = useRouter()
const tick = ref(Date.now())
let tickInterval = null

const greetingEmoji = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '🌙'
  if (h < 12) return '☀️'
  if (h < 18) return '⛅'
  return '🌙'
})

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return 'Burning the midnight oil?'
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const stats = computed(() => [
  { label: 'POSTS', value: usageStats.value.blogs || 0, color: '#658a4e', pct: Math.min(100, (usageStats.value.blogs || 0) * 10) },
  { label: 'PLANS', value: usageStats.value.plans_total || 0, color: '#d4944f', pct: Math.min(100, (usageStats.value.plans_total || 0) * 8) },
  { label: 'DONE', value: usageStats.value.plans_completed || 0, color: '#e85d2a', pct: usageStats.value.plans_total ? Math.round((usageStats.value.plans_completed || 0) / usageStats.value.plans_total * 100) : 0 },
  { label: 'CHATS', value: usageStats.value.chat_sessions || 0, color: '#5e534c', pct: Math.min(100, (usageStats.value.chat_sessions || 0) * 5) },
])

function getTimeDiff(target) {
  const diff = new Date(target) - tick.value
  const total = diff
  const days = Math.max(0, Math.floor(diff / 86400000))
  const hours = Math.max(0, Math.floor((diff % 86400000) / 3600000))
  const minutes = Math.max(0, Math.floor((diff % 3600000) / 60000))
  const seconds = Math.max(0, Math.floor((diff % 60000) / 1000))
  return { total, days, hours, minutes, seconds }
}

function pad(n) {
  return String(n).padStart(2, '0')
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(async () => {
  try {
    const [b, p, c, s] = await Promise.all([
      getBlogs({ page: 1, page_size: 5 }),
      getPlans(),
      getCountdowns(),
      getUsageStats(),
    ])
    blogs.value = b
    plans.value = p
    countdowns.value = c
    usageStats.value = s
  } catch {}

  tickInterval = setInterval(() => {
    tick.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (tickInterval) clearInterval(tickInterval)
})
</script>

<style scoped>
.home-page {
  max-width: 1080px;
  position: relative;
}

.home-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.home-top-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.greeting-text {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-ink-900);
  letter-spacing: -0.03em;
  font-family: 'Courier New', monospace;
}

.greeting-emoji {
  font-size: 20px;
  margin-right: 2px;
}

.greeting-sub {
  color: var(--color-ink-400);
  font-size: 12px;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.02em;
}

.home-stats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-card {
  background: var(--color-surface-elevated);
  border: 1.5px solid var(--color-ink-200);
  padding: 12px 16px;
  min-width: 90px;
  box-shadow: 2px 2px 0 var(--color-ink-100);
  transition: all 0.15s ease;
}

.stat-card:hover {
  box-shadow: 3px 3px 0 var(--color-ink-300);
  transform: translate(-1px, -1px);
}

.stat-num {
  display: block;
  font-size: 22px;
  font-weight: 800;
  color: var(--color-ink-800);
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  display: block;
  font-size: 10px;
  color: var(--color-ink-400);
  font-weight: 700;
  letter-spacing: 0.08em;
  font-family: 'Courier New', monospace;
  margin: 2px 0 6px;
}

.stat-bar {
  width: 100%;
  height: 3px;
  background: var(--color-ink-100);
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  background: var(--accent, var(--color-warm-400));
  transition: width 0.6s ease;
}

.viz-section {
  margin-bottom: 28px;
}

.viz-wrapper {
  border: 2px solid var(--color-ink-200);
  box-shadow: 4px 4px 0 var(--color-ink-100);
  overflow: hidden;
}

.countdown-section {
  margin-bottom: 28px;
}

.countdown-header,
.col-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.countdown-header h2,
.col-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-ink-700);
  letter-spacing: 0.06em;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
}

.section-link {
  font-size: 12px;
  color: var(--color-ink-400);
  text-decoration: none;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  transition: color 0.15s;
}

.section-link:hover {
  color: var(--color-warm-500);
}

.countdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(155px, 1fr));
  gap: 10px;
}

.countdown-tile {
  background: var(--color-surface-elevated);
  border: 1.5px solid var(--color-ink-200);
  padding: 14px 14px 10px;
  border-left: 3px solid var(--tile-color);
  box-shadow: 2px 2px 0 var(--color-ink-100);
  transition: all 0.15s ease;
  position: relative;
  overflow: hidden;
  display: block;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.countdown-tile::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 6px;
  height: 6px;
  background: var(--tile-color);
}

.countdown-tile:hover {
  box-shadow: 3px 3px 0 var(--color-ink-300);
  transform: translate(-1px, -1px);
}

.tile-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-ink-600);
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Courier New', monospace;
}

.tile-numbers {
  display: flex;
  align-items: baseline;
  gap: 2px;
  font-family: 'Courier New', monospace;
}

.tile-num {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-ink-800);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.tile-sep {
  font-size: 20px;
  font-weight: 400;
  color: var(--color-ink-300);
  margin: 0 1px;
}

.tile-passed {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-ink-400);
  letter-spacing: 0.08em;
  font-family: 'Courier New', monospace;
}

.tile-units {
  font-size: 9px;
  color: var(--color-ink-300);
  letter-spacing: 0.15em;
  font-family: 'Courier New', monospace;
  margin-top: 4px;
}

.empty-block {
  padding: 20px;
  text-align: center;
  border: 1.5px dashed var(--color-ink-200);
  background: var(--color-ink-50);
}

.empty-block a {
  color: var(--color-warm-500);
  text-decoration: none;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.empty-block a:hover {
  text-decoration: underline;
}

.home-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  align-items: start;
}

@media (max-width: 860px) {
  .home-columns { grid-template-columns: 1fr; }
  .home-top { flex-direction: column; }
}

.plan-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plan-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--color-surface-elevated);
  border: 1.5px solid var(--color-ink-200);
  box-shadow: 1px 1px 0 var(--color-ink-100);
  transition: all 0.12s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.plan-row:hover {
  box-shadow: 2px 2px 0 var(--color-ink-200);
  transform: translate(-1px, -1px);
}

.plan-status-dot {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  border: 1.5px solid var(--color-ink-400);
}

.plan-status-dot.done {
  background: var(--color-sage-500);
  border-color: var(--color-sage-500);
}

.plan-status-dot.in_progress {
  background: var(--color-warm-400);
  border-color: var(--color-warm-400);
}

.plan-body {
  flex: 1;
  min-width: 0;
}

.plan-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink-800);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.plan-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
}

.tag-pixel.high { color: var(--color-coral-500); }
.tag-pixel.medium { color: var(--color-warm-500); }
.tag-pixel.low { color: var(--color-sage-500); }

.plan-deadline {
  font-size: 10px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
}

.plan-progress-bar {
  width: 48px;
  height: 4px;
  background: var(--color-ink-100);
  flex-shrink: 0;
}

.plan-progress-fill {
  height: 100%;
  background: var(--color-warm-400);
  transition: width 0.4s ease;
}

.plan-pct {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-ink-500);
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  min-width: 30px;
  text-align: right;
}

.blog-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.blog-row {
  display: block;
  padding: 12px 14px;
  background: var(--color-surface-elevated);
  border: 1.5px solid var(--color-ink-200);
  text-decoration: none;
  color: inherit;
  box-shadow: 1px 1px 0 var(--color-ink-100);
  transition: all 0.12s ease;
  animation: fadeSlideUp 0.3s ease both;
  animation-delay: calc(var(--row-idx, 0) * 0.06s);
}

.blog-row:hover {
  box-shadow: 2px 2px 0 var(--color-ink-200);
  transform: translate(-1px, -1px);
  border-color: var(--color-warm-300);
}

.blog-row-cat {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-sage-600);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: 'Courier New', monospace;
  margin-bottom: 4px;
}

.blog-row-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-ink-800);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.blog-row-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--color-ink-400);
  font-family: 'Courier New', monospace;
}
</style>
