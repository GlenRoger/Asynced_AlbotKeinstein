# Albot Dashboard — Plan & Design Notes

## Purpose
A simple web-based dashboard to let non-programmers start, monitor, and manage the bot
without touching code, log files, or CSV files.

## Communication: Dashboard ↔ Bot
All communication goes through the **database** — the bot writes state/events, 
the dashboard reads them. Actions triggered from the dashboard (like refresh) are 
written to `Dashboard_cmd_register`, and the bot polls that table and acts on them.

> **Gap to address first:** Gif and greeting data currently live in CSV files
> (`known_gifs.csv` and `subs_greetings.csv`). For the dashboard to display and
> manage these properly, they need to be migrated into database tables.
> The bot can still load from CSV on startup, but the database becomes the source
> of truth going forward.

---

## Tabs / Sections

### 1. Status (Home tab)
- Green/yellow/red indicators: Twitch connection, OBS/overlay connection, database
- Token health: both tokens (bot + broadcaster), expiration in plain language,
  warning if expired or expiring within 3 days, link to get new token
- Recent errors: pulled from `Errors_register`, plain-language descriptions,
  severity color-coded

### 2. Live Activity
- Scrolling feed of what's happening this session (from `Info_register`)
- Human-readable: "CoolViewer joined → greeting gif played", "Command %greetings used"
- Errors stand out visually

### 3. Gifs & Greetings
- List of all viewers with a custom greeting gif assigned
- Shows: Twitch name, gif name, sound (if any)
- **Refresh Greetings button** — writes to `Dashboard_cmd_register`, bot picks it up
- **Refresh Gifs button** — same mechanism
- Future: Add / Edit / Delete a greeting directly from this tab (replaces editing the CSV)
- Future: Gif preview thumbnail before assigning

### 4. Session Summary
- Unique viewers seen this session
- How many greetings were played
- Which commands were used and how often
- Resets each stream start

### 5. Commands (future tab)
- View all active commands and who can use them (from the command CSV files / later a DB table)
- Enable / disable a command without touching files
- Edit the response text of a command

---

## Quick Actions (available on all tabs or in a toolbar)
- **Refresh Gifs** — triggers bot to reload known_gifs
- **Refresh Greetings** — triggers bot to reload subs_greetings
- **Silence / Un-silence bot** — toggles bot responses in chat
- **Restart bot** — graceful shutdown and restart
- All actions go via `Dashboard_cmd_register`

---

## Existing DB Tables Used
| Table | Used for |
|---|---|
| `Errors_register` | Error feed, status panel |
| `Tokens_register` | Token health display |
| `Info_register` | Live activity feed, session summary |
| `Dashboard_cmd_register` | Dashboard → Bot action triggers |

## New DB Tables Needed
| Table | Used for |
|---|---|
| `Gif_register` | Replace known_gifs.csv |
| `Greetings_register` | Replace subs_greetings.csv |

---

## Design Principles
- No raw Python errors or log prefixes visible to the user
- Every message tells the person *what happened* and *what to do*
- Buttons replace chat commands for routine maintenance tasks
- Dashboard is read-only to the bot's core logic — all triggers go via DB table
