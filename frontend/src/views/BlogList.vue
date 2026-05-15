<template>
  <div class="blog-page page-enter">
    <div v-animate="'fade-up'" class="blog-top">
      <div>
        <h1 class="page-title">Blog</h1>
        <p class="page-desc">Your learning notes and thoughts</p>
      </div>
      <router-link to="/blog/new" class="btn-primary">New Post</router-link>
    </div>

    <div v-animate="{ name: 'fade-up', delay: 80 }" class="blog-filters">
      <input v-model="keyword" type="text" placeholder="Search posts..." class="search-input" @input="debouncedFetch" />
      <div class="filter-tags">
        <button class="filter-tag" :class="{ active: !selectedCategory }" @click="selectedCategory = null; fetchBlogs()">All</button>
        <button v-for="cat in categories" :key="cat.name" class="filter-tag" :class="{ active: selectedCategory === cat.name }"
          @click="selectedCategory = cat.name; fetchBlogs()">
          {{ cat.name }} <span class="tag-count">{{ cat.count }}</span>
        </button>
      </div>
    </div>

    <div v-if="blogs.length === 0" v-animate="'fade-up'" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="8" y="6" width="32" height="36" rx="3"/>
          <line x1="16" y1="14" x2="32" y2="14"/>
          <line x1="16" y1="22" x2="28" y2="22"/>
          <line x1="16" y1="30" x2="24" y2="30"/>
        </svg>
      </div>
      <p>No posts yet</p>
      <router-link to="/blog/new" class="empty-link">Write your first post</router-link>
    </div>

    <div v-else class="blog-grid">
      <router-link v-for="(blog, i) in blogs" :key="blog.id" :to="`/blog/${blog.id}`"
        v-animate="{ name: 'fade-up', delay: i * 60 }" class="blog-card">
        <div class="blog-card-top">
          <span class="blog-cat">{{ blog.category || 'Uncategorized' }}</span>
          <span class="blog-views">{{ blog.view_count }}</span>
        </div>
        <h2 class="blog-title">{{ blog.title }}</h2>
        <p class="blog-summary" v-if="blog.summary">{{ blog.summary }}</p>
        <div class="blog-tags" v-if="blog.tags">
          <span v-for="tag in blog.tags.split(',')" :key="tag" class="tag-pill">{{ tag.trim() }}</span>
        </div>
        <div class="blog-date">{{ formatDate(blog.created_at) }}</div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBlogs, getCategories } from '../api/blog'

const blogs = ref([])
const categories = ref([])
const keyword = ref('')
const selectedCategory = ref(null)
let debounceTimer = null

function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchBlogs, 300)
}

async function fetchBlogs() {
  const params = { page: 1, page_size: 50 }
  if (keyword.value) params.keyword = keyword.value
  if (selectedCategory.value) params.category = selectedCategory.value
  blogs.value = await getBlogs(params)
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(async () => {
  const [b, c] = await Promise.all([fetchBlogs(), getCategories()])
  categories.value = c
})
</script>

<style scoped>
.blog-page { max-width: 900px; }

.blog-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-ink-900);
  letter-spacing: -0.02em;
}

.page-desc {
  color: var(--color-ink-400);
  font-size: 14px;
  margin-top: 4px;
}

.blog-filters {
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid var(--color-ink-200);
  border-radius: 12px;
  font-size: 14px;
  background: var(--color-surface-elevated);
  color: var(--color-ink-800);
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: var(--color-warm-400);
}

.search-input::placeholder {
  color: var(--color-ink-300);
}

.filter-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-tag {
  padding: 5px 12px;
  border: 1px solid var(--color-ink-200);
  border-radius: 8px;
  background: transparent;
  font-size: 13px;
  color: var(--color-ink-500);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-tag:hover { border-color: var(--color-ink-300); color: var(--color-ink-700); }

.filter-tag.active {
  background: var(--color-ink-800);
  color: var(--color-warm-50);
  border-color: var(--color-ink-800);
}

.tag-count {
  font-size: 11px;
  opacity: 0.6;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--color-ink-200);
}

.empty-state p {
  color: var(--color-ink-400);
  font-size: 15px;
  margin-bottom: 8px;
}

.empty-link {
  color: var(--color-warm-500);
  text-decoration: none;
  font-weight: 500;
}

.blog-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 700px) { .blog-grid { grid-template-columns: 1fr; } }

.blog-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 14px;
  text-decoration: none;
  transition: transform 0.25s, box-shadow 0.25s;
  animation: fadeSlideUp 0.4s ease both;
}

.blog-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(26, 22, 20, 0.06);
}

.blog-card-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.blog-cat {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-warm-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.blog-views {
  font-size: 12px;
  color: var(--color-ink-300);
}

.blog-views::before {
  content: '\u{1F441} ';
  font-size: 10px;
}

.blog-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-ink-800);
  margin-bottom: 6px;
  line-height: 1.4;
}

.blog-summary {
  font-size: 13px;
  color: var(--color-ink-400);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
}

.blog-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.tag-pill {
  font-size: 11px;
  padding: 2px 8px;
  background: var(--color-ink-50);
  border-radius: 6px;
  color: var(--color-ink-500);
}

.blog-date {
  font-size: 12px;
  color: var(--color-ink-300);
  margin-top: auto;
}

</style>
