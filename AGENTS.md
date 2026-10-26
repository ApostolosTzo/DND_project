<!-- GENERATED FILE - do not edit. Run: py tools/gen_agents_md.py -->
# AGENTS.md

This file is **generated** by `py tools/gen_agents_md.py`. Edit that script,
not this file; `py tools/check_docs.py` fails when it is stale.

## Invariants

This repo ships **one game in two builds**, and they must behave identically:

| Build | Entry point | UI |
|---|---|---|
| Flask (Python) | `py run_server.py` | `templates/index.html` |
| PWA (static, ships on Cloudflare Pages) | any static server on the repo root | root `index.html` + `js/*.js` |

- **Data lives once, in Python.** `items.py`, `shop.py`, `enemy.py`,
  `player.py` and `world_map.py` own every catalogue, shop, monster, race,
  class and map number. After changing any of that data, regenerate:

  ```bash
  py tools/gen_js_data.py     # rewrites js/game_data.js
  ```

  Never hand-edit `js/game_data.js` - it is generated and the freshness check
  overwrites-fails you. Data edits stop there; `js/*.js` picks the data up
  through `GAME_DATA` aliases.

- **Behaviour lives twice.** Combat, equipping, element riders, quests and
  saves are hand-written in *both* `*.py` and `js/*.js`. After any logic
  change, all three suites must be green or nothing ships:

  ```bash
  py tools/parity_check.py    # game_data freshness + cross-build logic parity
  node tools/js_suite.js      # PWA behaviour
  py tools/flask_suite.py     # Flask behaviour
  ```

  The suites freeze the RNG to one shared formula
  (`floor(r * (max - min + 1)) + min`), so runs are deterministic and every
  failure reproduces exactly. 0.999999 rolls all-max, 0.5 rolls mid.

- **The UI is one design and one page script, assembled twice.** Both HTML
  shells are generated from `tools/shells/` by:

  ```bash
  py tools/gen_html_shells.py         # rewrite both shells
  py tools/gen_html_shells.py --check # exit 1 when either shell is stale
  ```

  | Source | Role |
  |---|---|
  | `tools/shells/codex.css` | the codex design - embedded verbatim in BOTH shells |
  | `tools/shells/shared_page.js` | every render, panel and keyboard handler - one page script for both builds |
  | `tools/shells/pwa_adapter.js` | the `Backend` seam for the PWA (wraps `Game.*`, the live catalogue, localStorage) |
  | `tools/shells/flask_adapter.js` | the `Backend` seam for Flask (fetch/POST to the routes) |

  Never hand-edit `index.html` or `templates/index.html` - edit the source and
  regenerate. Both adapters must implement the same `Backend` members
  (`init`, `getState`, `action`, ..., `sellRows`, `equipRefusal`,
  `consumeDamage`); a missing member throws on first paint. The sources are
  inlined (not linked) so the precached `index.html` stays self-contained and
  the PWA keeps working offline. `py tools/check_docs.py` runs the `--check`.

- **Bump `CACHE_VERSION` in `sw.js` after any change to `js/*.js`, the root
  `index.html`, or anything in `tools/shells/`** - all of them end up inside
  the precached `index.html`, cache-first by the service worker, so without a
  bump returning players keep the old code after deploy. `_headers` keeps
  `sw.js` and `index.html` off the CDN cache for the same reason.

- **Rounding is a parity trap.** Python `round()` is half-even, JS
  `Math.round()` is half-up. Shared formulas round half-up
  (`int(x + 0.5)` in Python) and are pinned by suites on both sides.

- **Equipment numbers feed the maths.** `stats_bonus` on weapons and armour
  (Longsword STR+1, Ember Blade INT+1, Chainmail `dex_limit` 2) changes AC,
  to-hit and damage. Hand-computed expectations must include them.

- **Docs are UTF-8.** Edit `PROGRESS.md` / `README.md` / `GAME_GUIDE.md`
  through a Python script writing UTF-8 (the edit tool mangles em-dashes), use
  the `py` launcher, never redirect node stdout with PowerShell `>` (it writes
  UTF-16), and keep scratch files in `%TEMP%\opencode`.

- **`GAME_GUIDE.md` regenerates only when catalogue data changed:**
  `py tools/gen_game_guide.py`, then `py tools/audit_guide.py`.

- **`PROGRESS.md` is the changelog.** Document every meaningful change there;
  phrase recurring discoveries as `> **Lesson:**` blockquotes - the Lessons
  section below is mined from them.

## Running the two builds

| Build | Command | URL |
|---|---|---|
| Flask | `py run_server.py` | http://127.0.0.1:5000 |
| PWA | `py -m http.server 8734` (any static server) | http://127.0.0.1:8734 |

## File map

Descriptions live in `DESC` in `tools/gen_agents_md.py`; a file without
a description (or a description without a file) fails generation.

