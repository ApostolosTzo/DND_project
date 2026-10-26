// Shared Node harness: loads the PWA's game scripts into a vm context that
// behaves like a browser page (a localStorage stub, nothing else). Used by
// tools/js_probe.js (parity checks against Python) and tools/js_suite.js
// (behavioural tests of the game loop).
//
//   const { createGame } = require("./harness");
//   const g = createGame(rootDir);
//   g.call("twoHandedBonusFor", "2d6");   // -> 1
//   g.eval("startGame({name:'X'}).screen");  // -> "town"
//
// Everything is evaluated *inside* the context, because top-level const in
// game_data.js/items.js/etc. lives in the context's global lexical scope (the
// same way a browser's <script> tags share one scope) and is invisible from
// outside as a property. g.eval/g.call bridge that gap.

"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

// Load order matches the <script> tags in index.html. saves.js is included
// even though it reads localStorage at load time - the stub below satisfies it.
const SCRIPTS = [
    "dice.js",
    "game_data.js",
    "items.js",
    "enemy.js",
    "player.js",
    "quests.js",
    "shop.js",
    "world_map.js",
    "saves.js",
    "game.js"
];

function createGame(root) {
    const store = Object.create(null);
    const ctx = {
        console: console,
        localStorage: {
            getItem: (k) => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
            setItem: (k, v) => { store[k] = String(v); },
            removeItem: (k) => { delete store[k]; }
        }
    };
    vm.createContext(ctx);

    for (const file of SCRIPTS) {
        const full = path.join(root, "js", file);
        vm.runInContext(fs.readFileSync(full, "utf8"), ctx, { filename: file });
    }

    // Run code inside the context; normalize the result by round-tripping it
    // through JSON so callers get plain local objects, not cross-realm ones.
    function eval_(code) {
        const raw = vm.runInContext(code, ctx, { filename: "<probe>" });
        return JSON.parse(JSON.stringify(raw === undefined ? null : raw));
    }

    // Call a global function by name with JSON-safe arguments.
    function call(fn, ...args) {
        const code = fn + "(" + args.map((a) => JSON.stringify(a)).join(",") + ")";
        return eval_(code);
    }

    // Freeze Math.random at a constant (browser-side dice use it), so tests can
    // force "always triggers" (0) or "never triggers" (just under 1). The real
    // implementation is stashed so clearRandom() puts it back.
    function setRandom(value) {
        vm.runInContext(
            "if (!globalThis.__origRandom) globalThis.__origRandom = Math.random;\n" +
            "Math.random = function () { return " + value + "; };",
            ctx
        );
    }
    function clearRandom() {
        vm.runInContext(
            "if (globalThis.__origRandom) { Math.random = globalThis.__origRandom; delete globalThis.__origRandom; }",
            ctx
        );
    }

    return { ctx, eval: eval_, call, setRandom, clearRandom };
}

module.exports = { createGame, SCRIPTS };
