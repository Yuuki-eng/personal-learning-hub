import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue'), meta: { title: 'Home' } },
  { path: '/blog', name: 'BlogList', component: () => import('../views/BlogList.vue'), meta: { title: 'Blog' } },
  { path: '/blog/new', name: 'BlogNew', component: () => import('../views/BlogEditor.vue'), meta: { title: 'Write' } },
  { path: '/blog/:id', name: 'BlogDetail', component: () => import('../views/BlogDetail.vue'), meta: { title: 'Blog' } },
  { path: '/blog/:id/edit', name: 'BlogEdit', component: () => import('../views/BlogEditor.vue'), meta: { title: 'Edit' } },
  { path: '/plan', name: 'Plan', component: () => import('../views/Plan.vue'), meta: { title: 'Plan' } },
  { path: '/countdown', name: 'Countdown', component: () => import('../views/Countdown.vue'), meta: { title: 'Countdown' } },
  { path: '/music', name: 'Music', component: () => import('../views/Music.vue'), meta: { title: 'Music' } },
  { path: '/files', name: 'Files', component: () => import('../views/FileManager.vue'), meta: { title: 'Files' } },
  { path: '/ai', name: 'AIChat', component: () => import('../views/AIChat.vue'), meta: { title: 'AI' } },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { title: 'Settings' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'Learning Hub'} - Learning Hub`
})

export default router
