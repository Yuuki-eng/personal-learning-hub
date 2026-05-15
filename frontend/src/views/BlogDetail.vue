<template>
  <div class="blog-detail page-enter">
    <div v-if="!blog" class="loading">Loading...</div>
    <template v-else>
      <div class="detail-header">
        <router-link to="/blog" class="back-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back
        </router-link>
        <div class="detail-actions">
          <router-link :to="`/blog/${blog.id}/edit`" class="btn-secondary">Edit</router-link>
          <button class="btn-secondary danger" @click="handleDelete">Delete</button>
        </div>
      </div>

      <article class="detail-content">
        <div class="detail-meta">
          <span class="detail-cat">{{ blog.category }}</span>
          <span class="detail-date">{{ formatDate(blog.created_at) }}</span>
          <span class="detail-views">{{ blog.view_count }} views</span>
        </div>
        <h1 class="detail-title">{{ blog.title }}</h1>
        <div class="detail-tags" v-if="blog.tags">
          <span v-for="tag in blog.tags.split(',')" :key="tag" class="tag-pill">{{ tag.trim() }}</span>
        </div>
        <div class="markdown-body" v-html="renderedContent"></div>
      </article>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBlog, deleteBlog } from '../api/blog'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const blog = ref(null)

const renderedContent = computed(() => {
  if (!blog.value?.content) return ''
  return blog.value.content
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('Delete this post?', 'Confirm', { type: 'warning' })
    await deleteBlog(route.params.id)
    router.push('/blog')
  } catch {}
}

onMounted(async () => {
  blog.value = await getBlog(route.params.id)
})
</script>

<style scoped>
.blog-detail { max-width: 760px; }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-ink-500);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.back-link:hover { color: var(--color-ink-800); }
.back-link svg { width: 16px; height: 16px; }

.detail-actions { display: flex; gap: 8px; }

.btn-secondary {
  padding: 7px 14px;
  border: 1px solid var(--color-ink-200);
  border-radius: 10px;
  background: transparent;
  font-size: 13px;
  color: var(--color-ink-600);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--color-ink-50);
  border-color: var(--color-ink-300);
}

.btn-secondary.danger { color: #b91c1c; border-color: #fecaca; }
.btn-secondary.danger:hover { background: #fef2f2; }

.detail-content {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 16px;
  padding: 36px 40px;
}

.detail-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}

.detail-cat {
  color: var(--color-warm-600);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 12px;
}

.detail-date, .detail-views { color: var(--color-ink-400); }

.detail-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-ink-900);
  letter-spacing: -0.02em;
  margin-bottom: 12px;
  line-height: 1.3;
}

.detail-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 24px;
}

.tag-pill {
  font-size: 12px;
  padding: 3px 10px;
  background: var(--color-ink-50);
  border-radius: 8px;
  color: var(--color-ink-500);
}

.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-ink-700);
}

.markdown-body :deep(h1) { font-size: 22px; font-weight: 700; margin: 24px 0 12px; color: var(--color-ink-800); }
.markdown-body :deep(h2) { font-size: 18px; font-weight: 600; margin: 20px 0 10px; color: var(--color-ink-800); }
.markdown-body :deep(h3) { font-size: 16px; font-weight: 600; margin: 16px 0 8px; color: var(--color-ink-800); }
.markdown-body :deep(code) {
  background: var(--color-ink-50);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--color-ink-400);
}
</style>