| File | Role |
|---|---|
| `combat.py` | Terminal combat loop - not on the Flask or PWA path any more (nothing imports it). |
| `dice.py` | Dice roller (`NdX+Y`, 4d6-drop-lowest); shared by creation and combat. |
| `enemy.py` | Enemy class: generation/scaling, damage types, element riders, drops; `apply_damage` rounds half-up. |
| `game_server.py` | The Flask build: routes, screen state machine, every action handler. |
| `inventory.py` | Terminal inventory screen - only reachable from `combat.py`. |
| `items.py` | The catalogue (weapons/armour/potions/quest items) - single source of truth for game data. |
| `player.py` | Player class: stats, HP/AC formulas, equipment and off-hand rules, levelling. |
| `quests.py` | Quest definitions and quest hub logic (hand-written twice, never generated). |
| `run_server.py` | Launcher: `py run_server.py` starts Flask on port 5000. |
| `save_load.py` | Multi-save JSON system; `SAVES_DIR` is redirected to a temp dir by flask_suite. |
| `shop.py` | Shop NPC stock and prices, selling at 80% (half-up rounding). |
| `ui.py` | Terminal-only helpers (arrow-key menu, screen clears); imports `msvcrt`. |
| `world_map.py` | Location graph, coordinates and connections - generated into `GAME_DATA`. |
| `_headers` | Cloudflare Pages cache headers: `sw.js`/`index.html` no-cache, `js/*` must-revalidate. |
| `index.html` | **GENERATED** by `tools/gen_html_shells.py` - the PWA shell (codex CSS + shared page script inlined, PWA adapter); loads `js/*.js` in order. |
| `manifest.json` | PWA manifest (name, icons, standalone display). |
| `sw.js` | Service worker: precache list + `CACHE_VERSION` (bump after `js/*.js`, `index.html`, or `tools/shells/` changes). |
| `templates/index.html` | **GENERATED** by `tools/gen_html_shells.py` - the Flask shell (same codex CSS + shared page script inlined, Flask adapter). |
| `js/dice.js` | Dice rolling; mirrors `dice.py`. |
| `js/enemy.js` | Enemy logic, damage types, element riders, drops; data from `GAME_DATA`. |
| `js/game.js` | PWA state machine - mirrors `game_server.py` routes and handlers. |
| `js/game_data.js` | **GENERATED** by `tools/gen_js_data.py` - never hand-edit. |
| `js/items.js` | Item classes and catalogue helpers; data from `GAME_DATA`. |
| `js/player.js` | Player logic (stats, AC, off-hand rules); data from `GAME_DATA`. |
| `js/quests.js` | Quests - hand-written (quests are deliberately not generated). |
| `js/saves.js` | localStorage multi-save; mirrors `save_load.py`. |
| `js/shop.js` | Shop stock, buy/sell logic; data from `GAME_DATA`. |
| `js/world_map.js` | Map helpers; data from `GAME_DATA`. |
| `tools/audit_guide.py` | Verifies `GAME_GUIDE.md` still matches the catalogue. |
| `tools/check_docs.py` | Fails (exit 1) when a generated doc (AGENTS.md) or either HTML shell is stale. |
| `tools/flask_suite.py` | Flask behavioural suite - drives the real routes through the test client. |
| `tools/gen_agents_md.py` | Writes AGENTS.md (this file's generator). |
| `tools/gen_game_guide.py` | Regenerates `GAME_GUIDE.md` from the catalogue (catalogue changes only). |
| `tools/gen_html_shells.py` | Assembles both HTML shells from `tools/shells/` (`--check` fails when stale). |
| `tools/gen_js_data.py` | Regenerates `js/game_data.js` from the Python modules (any data change). |
| `tools/harness.js` | vm-based loader that runs `js/*.js` headlessly with a settable RNG. |
| `tools/js_probe.js` | JS half of parity_check: runs the shared logic over the case grid, prints JSON. |
| `tools/js_suite.js` | PWA behavioural suite (create/shop/fight/riders/potions/saves). |
| `tools/parity_check.py` | Freshness of `game_data.js` + cross-build logic parity across 11 groups. |
| `tools/shells/codex.css` | The codex design - embedded verbatim in BOTH shells. |
| `tools/shells/flask_adapter.js` | The `Backend` seam for Flask (fetch/POST to the routes). |
| `tools/shells/pwa_adapter.js` | The `Backend` seam for the PWA (wraps `Game.*`, catalogue, localStorage). |
| `tools/shells/shared_page.js` | The one page script: every render, panel and keyboard handler for both builds. |
| `AGENTS.md` | **GENERATED** by this script - edit `tools/gen_agents_md.py`, not the file. |
| `GAME_GUIDE.md` | **GENERATED** player guide - regenerate only when the catalogue changes. |
| `PROGRESS.md` | Running changelog; its `> **Lesson:**` blockquotes feed this file. |
| `README.md` | User-facing docs: why two builds, how to run, deploy, editing rules. |

## Lessons mined from PROGRESS.md

Every `> **Lesson:**` blockquote in the changelog lands here on regen.

- **Single-Sourced Data & Permanent Test Suites (Pass 1)** - a generated file is an interface, not a copy - edit its input, never its output, and keep a freshness check that fails loudly when someone forgets to regen.
- **Single-Sourced Data & Permanent Test Suites (Pass 1)** - rounding is a silent parity trap. Python's `round()` is half-even, JS's `Math.round()` is half-up. Any formula shared between the builds needs its rounding rule written down and pinned in a suite on both sides.
- **Codex UI Recreation (Pass 3)** - Two builds can duplicate the *engine* and let a parity suite police it, because a truth table can check a formula. The view has no truth table - duplication there just drifts, one pixel at a time, until nobody can say which copy is right. The fix is the same shape either way: one source, a generator, and a freshness check that fails loudly. The only extra constraint is that the generated artifact may have to stand alone - the offline PWA precaches `index.html`, so the shared sources go in inline rather than linked.
