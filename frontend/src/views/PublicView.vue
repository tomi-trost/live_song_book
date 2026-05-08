<template>
  <div class="public-root">
    <header class="pub-header">
      <div class="pub-header-inner">
        <div class="pub-title">🎵 Live Song Book</div>
        <div v-if="live.state.is_active" class="badge badge-live">LIVE</div>
        <div v-else class="badge badge-off">Offline</div>
      </div>
    </header>

    <main class="page">
      <div v-if="!live.state.is_active" class="idle-state">
        <div class="idle-icon">🔥</div>
        <h2>Nothing playing yet</h2>
        <p class="text-muted">The admin will start the show soon. Stay tuned!</p>
      </div>

      <SongDisplay v-else-if="live.state.song" :song="live.state.song" />

      <div v-else class="idle-state">
        <div class="idle-icon">🎸</div>
        <p class="text-muted">Waiting for the first song…</p>
      </div>

      <div v-if="pdfs.length" class="pdf-section">
        <hr class="divider" />
        <h3 class="text-muted" style="margin-bottom:12px">Song sheets for tonight</h3>
        <div class="pdf-list">
          <a v-for="pdf in pdfs" :key="pdf.name" :href="pdf.url" target="_blank" class="pdf-link">
            <span>📄</span> {{ pdf.name }}
          </a>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useLiveStore } from '../stores/live'
import SongDisplay from '../components/SongDisplay.vue'
import api from '../api'

const live = useLiveStore()
const pdfs = ref([])

onMounted(async () => {
  await live.fetchState()
  live.connect()
  try {
    const { data } = await api.get('/api/pdf')
    pdfs.value = data
  } catch {}
})

onUnmounted(() => live.disconnect())
</script>

<style scoped>
.public-root { min-height: 100dvh; }

.pub-header {
  position: sticky; top: 0;
  background: rgba(15,15,15,0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  z-index: 10;
  padding: 12px 16px;
}

.pub-header-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pub-title { font-weight: 700; font-size: 18px; }

.idle-state {
  text-align: center;
  padding: 80px 0;
}

.idle-icon { font-size: 64px; margin-bottom: 16px; }
.idle-state h2 { font-size: 22px; margin-bottom: 8px; }

.pdf-section { margin-top: 24px; }

.pdf-list { display: flex; flex-direction: column; gap: 8px; }

.pdf-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  transition: border-color 0.15s;
}

.pdf-link:hover { border-color: var(--accent); }
</style>
