<template>
  <div class="page">
    <div class="flex items-center justify-between" style="margin-bottom:24px">
      <div>
        <h1>Setlists</h1>
        <p class="text-muted">Plan your song sequences for the night</p>
      </div>
      <button class="btn-primary" @click="openCreate">+ New setlist</button>
    </div>

    <div class="setlist-grid">
      <div v-for="sl in setlists" :key="sl.id" class="card setlist-card">
        <div class="sl-header">
          <div>
            <div class="sl-name">{{ sl.name }}</div>
            <div class="text-muted" style="font-size:12px">{{ sl.song_ids.length }} songs</div>
          </div>
          <div class="flex gap-2">
            <button class="btn-secondary" @click="openEdit(sl)">Edit</button>
            <button class="btn-danger btn-icon" @click="confirmDelete(sl)">✕</button>
          </div>
        </div>
        <div class="sl-songs">
          <div v-for="(id, i) in sl.song_ids" :key="id" class="sl-song">
            <span class="sl-num">{{ i + 1 }}.</span>
            <span>{{ songMap[id]?.title ?? id }}</span>
            <span class="text-muted" style="font-size:12px">{{ songMap[id]?.author }}</span>
          </div>
          <div v-if="!sl.song_ids.length" class="text-muted" style="font-size:13px;padding:8px 0">No songs yet</div>
        </div>
      </div>
      <div v-if="!setlists.length" class="text-muted" style="text-align:center;padding:40px">No setlists yet.</div>
    </div>

    <!-- Create / Edit modal -->
    <div v-if="modal.open" class="modal-overlay" @click.self="modal.open=false">
      <div class="modal">
        <div class="modal-title">{{ modal.editing ? 'Edit setlist' : 'New setlist' }}</div>
        <div class="field">
          <label>Setlist name</label>
          <input v-model="form.name" placeholder="e.g. Camp Night 1" />
        </div>
        <div class="field">
          <label>Add songs (pick from library)</label>
          <select @change="addSong($event.target.value); $event.target.value=''">
            <option value="">— add a song —</option>
            <option v-for="s in availableSongs" :key="s.id" :value="s.id">
              {{ s.title }} – {{ s.author }}
            </option>
          </select>
        </div>
        <div class="sl-edit-songs">
          <div v-for="(id, i) in form.song_ids" :key="id" class="sl-edit-row">
            <span class="sl-num">{{ i + 1 }}</span>
            <span class="flex-1">{{ songMap[id]?.title }}</span>
            <button class="btn-ghost btn-icon" :disabled="i === 0" @click="moveUp(i)">↑</button>
            <button class="btn-ghost btn-icon" :disabled="i === form.song_ids.length-1" @click="moveDown(i)">↓</button>
            <button class="btn-ghost btn-icon" style="color:var(--danger)" @click="removeSong(i)">✕</button>
          </div>
          <div v-if="!form.song_ids.length" class="text-muted" style="font-size:13px;padding:8px 0">No songs added yet</div>
        </div>
        <div class="flex justify-end gap-2" style="margin-top:20px">
          <button class="btn-secondary" @click="modal.open=false">Cancel</button>
          <button class="btn-primary" :disabled="!form.name || saving" @click="save">
            {{ saving ? 'Saving…' : (modal.editing ? 'Save' : 'Create') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget=null">
      <div class="modal">
        <div class="modal-title">Delete "{{ deleteTarget.name }}"?</div>
        <p class="text-muted" style="margin-bottom:24px">This cannot be undone.</p>
        <div class="flex justify-end gap-2">
          <button class="btn-secondary" @click="deleteTarget=null">Cancel</button>
          <button class="btn-danger" @click="deleteSetlist">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const setlists = ref([])
const songs = ref([])
const saving = ref(false)
const deleteTarget = ref(null)

const modal = ref({ open: false, editing: false, id: null })
const form = ref({ name: '', song_ids: [] })

const songMap = computed(() => Object.fromEntries(songs.value.map(s => [s.id, s])))
const availableSongs = computed(() => songs.value.filter(s => !form.value.song_ids.includes(s.id)))

onMounted(async () => {
  const [sl, sg] = await Promise.all([api.get('/api/setlists'), api.get('/api/songs')])
  setlists.value = sl.data
  songs.value = sg.data
})

function openCreate() {
  form.value = { name: '', song_ids: [] }
  modal.value = { open: true, editing: false, id: null }
}

function openEdit(sl) {
  form.value = { name: sl.name, song_ids: [...sl.song_ids] }
  modal.value = { open: true, editing: true, id: sl.id }
}

function addSong(id) {
  if (id && !form.value.song_ids.includes(id)) form.value.song_ids.push(id)
}

function removeSong(i) {
  form.value.song_ids.splice(i, 1)
}

function moveUp(i) {
  if (i === 0) return
  const ids = form.value.song_ids
  ;[ids[i - 1], ids[i]] = [ids[i], ids[i - 1]]
}

function moveDown(i) {
  const ids = form.value.song_ids
  if (i >= ids.length - 1) return
  ;[ids[i], ids[i + 1]] = [ids[i + 1], ids[i]]
}

async function save() {
  saving.value = true
  try {
    if (modal.value.editing) {
      await api.patch(`/api/setlists/${modal.value.id}`, form.value)
    } else {
      await api.post('/api/setlists', form.value)
    }
    modal.value.open = false
    const { data } = await api.get('/api/setlists')
    setlists.value = data
  } finally {
    saving.value = false
  }
}

function confirmDelete(sl) { deleteTarget.value = sl }

async function deleteSetlist() {
  await api.delete(`/api/setlists/${deleteTarget.value.id}`)
  deleteTarget.value = null
  const { data } = await api.get('/api/setlists')
  setlists.value = data
}
</script>

<style scoped>
.setlist-grid { display: flex; flex-direction: column; gap: 16px; }

.setlist-card { padding: 16px 20px; }

.sl-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.sl-name { font-size: 17px; font-weight: 700; }

.sl-songs { display: flex; flex-direction: column; gap: 4px; border-top: 1px solid var(--border); padding-top: 10px; }
.sl-song { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.sl-num { color: var(--text-muted); min-width: 20px; font-size: 12px; }

.sl-edit-songs { display: flex; flex-direction: column; gap: 4px; margin-top: 8px; max-height: 280px; overflow-y: auto; }
.sl-edit-row { display: flex; align-items: center; gap-8px; gap: 6px; padding: 6px 8px; background: var(--surface2); border-radius: 6px; font-size: 14px; }
</style>
