<template>
  <div class="login-page">
    <div class="login-card card">
      <h1>Admin Login</h1>
      <p class="text-muted" style="margin-bottom:24px">Live Song Book</p>
      <form @submit.prevent="submit">
        <div class="field">
          <label>Username</label>
          <input v-model="form.username" type="text" autocomplete="username" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="form.password" type="password" autocomplete="current-password" required />
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <button type="submit" class="btn-primary" style="width:100%;" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/admin/live')
  } catch {
    error.value = 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.login-card { width: 100%; max-width: 360px; }
h1 { margin-bottom: 4px; }

.error-msg {
  background: rgba(192,57,43,0.15);
  border: 1px solid var(--danger);
  border-radius: 6px;
  color: #e74c3c;
  padding: 10px 12px;
  font-size: 13px;
  margin-bottom: 16px;
}
</style>
