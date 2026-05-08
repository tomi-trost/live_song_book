<template>
  <div class="page">
    <div class="flex items-center justify-between" style="margin-bottom:24px">
      <div>
        <h1>Song Sheet PDFs</h1>
        <p class="text-muted">Upload PDFs that audience members can download</p>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px">
      <h2>Upload PDF</h2>
      <div class="upload-area" @dragover.prevent @drop.prevent="onDrop">
        <input ref="fileInput" type="file" accept=".pdf" style="display:none" @change="onFile" />
        <button class="btn-secondary" @click="fileInput.click()">Choose PDF file</button>
        <p class="text-muted" style="margin-top:8px;font-size:13px">or drag & drop here</p>
      </div>
      <div v-if="uploading" class="text-muted" style="margin-top:12px;font-size:13px">Uploading…</div>
    </div>

    <div v-if="pdfs.length">
      <h2>Uploaded files</h2>
      <div class="pdf-list">
        <div v-for="pdf in pdfs" :key="pdf.name" class="pdf-row card">
          <div class="flex items-center gap-3">
            <span style="font-size:24px">📄</span>
            <div>
              <div class="pdf-name">{{ pdf.name }}</div>
              <a :href="pdf.url" target="_blank" class="text-muted" style="font-size:12px">Download ↗</a>
            </div>
          </div>
          <button class="btn-danger" @click="deletePdf(pdf.name)">Delete</button>
        </div>
      </div>
    </div>
    <div v-else class="text-muted" style="text-align:center;padding:40px">No PDFs uploaded yet.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const pdfs = ref([])
const uploading = ref(false)
const fileInput = ref(null)

onMounted(load)

async function load() {
  const { data } = await api.get('/api/pdf')
  pdfs.value = data
}

async function upload(file) {
  if (!file || !file.name.endsWith('.pdf')) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    await api.post('/api/pdf', fd)
    await load()
  } finally {
    uploading.value = false
  }
}

function onFile(e) { upload(e.target.files[0]) }
function onDrop(e) { upload(e.dataTransfer.files[0]) }

async function deletePdf(name) {
  await api.delete(`/api/pdf/${name}`)
  await load()
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  transition: border-color 0.15s;
}

.upload-area:hover { border-color: var(--accent); }

.pdf-list { display: flex; flex-direction: column; gap: 10px; }
.pdf-row { display: flex; align-items: center; justify-content: space-between; }
.pdf-name { font-weight: 600; font-size: 14px; }
</style>
