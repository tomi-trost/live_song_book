# Song Format Guide

Songs are stored as plain text using a simplified subset of the [Tabdown](https://github.com/ultimate-guitar/Tabdown) format. This document describes exactly what is supported and how to enter songs correctly.

---

## Section headers

Start a line with `#` followed by the section name. This creates a coloured label above that part of the song.

```
# Verse 1
# Chorus
# Bridge
# Outro
```

---

## Chords with lyrics (inline style)

Place chord names in square brackets directly in front of the syllable where the chord changes. Chords and lyrics live **on the same line** — there is no separate chord line above the lyrics.

```
# Verse 1
[C]Amazing [G]grace how [Am]sweet the [F]sound
[C]That saved a [G]wretch like [C]me

# Chorus
[F]Through many [C]dangers [G]toils and [Am]snares
[F]I have al[C]ready [G]come
```

Rules:
- Chord names follow standard notation: `C`, `Am`, `F#`, `Bb`, `Dm7`, `G/B`, `Cadd9`, etc.
- A chord placed at the start of a line with no lyric text is fine — it will show the chord alone.
- Leave an **empty line** between sections for visual breathing room.

---

## Lines without chords

Plain lines (no brackets) are rendered as lyrics only. Useful for spoken lines, repeated choruses noted as text, or instrumental breaks.

```
# Intro
(instrumental)

# Verse 1
[G]Here we go...
```

---

## Comments (stripped from display)

Lines starting with `//` are ignored entirely — useful for personal notes while editing.

```
// Capo 2 sounds better here
[C]Amazing [G]grace...
```

Multi-line comments between `/*` and `*/` are also stripped:

```
/*
  Original key: D
  Easier to play in C with capo 2
*/
# Verse 1
[C]Amazing [G]grace...
```

---

## Metadata (stripped from display)

Lines starting with `%` are ignored. You can include Tabdown metadata for your own reference — it will not appear to the audience.

```
% capo: 2
% tuning: E A D G B E
```

---

## Full example

```
% capo: 0

# Verse 1
[Am]I see trees of [F]green, [C]red roses too
[Am]I see them [F]bloom for [C]me and [G]you
[F]And I think to my[C]self
[F]What a wonderful [C]world [G7]

# Chorus
// Slow down here
[C]What a [G7]wonderful [C]world
```

---

## What is NOT supported

The following Tabdown features are intentionally not parsed and will be displayed as plain text if used:

| Feature | Tabdown syntax | Status |
|---|---|---|
| Chord variations | `[G7b13]: 3x344x` | Not parsed |
| Inline fingering | `[Dm](x-x-10-9-8-10)` | Chord name extracted, fingering ignored |
| Reference links | `[F][2]` / `[2]: 1x323x` | Displayed as-is |
| Above-lyric chord lines | Separate chord/lyric lines | Use inline style instead |

---

## Batch JSON import

Instead of adding songs one by one through the admin panel, you can upload a `.json` file containing multiple songs at once using the **Import JSON** button on the Songs page.

### File format

The file must be a JSON array where each element is an object with exactly these three fields:

| Field | Type | Description |
|---|---|---|
| `title` | string | Song title |
| `author` | string | Artist or band name |
| `content` | string | Song lyrics and chords in the tabdown format described above |

All three fields are required and must not be empty. Any extra fields in the object are silently ignored.

Use `\n` for newlines inside the `content` string (standard JSON string encoding).

### Example

```json
[
  {
    "title": "Wonderful World",
    "author": "Louis Armstrong",
    "content": "# Verse 1\n[Am]I see trees of [F]green, [C]red roses too\n[Am]I see them [F]bloom for [C]me and [G]you\n\n# Chorus\n[C]What a [G7]wonderful [C]world"
  },
  {
    "title": "Another Song",
    "author": "Some Artist",
    "content": "# Verse 1\n[G]Line one\n[Em]Line two"
  }
]
```

An example import file with five original songs is provided in `example_songs.json` at the root of the repository.

### Error handling

If the file cannot be parsed (invalid JSON), a required field is missing, or a field has the wrong type, the import is aborted entirely and the admin panel will display a list of errors pointing to the problematic song(s) by position. No songs are inserted on failure.

---

## Tips

- Copy-paste from Ultimate Guitar or similar sites works if you convert their above-lyric chord lines to inline style.
- The audience can transpose chords up/down on their own device — enter the song in whatever key is comfortable to read.
- Section headers render in a distinct colour so audiences can navigate long songs at a glance.
