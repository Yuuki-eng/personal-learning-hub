<template>
  <div class="editor-page page-enter">
    <div class="editor-top">
      <router-link to="/blog" class="back-link">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        Back
      </router-link>
      <div class="editor-actions">
        <button class="btn-secondary" @click="saveDraft" :disabled="saving">Save Draft</button>
        <button class="btn-primary" @click="publish" :disabled="saving">{{ saving ? 'Saving...' : 'Publish' }}</button>
      </div>
    </div>

    <div class="editor-body">
      <input v-model="form.title" type="text" class="title-input" placeholder="Post title..." />

      <div class="meta-row">
        <input v-model="form.category" type="text" class="meta-input" placeholder="Category" />
        <input v-model="form.tags" type="text" class="meta-input" placeholder="Tags (comma separated)" />
        <input v-model="form.summary" type="text" class="meta-input wide" placeholder="Summary (optional)" />
      </div>

      <div class="editor-container">
        <MdEditor
          v-model="form.content"
          :theme="'light'"
          language="en"
          style="height: 500px; border-radius: 12px; overflow: hidden;"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getBlog, createBlog, updateBlog } from '../api/blog'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)

const form = ref({
  title: '',
  content: '',
  summary: '',
  category: 'Uncategorized',
  tags: '',
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    const blog = await getBlog(route.params.id)
    form.value = {
      title: blog.title,
      content: blog.content,
      summary: blog.summary || '',
      category: blog.category || 'Uncategorized',
      tags: blog.tags || '',
    }
  }
})

async function saveDraft() {
  await doSave(false)
}

async function publish() {
  await doSave(true)
}

async function doSave(published) {
  if (saving.value) return
  if (!form.value.title.trim()) {
    ElMessage.warning('Title is required')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateBlog(route.params.id, { ...form.value, is_published: published })
      ElMessage.success('Updated')
    } else {
      const blog = await createBlog({ ...form.value, is_published: published })
      ElMessage.success('Created')
      router.push(`/blog/${blog.id}`)
    }
  } catch {}
  saving.value = false
}
</script>

<style scoped>
.editor-page { max-width: 900px; }

.editor-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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

.editor-actions { display: flex; gap: 8px; }

.editor-body {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-ink-100);
  border-radius: 16px;
  padding: 28px;
}

.title-input {
  width: 100%;
  border: none;
  font-size: 26px;
  font-weight: 700;
  color: var(--color-ink-900);
  outline: none;
  margin-bottom: 16px;
  background: transparent;
  letter-spacing: -0.01em;
}

.title-input::placeholder { color: var(--color-ink-200); }

.meta-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.meta-input {
  padding: 8px 12px;
  border: 1px solid var(--color-ink-200);
  border-radius: 10px;
  font-size: 13px;
  color: var(--color-ink-700);
  outline: none;
  background: var(--color-ink-50);
  min-width: 140px;
  transition: border-color 0.2s;
}

.meta-input.wide { flex: 1; min-width: 200px; }
.meta-input:focus { border-color: var(--color-warm-400); }
.meta-input::placeholder { color: var(--color-ink-300); }

.editor-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-ink-100);
}
</style>
