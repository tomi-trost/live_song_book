<template>
  <div class="page">
    <div class="flex items-center justify-between" style="margin-bottom:24px">
      <div>
        <h1>Songs</h1>
        <p class="text-muted">{{ songs.length }} song{{ songs.length !== 1 ? 's' : '' }} in the library</p>
      </div>
      <div class="flex gap-2">
        <button class="btn-secondary" @click="triggerImport">Import JSON</button>
        <button class="btn-primary" @click="openCreate">+ Add song</button>
      </div>
      <input ref="importInput" type="file" accept=".json" style="display:none" @change="handleImport" />
    </div>

    <div v-if="importResult" :class="['import-banner', importResult.type]">
      <div>{{ importResult.message }}</div>
      <ul v-if="importResult.errors && importResult.errors.length" class="import-errors">
        <li v-for="e in importResult.errors.slice(0, 10)" :key="e.index + e.error">
          Song {{ e.index + 1 }}: {{ e.error }}
        </li>
        <li v-if="importResult.errors.length > 10" class="text-muted">
          … and {{ importResult.errors.length - 10 }} more error(s)
        </li>
      </ul>
      <button class="import-close" @click="importResult = null">✕</button>
    </div>

    <div class="search-bar">
      <input v-model="search" placeholder="Search by title or author…" />
    </div>

    <div class="song-list">
      <div v-for="song in filtered" :key="song.id" class="song-row card">
        <div class="song-info">
          <div class="song-name">{{ song.title }}</div>
          <div class="song-auth text-muted">{{ song.author }}</div>
        </div>
        <div class="flex gap-2">
          <button class="btn-secondary" @click="openEdit(song)">Edit</button>
          <button class="btn-danger" @click="confirmDelete(song)">Delete</button>
        </div>
      </div>
      <div v-if="!filtered.length" class="empty-state text-muted">No songs found.</div>
    </div>

    <!-- Create / Edit modal -->
    <div v-if="modal.open" class="modal-overlay" @click.self="modal.open=false">
      <div class="modal">
        <div class="modal-title">{{ modal.editing ? 'Edit song' : 'Add new song' }}</div>
        <form @submit.prevent="save">
          <div class="field">
            <label>Title</label>
            <input v-model="form.title" required placeholder="Song title" />
          </div>
          <div class="field">
            <label>Author / Artist</label>
            <input v-model="form.author" required placeholder="e.g. Bob Dylan" />
          </div>
          <div class="field">
            <label>Lyrics & chords (tabdown format)</label>
            <textarea v-model="form.content" rows="16" placeholder="[Verse 1]&#10;[C]Amazing [G]grace how [Am]sweet the [F]sound&#10;[C]That saved a [G]wretch like [C]me" required></textarea>
            <p class="text-muted" style="margin-top:4px;font-size:12px">Wrap chord names in brackets: [C], [Am], [F#m7]. Section headers: [Verse 1], [Chorus].</p>
          </div>
          <div class="flex justify-end gap-2">
            <button type="button" class="btn-secondary" @click="modal.open=false">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving…' : (modal.editing ? 'Save changes' : 'Add song') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget=null">
      <div class="modal">
        <div class="modal-title">Delete "{{ deleteTarget.title }}"?</div>
        <p class="text-muted" style="margin-bottom:24px">This cannot be undone.</p>
        <div class="flex justify-end gap-2">
          <button class="btn-secondary" @click="deleteTarget=null">Cancel</button>
          <button class="btn-danger" @click="deleteSong">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const songs = ref([])
const search = ref('')
const saving = ref(false)
const deleteTarget = ref(null)
const importInput = ref(null)
const importResult = ref(null)

const modal = ref({ open: false, editing: false, id: null })
const form = ref({ title: '', author: '', content: '' })

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return songs.value.filter(s =>
    s.title.toLowerCase().includes(q) || s.author.toLowerCase().includes(q)
  )
})

onMounted(load)

async function load() {
  const { data } = await api.get('/api/songs')
  songs.value = data
}

function openCreate() {
  form.value = { title: '', author: '', content: '' }
  modal.value = { open: true, editing: false, id: null }
}

function openEdit(song) {
  form.value = { title: song.title, author: song.author, content: song.content }
  modal.value = { open: true, editing: true, id: song.id }
}

async function save() {
  saving.value = true
  try {
    if (modal.value.editing) {
      await api.patch(`/api/songs/${modal.value.id}`, form.value)
    } else {
      await api.post('/api/songs', form.value)
    }
    modal.value.open = false
    await load()
  } finally {
    saving.value = false
  }
}

function triggerImport() {
  importResult.value = null
  importInput.value.click()
}

async function handleImport(event) {
  const file = event.target.files[0]
  if (!file) return
  event.target.value = ''

  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await api.post('/api/songs/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    importResult.value = { type: 'success', message: `Successfully imported ${data.imported} song(s).` }
    await load()
  } catch (err) {
    const detail = err.response?.data?.detail
    if (detail && typeof detail === 'object' && detail.errors) {
      importResult.value = { type: 'error', message: detail.message || 'Import failed.', errors: detail.errors }
    } else {
      importResult.value = { type: 'error', message: typeof detail === 'string' ? detail : 'Import failed. Check the file and try again.' }
    }
  }
}

function confirmDelete(song) {
  deleteTarget.value = song
}

async function deleteSong() {
  await api.delete(`/api/songs/${deleteTarget.value.id}`)
  deleteTarget.value = null
  await load()
}
</script>

<style scoped>
.search-bar { margin-bottom: 16px; }
.song-list { display: flex; flex-direction: column; gap: 10px; }
.song-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.song-name { font-weight: 600; }
.song-auth { font-size: 13px; margin-top: 2px; }
.empty-state { text-align: center; padding: 40px; }
.import-banner {
  position: relative;
  padding: 12px 40px 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}
.import-banner.success { background: #d1fae5; color: #065f46; }
.import-banner.error { background: #fee2e2; color: #991b1b; }
.import-errors { margin: 6px 0 0 16px; padding: 0; list-style: disc; }
.import-errors li { margin-top: 2px; }
.import-close {
  position: absolute;
  top: 10px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  opacity: 0.6;
}
.import-close:hover { opacity: 1; }
</style>
