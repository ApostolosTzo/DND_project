// JS half of tools/parity_check.py: runs the shared logic functions over the
// case grid the Python side sends as JSON, and prints the results as JSON.
// parity_check.py computes the same values with the Python implementations and
// diffs the two lists item by item.
//
//   node tools/js_probe.js <cases.json> [repo-root]
//
// The case grid lives in parity_check.py so both halves always test identical
// inputs; this file only executes them.

"use strict";
const fs = require("fs");
const path = require("path");
const { createGame } = require("./harness");

const casesPath = process.argv[2];
const root = process.argv[3] || path.join(__dirname, "..");

if (!casesPath) {
    console.error("usage: node tools/js_probe.js <cases.json> [repo-root]");
    process.exit(2);
}

const cases = JSON.parse(fs.readFileSync(casesPath, "utf8"));
const g = createGame(root);
const J = JSON.stringify;
const out = {};

// --- pure item functions ---------------------------------------------------
out.two_handed = cases.dice.map((d) => g.call("twoHandedBonusFor", d));
out.damage_type = cases.damage_type.map((n) => g.call("damageType", n));
out.heal = cases.potion_inputs.map((n) => g.call("healAmount", n));
out.is_potion = cases.potion_inputs.map((n) => g.call("isPotion", n));
out.sell = cases.sell_inputs.map((n) => g.call("sellPrice", n));

out.element_of = cases.element_names.map((n) =>
    g.eval("elementOf(createItem(" + J(n) + "))"));

// usableBy over every item x every class, in one flat list (same order the
// Python side iterates).
out.usable = [];
for (const name of cases.usable.items) {
    for (const cls of cases.usable.classes) {
        out.usable.push(
            g.eval("usableBy(createItem(" + J(name) + "), " + J(cls) + ")"));
    }
}

// --- enemy construction ----------------------------------------------------
out.enemy = {};
for (const name of cases.enemy.templates) {
    out.enemy[name] = cases.enemy.levels.map((level) =>
        g.eval("(() => {" +
            "const e = new Enemy(" + J(name) + ", " + level + ");" +
            "return {max_hp: e.max_hp, ac: e.ac, damage_dice: e.damage_dice," +
            "damage_bonus: e.damage_bonus, xp_reward: e.xp_reward," +
            "gold_drop: e.gold_drop(), weak_to: e.weak_to, resists: e.resists};" +
            "})()"));
}

// --- damage application (weak/resist multipliers + rounding) ---------------
out.apply = cases.apply.map((c) =>
    g.eval("(() => {" +
        "const e = new Enemy(" + J(c.name) + ", 1);" +
        "const r = e.apply_damage(" + c.amount + ", " + J(c.type) + ");" +
        "return [r.total, r.note, e.hp];" +
        "})()"));

// --- player construction and the equipment sequence ------------------------
out.players = cases.players.map((c) =>
    g.eval("(() => {" +
        "const p = new Player(" + J(c.name) + ", " + J(c.race) + ", " +
        J(c.cls) + ", " + J(c.stats) + ");" +
        "const snap = [[p.max_hp, p.hp, p.ac, p.hp_per_level(), " +
        "p.xp_to_next(), p.sheet()]];" +
        "for (const step of " + J(c.steps) + ") {" +
        "  const arg = step[1] === null ? null : createItem(step[1]);" +
        "  if (step[0] === \"weapon\") p.equip_weapon(arg);" +
        "  else if (step[0] === \"offhand\") p.equip_offhand(arg);" +
        "  else if (step[0] === \"armor\") p.equip_armor(arg);" +
        "  snap.push([p.max_hp, p.hp, p.ac," +
        "    p.offhand ? p.offhand.name : null, p.inventory.length," +
        "    p.hands_full(), p.weapon ? p.weapon.name : null," +
        "    p.armor ? p.armor.name : null]);" +
        "}" +
        "return snap;" +
        "})()"));

// --- element riders with a frozen RNG --------------------------------------
// rng 0 forces every chance roll to succeed (and every die to read its
// minimum), rng just under 1 forces every chance roll to fail. The dark rider
// has no chance roll, so it must behave identically under both.
out.elements = cases.elements.map((c) => {
    g.setRandom(c.rng);
    const res = g.eval("(() => {" +
        "const p = new Player(\"Tester\", \"Human\", \"Wizard\", " + J(c.stats) + ");" +
        "const e = new Enemy(\"Zombie\", 1);" +
        "const note = e.inflict_element(" + J(c.element) + ", p);" +
        "return [note, e.status, e.status_text()];" +
        "})()");
    g.clearRandom();
    return res;
});

process.stdout.write(JSON.stringify(out));
