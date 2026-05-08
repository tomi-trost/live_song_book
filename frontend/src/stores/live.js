import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'
import api from '../api'

export const useLiveStore = defineStore('live', () => {
  const state = ref({ is_active: false, current_song_id: null, setlist_id: null, position: 0, song: null })
  let es = null

  async function fetchState() {
    const { data } = await api.get('/api/live/state')
    state.value = data
  }

  function connect() {
    if (es) return
    es = new EventSource('/api/live/stream')
    es.addEventListener('state', (e) => {
      state.value = JSON.parse(e.data)
    })
    es.onerror = () => {
      es.close()
      es = null
      setTimeout(connect, 3000)
    }
  }

  function disconnect() {
    if (es) { es.close(); es = null }
  }

  return { state, fetchState, connect, disconnect }
})
