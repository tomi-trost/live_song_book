<template>
  <div class="admin-root">
    <nav class="admin-nav">
      <div class="nav-inner">
        <RouterLink to="/" class="nav-brand">🎵 Song Book</RouterLink>
        <div class="nav-links">
          <RouterLink to="/admin/live" class="nav-link">Live</RouterLink>
          <RouterLink to="/admin/songs" class="nav-link">Songs</RouterLink>
          <RouterLink to="/admin/setlists" class="nav-link">Setlists</RouterLink>
          <RouterLink to="/admin/pdf" class="nav-link">PDFs</RouterLink>
        </div>
        <button class="btn-ghost" style="font-size:13px" @click="logout">Sign out</button>
      </div>
    </nav>
    <RouterView />
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-root { min-height: 100dvh; }

.admin-nav {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 52px;
}

.nav-brand { font-weight: 700; font-size: 16px; color: var(--text); margin-right: 8px; }

.nav-links { display: flex; gap: 4px; flex: 1; }

.nav-link {
  padding: 6px 12px;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
  transition: color 0.15s, background 0.15s;
}

.nav-link:hover { color: var(--text); background: var(--surface2); }
.nav-link.router-link-active { color: var(--accent); background: var(--surface2); }
</style>
