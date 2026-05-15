<template>
  <div class="weather-bar glass-bar">
    <div class="weather-main">
      <span class="weather-icon">{{ weatherIcon }}</span>
      <div class="weather-data">
        <span class="weather-temp">{{ temperature }}°</span>
        <span class="weather-desc">{{ description }}</span>
      </div>
    </div>
    <div class="weather-details">
      <span class="weather-loc">{{ location }}</span>
      <span class="weather-dot">·</span>
      <span class="weather-humid">💧 {{ humidity }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const temperature = ref('--')
const description = ref('Loading...')
const humidity = ref('--')
const location = ref('Detecting...')
const weatherIcon = ref('🌤️')

const weatherMap = {
  0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️',
  45: '🌫️', 48: '🌫️',
  51: '🌦️', 53: '🌦️', 55: '🌧️',
  61: '🌧️', 63: '🌧️', 65: '🌧️',
  71: '🌨️', 73: '🌨️', 75: '❄️',
  80: '🌦️', 81: '🌧️', 82: '⛈️',
  95: '⛈️', 96: '⛈️', 99: '⛈️',
}

const descMap = {
  0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
  45: 'Foggy', 48: 'Depositing rime fog',
  51: 'Light drizzle', 53: 'Drizzle', 55: 'Dense drizzle',
  61: 'Light rain', 63: 'Moderate rain', 65: 'Heavy rain',
  71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
  80: 'Rain showers', 81: 'Moderate showers', 82: 'Violent showers',
  95: 'Thunderstorm', 96: 'Thunderstorm w/ hail', 99: 'Heavy thunderstorm',
}

async function fetchWeather(lat, lon) {
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto`
    const resp = await fetch(url)
    const data = await resp.json()
    const cur = data.current
    temperature.value = Math.round(cur.temperature_2m)
    humidity.value = cur.relative_humidity_2m
    const code = cur.weather_code
    weatherIcon.value = weatherMap[code] || '🌡️'
    description.value = descMap[code] || 'Unknown'
  } catch {
    description.value = 'Offline'
    temperature.value = '--'
  }
}

async function fetchLocationByIP() {
  try {
    const resp = await fetch('https://ipapi.co/json/')
    const data = await resp.json()
    if (data.latitude && data.longitude) {
      fetchWeather(data.latitude, data.longitude)
      const city = data.city || data.region || ''
      if (city && city !== 'Unknown') {
        location.value = city
      } else {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
        if (tz && tz.startsWith('Asia/Shanghai')) {
          location.value = 'China'
        } else {
          location.value = `${data.latitude.toFixed(2)}, ${data.longitude.toFixed(2)}`
        }
      }
    } else {
      fallback()
    }
  } catch {
    fallback()
  }
}

function fallback() {
  fetchWeather(39.9, 116.4)
  location.value = 'Beijing'
}

onMounted(() => {
  fetchLocationByIP()
})
</script>

<style scoped>
.weather-bar {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  font-size: 13px;
  animation: float 6s ease-in-out infinite;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weather-icon {
  font-size: 20px;
  line-height: 1;
}

.weather-data {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.weather-temp {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-ink-800);
  font-variant-numeric: tabular-nums;
  font-family: 'Courier New', monospace;
}

.weather-desc {
  font-size: 12px;
  color: var(--color-ink-500);
}

.weather-details {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-ink-400);
}

.weather-dot {
  opacity: 0.3;
}
</style>
