import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)

  function setToken(t) {
    token.value = t
    if (t) localStorage.setItem('token', t)
    else localStorage.removeItem('token')
    api.defaults.headers.common['Authorization'] = t ? `Bearer ${t}` : ''
  }

  async function login(username, password) {
    const form = new URLSearchParams({ username, password })
    const { data } = await api.post('/api/auth/login', form)
    setToken(data.access_token)
  }

  function logout() {
    setToken(null)
  }

  // restore header on load
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  return { token, login, logout }
})
