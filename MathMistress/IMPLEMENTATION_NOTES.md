# MathMistress — Implementation Notes

**Date:** 2026-09-06
**Scope:** Audit + delta vs `BLUEPRINT.md`.

## Status vs Blueprint

| BLUEPRINT goal | Met? | Notes |
|---|---|---|
| #1 Zero persistence | ✓ | No localStorage / cookies / backend. All state in memory. |
| #2 Minimal exposition + Help button | ✓ | `scripts/help.js` reveals one hint per click. |
| #3 Distraction-driven gameplay | ✓ | `scripts/npc.js` schedules Dionysus + Quetzalcoatl distractions. |
| #4 Rapid loop (<10 s to first interaction) | ✓ | Splash → Begin → first problem is a single click. |
| #5 Pure HTML5 / CSS / vanilla JS, no build | ✓ | ES modules, no bundler. |
| §2 Asset dirs `assets/img/`, `assets/audio/` | ✓ (this PR) | `dionysus.svg`, `quetzalcoatl.svg`, `ambient-loop.wav` (procedurally generated 2 s sine). |
| §3 Game loop state machine | ✓ | `core.js` evaluates → correct → next problem / incorrect → drain focus. |
| §3 FocusMeter 0-100, soft reset at 0 | ✓ | `drainFocus` clamps at 0 and ends the game. |
| §4 Progressive difficulty (basic → medium → hard → fractions) | partial | basic/medium/hard wired; fractions **deferred**. |
| §4 Fractions at higher levels | ✗ deferred | Out of scope for this PR; tracked as future work. |
| §4 `validateAnswer` strict equals | ✓ | No float comparison. |
| §5 NPC `class NPC` + `scheduleDistraction` | ✓ | Refactored to accept `spritePath` and pass `(name, phrase, sprite)` to callback. |
| §6 Help progressive reveal | ✓ | `hintFunctions` array, `hintPointer` walks through. |
| §7 Antique parchment + twilight purple | ✓ | `--accent` / `--ink` / `--parchment` in `main.css`. |
| §7 Cormorant Garamond + Roboto Mono | ✓ | Linked from Google Fonts in `index.html`. |
| §7 Ambient audio loop, mute toggle | ✓ (this PR) | `ambient-loop.wav` + mute button default-on. |

## This PR's changes

- **Quality gate:** ESLint clean (was 22 errors, now 0); `randomInt` extracted to `scripts/utils.js` (was duplicated in `mathEngine.js` and `npc.js`).
- **Test coverage:** 6 suites / 23 tests (was 3 / 6). Added suites for `utils.js`, `help.js`, `npc.js`, and shape-checking for `mathEngine.js`. New shape tests confirmed non-tautological via break-it check (stubbing `generateProblem` made 3 new tests fail).
- **Assets:** `assets/img/dionysus.svg`, `assets/img/quetzalcoatl.svg`, `assets/audio/ambient-loop.wav` (procedurally generated 2 s 220 Hz sine, 88 KB).
- **UI:** Mute toggle button in header, `<audio>` element wired up.
- **Real bug fixed:** `scripts/help.js` previously captured `document.getElementById('feedback')` at module load time. In ESM modules this ran before DOM ready, leaving `hintArea = null`. Refactored to a lazy `hintArea()` lookup so the module is robust regardless of script-load order.

## Deferred (out of scope)

- Python desktop build (`src/mathmistress/`).
- Fractions / advanced problem types.
- Difficulty progression beyond 3 levels.
- Localisation / i18n.
- Build step / bundler.
