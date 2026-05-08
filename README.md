# Live Song Book

> A real-time song lyrics display for campfire singalongs. The guitarist controls what's on screen; everyone else just opens the link on their phone and sings along.

---

## Features

- **Live public view** — displays the current song's lyrics and chords, updates instantly when the admin changes it
- **Chord transposition** — every viewer can shift chords up/down semitones on their own device
- **Admin dashboard** — manage the song library, build setlists, and control the live display
- **Setlist sequencer** — queue up songs for the night and step through them with prev/next
- **PDF downloads** — upload song sheet PDFs the audience can grab straight from the public page

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI + Pydantic |
| Frontend | Vue 3 + Vite + Pinia |
| Database | MongoDB |
| Real-time | Server-Sent Events (SSE) |
| Infra | Docker + Docker Compose |

## Getting started

**Prerequisites:** Docker and Docker Compose installed.

```bash
git clone <repo-url>
cd live_song_book

cp .env.example .env
# Edit .env — set SECRET_KEY and ADMIN_PASSWORD before running in production
```

```bash
make start      # build images and launch
```

The app is now running at `http://localhost`.

| URL | What it is |
|---|---|
| `http://localhost/` | Public song view (share this link with singers) |
| `http://localhost/admin` | Admin panel |

Default credentials (change in `.env`): `admin` / `admin123`

## Makefile commands

```
make start          build images and start all containers
make up             start without rebuilding
make down           stop containers
make build          build images
make rebuild        build images with no cache
make logs           follow all logs
make logs-backend   follow backend logs only
make restart        restart all services
make ps             show container status
make clean          stop and delete all volumes  ⚠ wipes the database
make shell-backend  open a shell inside the backend container
make shell-mongo    open mongosh on the database
```

## Song format

Songs are stored as plain text with inline chords. See [SONG_FORMAT.md](SONG_FORMAT.md) for the full guide. Quick example:

```
# Verse 1
[Am]I see trees of [F]green, [C]red roses too
[Am]I see them [F]bloom for [C]me and [G]you

# Chorus
[F]What a [C]wonderful [G7]world
```

## Configuration

All configuration is done through environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `changeme-...` | JWT signing secret — **change this** |
| `ADMIN_USERNAME` | `admin` | Admin login username |
| `ADMIN_PASSWORD` | `admin123` | Admin login password — **change this** |

## License

MIT
