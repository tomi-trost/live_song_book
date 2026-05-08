<template>
  <div class="song-display">
    <div class="song-header">
      <div class="song-title">{{ song.title }}</div>
      <div class="song-author">{{ song.author }}</div>
      <div class="transpose-bar">
        <button class="btn-ghost btn-icon" @click="shift(-1)" title="Transpose down">♭</button>
        <span class="transpose-label">{{ transposeLabel }}</span>
        <button class="btn-ghost btn-icon" @click="shift(1)" title="Transpose up">♯</button>
        <button class="btn-ghost" style="font-size:12px;padding:4px 8px" @click="semitones=0">reset</button>
      </div>
    </div>
    <div class="song-body">
      <div v-for="(block, i) in parsed" :key="i" :class="['song-block', block.type]">
        <div v-if="block.type === 'section'" class="section-label">{{ block.text }}</div>
        <div v-else-if="block.type === 'line'" class="chord-line">
          <span v-for="(chunk, j) in block.chunks" :key="j" class="chunk">
            <span v-if="chunk.chord" class="chord">{{ transposeChord(chunk.chord) }}</span>
            <span v-if="chunk.chord" class="chord-spacer"> </span>
            <span class="lyric">{{ chunk.lyric }}</span>
          </span>
        </div>
        <div v-else class="empty-line">&nbsp;</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ song: { type: Object, required: true } })

const semitones = ref(0)

const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
const FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
const ENHARMONIC = { 'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#' }

function noteIndex(note) {
  const normalized = ENHARMONIC[note] ?? note
  return NOTES.indexOf(normalized)
}

function transposeNote(note, n) {
  const idx = noteIndex(note)
  if (idx === -1) return note
  return NOTES[(idx + n + 12) % 12]
}

function transposeChord(chord) {
  if (!semitones.value) return chord
  // match root note (e.g. C, C#, Db, F#) + rest (e.g. m, maj7, sus4/G)
  return chord.replace(/([A-G][b#]?)/g, (match) => transposeNote(match, semitones.value))
}

function shift(n) {
  semitones.value = ((semitones.value + n + 12) % 12)
  if (semitones.value > 6) semitones.value -= 12
}

const transposeLabel = computed(() => {
  if (!semitones.value) return '±0'
  return semitones.value > 0 ? `+${semitones.value}` : `${semitones.value}`
})

const parsed = computed(() => {
  const lines = props.song.content.split('\n')
  const blocks = []
  let inBlockComment = false

  for (const line of lines) {
    const trimmed = line.trim()

    if (inBlockComment) {
      if (trimmed.includes('*/')) inBlockComment = false
      continue
    }
    if (trimmed.startsWith('/*')) { inBlockComment = true; continue }
    if (trimmed.startsWith('//')) continue
    if (trimmed.startsWith('%')) continue

    if (!trimmed) { blocks.push({ type: 'empty' }); continue }

    // Section header: # Verse 1
    if (trimmed.startsWith('#')) {
      blocks.push({ type: 'section', text: trimmed.replace(/^#+\s*/, '') })
      continue
    }

    // Inline chords: [C]word [G]other
    if (/\[[A-G][^\]]*\]/.test(trimmed)) {
      const chunks = []
      const firstChord = trimmed.search(/\[[A-G][^\]]*\]/)
      if (firstChord > 0) chunks.push({ chord: null, lyric: trimmed.slice(0, firstChord) })
      const re = /\[([A-G][^\]]*)\]([^\[]*)/g
      re.lastIndex = firstChord
      let match
      while ((match = re.exec(trimmed)) !== null) chunks.push({ chord: match[1], lyric: match[2] })
      blocks.push({ type: 'line', chunks })
      continue
    }

    blocks.push({ type: 'line', chunks: [{ chord: null, lyric: trimmed }] })
  }

  return blocks
})
</script>

<style scoped>
.song-display { padding: 4px 0; }

.song-header { margin-bottom: 24px; }
.song-title { font-size: clamp(22px, 5vw, 36px); font-weight: 800; line-height: 1.2; }
.song-author { color: var(--text-muted); font-size: 15px; margin-top: 4px; }

.transpose-bar {
  display: flex; align-items: center; gap: 4px;
  margin-top: 14px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 4px 8px;
  width: fit-content;
}
.transpose-label { font-size: 13px; font-weight: 700; min-width: 28px; text-align: center; color: var(--accent); }

.song-body { display: flex; flex-direction: column; gap: 2px; }

.section-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--accent);
  margin-top: 20px;
  margin-bottom: 6px;
}

.chord-line {
  display: flex;
  flex-wrap: wrap;
  font-family: var(--font-mono);
  font-size: clamp(14px, 3.5vw, 18px);
  line-height: 1;
}

.chunk {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  margin-right: 2px;
  margin-bottom: 8px;
}

.chord {
  color: var(--chord);
  font-weight: 700;
  font-size: clamp(12px, 3vw, 15px);
  min-height: 18px;
  white-space: nowrap;
}

.lyric { white-space: pre; }
.chord-spacer { display: none; }

.empty-line { height: 12px; }
</style>
