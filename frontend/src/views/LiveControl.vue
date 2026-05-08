<template>
  <div class="page">
    <div class="flex items-center justify-between" style="margin-bottom:24px">
      <div>
        <h1>Live Control</h1>
        <p class="text-muted">Dictate what song is shown to your audience</p>
      </div>
      <div class="flex items-center gap-2">
        <span :class="['badge', live.state.is_active ? 'badge-live' : 'badge-off']">
          {{ live.state.is_active ? 'LIVE' : 'OFFLINE' }}
        </span>
        <button v-if="live.state.is_active" class="btn-danger" @click="stop">Stop show</button>
      </div>
    </div>

    <!-- Start setlist -->
    <div class="card" style="margin-bottom:20px">
      <h2>Start a setlist</h2>
      <div class="flex gap-3 wrap">
        <select v-model="selectedSetlist" style="flex:1;min-width:200px">
          <option value="">— choose a setlist —</option>
          <option v-for="s in setlists" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <button class="btn-primary" :disabled="!selectedSetlist" @click="startSetlist">Start setlist</button>
      </div>
    </div>

    <!-- Active setlist controls -->
    <div v-if="live.state.setlist_id && activeSetlist" class="card" style="margin-bottom:20px">
      <div class="flex items-center justify-between" style="margin-bottom:16px">
        <h2 style="margin:0">{{ activeSetlist.name }}</h2>
        <div class="flex gap-2">
          <button class="btn-secondary" :disabled="live.state.position === 0" @click="prev">← Prev</button>
          <button class="btn-secondary" :disabled="live.state.position >= activeSetlist.song_ids.length - 1" @click="next">Next →</button>
        </div>
      </div>
      <div class="setlist-songs">
        <div
          v-for="(songId, idx) in activeSetlist.song_ids"
          :key="songId"
          :class="['setlist-item', { active: live.state.current_song_id === songId }]"
          @click="setSong(songId)"
        >
          <span class="item-num">{{ idx + 1 }}</span>
          <span class="item-title">{{ songMap[songId]?.title ?? songId }}</span>
          <span class="item-author text-muted">{{ songMap[songId]?.author }}</span>
          <span v-if="live.state.current_song_id === songId" class="item-badge badge badge-live">NOW</span>
        </div>
      </div>
    </div>

    <!-- Manual song override -->
    <div class="card">
      <h2>Play any song</h2>
      <div class="flex gap-3 wrap">
        <select v-model="manualSong" style="flex:1;min-width:200px">
          <option value="">— choose a song —</option>
          <option v-for="s in songs" :key="s.id" :value="s.id">{{ s.title }} – {{ s.author }}</option>
        </select>
        <button class="btn-primary" :disabled="!manualSong" @click="setSong(manualSong)">Play now</button>
      </div>
    </div>

    <!-- Current song preview -->
    <div v-if="live.state.song" class="card" style="margin-top:20px">
      <h2>Now showing</h2>
      <div class="now-playing">
        <div class="np-title">{{ live.state.song.title }}</div>
        <div class="np-author text-muted">{{ live.state.song.author }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLiveStore } from '../stores/live'
import api from '../api'

const live = useLiveStore()
const setlists = ref([])
const songs = ref([])
const selectedSetlist = ref('')
const manualSong = ref('')

const songMap = computed(() => Object.fromEntries(songs.value.map(s => [s.id, s])))
const activeSetlist = computed(() => setlists.value.find(s => s.id === live.state.setlist_id))

onMounted(async () => {
  await live.fetchState()
  live.connect()
  const [s, sl] = await Promise.all([api.get('/api/songs'), api.get('/api/setlists')])
  songs.value = s.data
  setlists.value = sl.data
})

onUnmounted(() => live.disconnect())

async function startSetlist() {
  await api.post('/api/live/start', { setlist_id: selectedSetlist.value })
}

async function stop() {
  await api.post('/api/live/stop')
}

async function setSong(id) {
  await api.post('/api/live/song', { song_id: id })
}

async function next() {
  await api.post('/api/live/next')
}

async function prev() {
  await api.post('/api/live/prev')
}
</script>

<style scoped>
.setlist-songs { display: flex; flex-direction: column; gap: 4px; }

.setlist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.setlist-item:hover { background: var(--surface2); }
.setlist-item.active { border-color: var(--accent); background: rgba(232,160,69,0.08); }

.item-num { color: var(--text-muted); font-size: 13px; min-width: 20px; }
.item-title { font-weight: 600; flex: 1; }
.item-author { font-size: 13px; }
.item-badge { margin-left: auto; }

.now-playing { padding: 8px 0; }
.np-title { font-size: 22px; font-weight: 700; }
.np-author { font-size: 15px; margin-top: 4px; }
</style>
