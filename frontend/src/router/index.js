import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', component: () => import('../views/PublicView.vue') },
  { path: '/admin/login', component: () => import('../views/AdminLogin.vue') },
  {
    path: '/admin',
    component: () => import('../views/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/live' },
      { path: 'live', component: () => import('../views/LiveControl.vue') },
      { path: 'songs', component: () => import('../views/SongManager.vue') },
      { path: 'setlists', component: () => import('../views/SetlistManager.vue') },
      { path: 'pdf', component: () => import('../views/PdfManager.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return '/admin/login'
  }
})

export default router
