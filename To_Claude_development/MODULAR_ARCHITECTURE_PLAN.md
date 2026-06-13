# Albot — Modular Architecture Plan

## Goal
Make it easy to add new self-contained features (like a chess game) without touching
existing bot code. Each feature should also be runnable and testable on its own,
without needing a live Twitch stream.

---

## The Core Problem Today

`AlbotBrain` creates every component, holds references to all of them, and wires them
together with 20+ manual `set_x()` calls in every direction. Adding anything new means
touching `AlbotBrain`, `Command_central`, `overlay_runner`, and threading the new thing
through the existing connections. It's fragile and gets harder every time.

---

## The Five Changes

### 1. Event Bus
**What:** A single central "message board" that all parts of the bot talk through.
Instead of components calling each other directly, they post events ("a chat message
arrived", "play a gif") and subscribe to the events they care about.

**Why:** A new module just subscribes to the events it needs. No wiring into existing
files required. `AlbotBrain` stops being a wiring harness.

---

### 2. Module Interface
**What:** A simple base class that every feature implements. It has four methods:
- `on_load()` — runs at startup
- `on_chat_message(user, message)` — called for every chat message
- `on_command(user, command, params)` — called when a `%command` is used
- `on_unload()` — runs at shutdown

**Why:** The bot core loads a list of modules and routes events to them. Each module is
responsible for its own logic and nothing else. Adding chess means creating one new file
that implements these four methods — no changes to anything existing.

---

### 3. Per-Module Windows
**What:** Modules that need a visual (like chess) create and manage their own window
internally. The bot core does not own or know about module windows.

**Why:** Currently everything shares one overlay window, which creates dependencies.
A module with its own window can be opened, tested, and closed independently.

---

### 4. Fake Twitch Source for Testing
**What:** A simple stand-in for the real Twitch connection that lets you type chat
messages from the keyboard (or a local file) and fire them into the bot as if they
came from real viewers.

**Why:** You can develop and test any module completely offline, without running a
stream. Essential for testing chess moves, command responses, or any new feature.

---

### 5. Dead Code Cleanup
**What:** Remove the large blocks of commented-out code in `overlay_runner.py`,
`TwitchConnection.py`, and `AlbotBrain.py` (old shout-out logic, old overlay routing,
old queue experiments).

**Why:** The files are hard to read, and old code can accidentally get "resurrected".
Low risk, can be done at any time.

---

## New Folder Structure

```
.\core\         — Twitch connection, event bus, module loader (bot plumbing)
.\modules\      — One folder per feature: greetings, chess, polls, etc.
```

Each module folder is self-contained: its own logic, its own window if needed, its own
test script.

---

## Suggested Order of Work

| Step | What | Why first |
|------|------|-----------|
| 1 | Event bus | Enables everything else |
| 2 | Module interface + loader | Move greetings into a proper module immediately |
| 3 | Per-module windows | Needed for chess and future visual features |
| 4 | Fake Twitch source | Makes development much faster |
| 5 | Dead code cleanup | Low risk, do anytime |

---

## End State

Adding a chess module means: create `modules/chess/chess_module.py`, implement the
four module methods, open its own window in `on_load()`, respond to `%chess` in
`on_command()`. No changes to any existing file needed.
