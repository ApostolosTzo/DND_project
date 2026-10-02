// shop.py - NPC shop definitions (stock, price and level gate).
//
// This module derives its stock; it does not hard-code it. The previous version
// was a literal object in which the same weapon appeared five times inside one
// NPC, and since JavaScript silently keeps the last duplicate key, those
// repeats were invisible dead weight: a reader could edit what looked like the
// live entry and change nothing at all.
//
// Stock is computed from the catalogue in items.js:
//
//   * Every item lands on one of sixteen unlock tiers, level 1 to level 200.
//   * Each class gets its own themed NPC, and every armory also stocks the
//     universal ranged kit, so a Fighter can buy a bow from any of them.
//   * Prices follow the tier: roughly TIER_MULT levels of income, multiplied by
//     where the item sits within its own rung (1.0x for the cheapest, 3.0x for
//     the strongest).
//
// This is a line-for-line mirror of shop.py's derivation. parity_check.py
// compares the two results item by item.

// NPCs pay 20% under the cheapest price an item sells for.
const SELL_RATIO = 0.8;

// -----------------------------
// The unlock ladder: 1 -> 200
// -----------------------------
// The game runs to level 200, so the ladder spreads across the whole range with
// growing gaps: 2, 3, 4, 5, 7, 8, 10, 12, 14, 16, 18, 20, 22, 24, 34.
const UNLOCK_TIERS = [1, 3, 6, 10, 15, 22, 30, 40, 52, 66, 82, 100, 120, 142, 166, 200];

const TIER_BASE = 10.0;
const TIER_MULT = [1.0, 1.1, 1.2, 1.35, 1.5, 1.7, 1.9, 2.1, 2.35, 2.6, 2.9, 3.2, 3.5, 3.8, 4.1, 4.5];

// How much a weapon's element is worth when ranking it for a rung.
const ELEMENT_VALUE = { ice: 2.0, poison: 2.5, lightning: 1.5, fire: 1.0, dark: 1.0 };

// -----------------------------
// The four armories
// -----------------------------
// [NPC name, class, tagline shown as the shop's greeting]
const ARMORY_NPCS = [
    ["Weaponsmith", "Fighter", "Blades, axes and polearms."],
    ["Shadow Fence", "Rogue", "Finesse weapons and thrown daggers."],
    ["Wizard", "Wizard", "Staves and elemental wands."],
    ["Temple", "Cleric", "Maces, flails and divine tools."]
];

// Potions are priced by hand rather than by rung.
const POTION_PRICES = {
    "Healing Potion": 15,
    "Greater Healing Potion": 200,
    "Superior Healing Potion": 1500,
    "Grand Healing Potion": 8000,
    "Ultimate Healing Potion": 30000
};

// Armour and shields keep the ORIGINAL hand-tuned level order, stretched onto
// the new ladder rather than re-derived. Their stat bonuses are large and uneven
// (Wizard Robe INT+9, Dragon Scale CON+8), so any computed power score would
// reorder pieces that were placed deliberately.
const OLD_ARMOUR_LEVELS = {
    "Leather": 1, "Studded Leather": 2, "Hide": 1, "Chainmail": 1, "Scale Mail": 2,
    "Breastplate": 3, "Half Plate": 4, "Ring Mail": 1, "Plate": 4, "Splint": 5,
    "Titanium": 7, "Dragon Scale": 10, "Padded Armor": 1, "Nomad Leather": 2,
    "Doublet": 3, "Shadowcloth": 6, "Wolf Hide Armor": 4, "Robe of Silk": 3,
    "Mithral Leather": 7, "Elven Cloak Armor": 6, "Riveted Leather": 2, "Padded Mail": 2,
    "Ironweave Mail": 5, "Bone Lacquer": 8, "Goblinforged Mail": 6, "Enchanted Hide": 7,
    "Lamellar Armor": 7, "Ward Mail": 6, "Banded Mail": 1, "Steel Plate": 8,
    "Obsidian Plate": 9, "Mithral Plate": 10, "Warden Plate": 9, "Dragonbone Plate": 10,
    "Titanforged Plate": 9, "Barrier Plate": 11, "Ancient Scale Plate": 12,
    // Sold by the Wizard's stall rather than the Armorer, but it is still armour.
    "Wizard Robe": 2
};

const OLD_SHIELD_LEVELS = {
    "Buckler": 1, "Shield": 1, "Iron Shield": 2, "Bronze Shield": 2, "Tower Shield": 4,
    "Runed Shield": 5, "Magic Shield": 6, "Warden's Bulwark": 8, "Bulwark of Dawn": 10,
    "Dragon Shield": 11, "Aegis Shield": 13
};

const OLD_LEVEL_MAX = { armour: 12, shields: 13 };

// Odds and ends that are neither weapon nor armour, sold by a named NPC.
const EXTRA_STOCK = {
    "Wizard": {
        "Arcane Ring": { price: 2400, min_level: 66 }
    }
};

// -----------------------------
// Deriving the stock
// -----------------------------
function _avgDice(dice) {
    let s = String(dice);
    let bonus = 0;
    if (s.indexOf("+") !== -1) {
        const parts = s.split("+");
        s = parts[0];
        bonus = parseInt(parts[1], 10);
    } else if (s.indexOf("-") !== -1) {
        const parts = s.split("-");
        s = parts[0];
        bonus = -parseInt(parts[1], 10);
    }
    const d = s.split("d");
    return parseInt(d[0], 10) * (parseInt(d[1], 10) + 1) / 2.0 + bonus;
}

// Rough power ranking, used only to sort items within a rung. Armour ranks 0 -
// it is ordered by its hand-tuned level instead.
function _weaponScore(item) {
    if (!item || item.category !== "weapon") return 0.0;
    const bonuses = Object.keys(item.stats_bonus || {}).reduce(
        (a, k) => a + item.stats_bonus[k], 0);
    const el = elementOf(item);
    return _avgDice(item.damage_dice)
        + 2 * twoHandedBonus(item)
        + 1.5 * bonuses
        + (ELEMENT_VALUE[el] || 0.0);
}

// Snap to a price players read as a deliberate number, not a computed one.
function _roundPrice(v) {
    v = Math.max(5.0, v);
    let step;
    if (v >= 10000) step = 250;
    else if (v >= 2500) step = 100;
    else if (v >= 800) step = 50;
    else if (v >= 200) step = 10;
    else if (v >= 60) step = 5;
    else step = 1;
    return Math.round(v / step) * step;
}

function _priceFor(tier, rel) {
    return _roundPrice(TIER_BASE * UNLOCK_TIERS[tier] * TIER_MULT[tier] * rel);
}

// Rank -> rung, spread evenly across the whole ladder.
function _spread(ranked) {
    const n = ranked.length;
    const out = {};
    if (n === 0) return out;
    if (n === 1) { out[ranked[0]] = 0; return out; }
    const last = UNLOCK_TIERS.length - 1;
    ranked.forEach((name, rank) => { out[name] = Math.round(rank / (n - 1) * last); });
    return out;
}

// Stretch the original 1..old_max ladder onto the full UNLOCK_TIERS.
function _mapOldLevel(old, oldMax) {
    const last = UNLOCK_TIERS.length - 1;
    const frac = (Math.max(1, old) - 1) / Math.max(1, oldMax - 1);
    return Math.round(frac * last);
}

function _build() {
    const groups = {};
    Object.keys(ITEMS).forEach((name) => {
        const item = ITEMS[name];
        if (item.category !== "weapon") return;
        const classes = WEAPON_CLASSES[name] || ALL_CLASSES;
        if (classes === ALL_CLASSES) {
            groups.Universal = groups.Universal || [];
            groups.Universal.push(name);
        } else {
            classes.forEach((c) => {
                groups[c] = groups[c] || [];
                groups[c].push(name);
            });
        }
    });

    const tiers = {};
    const byScore = (a, b) => {
        const d = _weaponScore(ITEMS[a]) - _weaponScore(ITEMS[b]);
        return d !== 0 ? d : (a < b ? -1 : (a > b ? 1 : 0));
    };

    // The universal kit lands on the same rung in every stall, so a Crossbow
    // never costs a different level depending on who you buy it from.
    Object.assign(tiers, _spread((groups.Universal || []).slice().sort(byScore)));

    ARMORY_NPCS.forEach(([, cls]) => {
        // A class's starting weapon is always rung 0: a Fighter handed a
        // Longsword at level 1 must be able to buy a replacement at level 1.
        const opener = STARTING_GEAR[cls].weapon;
        const rest = (groups[cls] || []).filter((n) => n !== opener).sort(byScore);
        tiers[opener] = 0;
        Object.keys(_spread(rest)).forEach((name) => {
            tiers[name] = Math.min(UNLOCK_TIERS.length - 1, _spread(rest)[name] + 1);
        });
    });
    Object.keys(OLD_ARMOUR_LEVELS).forEach((name) => {
        tiers[name] = _mapOldLevel(OLD_ARMOUR_LEVELS[name], OLD_LEVEL_MAX.armour);
    });
    Object.keys(OLD_SHIELD_LEVELS).forEach((name) => {
        tiers[name] = _mapOldLevel(OLD_SHIELD_LEVELS[name], OLD_LEVEL_MAX.shields);
    });

    const armour = Object.keys(ITEMS).filter(
        (n) => ITEMS[n].category === "armor" && ITEMS[n].armor_type !== "shield");
    const shields = Object.keys(ITEMS).filter(
        (n) => ITEMS[n].category === "armor" && ITEMS[n].armor_type === "shield");

    const stock = {};
    ARMORY_NPCS.forEach(([npc, cls]) => {
        const set = {};
        (groups[cls] || []).forEach((n) => { set[n] = true; });
        (groups.Universal || []).forEach((n) => { set[n] = true; });
        stock[npc] = Object.keys(set).sort((a, b) => (
            (tiers[a] - tiers[b]) || byScore(a, b)));
    });
    stock["Armorer"] = armour.slice().sort((a, b) => (tiers[a] - tiers[b]) || (
        a < b ? -1 : (a > b ? 1 : 0)));
    stock["Shield Smith"] = shields.slice().sort((a, b) => (tiers[a] - tiers[b]) || (
        a < b ? -1 : (a > b ? 1 : 0)));

    Object.keys(EXTRA_STOCK).forEach((npc) => {
        const extras = EXTRA_STOCK[npc];
        const set = {};
        stock[npc].forEach((n) => { set[n] = true; });
        Object.keys(extras).forEach((n) => { set[n] = true; });
        stock[npc] = Object.keys(set).sort((a, b) => {
            const la = extras[a] ? extras[a].min_level : tiers[a];
            const lb = extras[b] ? extras[b].min_level : tiers[b];
            return (la - lb) || byScore(a, b);
        });
    });

    const prices = {};
    Object.keys(stock).forEach((npc) => {
        const extras = EXTRA_STOCK[npc] || {};
        const buckets = {};
        stock[npc].forEach((n) => {
            if (extras[n]) return;
            if (buckets[tiers[n]] === undefined) buckets[tiers[n]] = [];
            buckets[tiers[n]].push(n);
        });
        Object.keys(buckets).forEach((tier) => {
            const group = buckets[tier].slice().sort(byScore);
            const m = group.length;
            group.forEach((n, i) => {
                // 1.0x cheapest at this rung, 3.0x strongest, so every rung offers
                // a budget option as well as a flagship.
                const rel = (m === 1) ? 1.8 : 1.0 + 2.0 * i / (m - 1);
                prices[n] = _priceFor(tier, rel);
            });
        });
    });

    const levels = {};
    Object.keys(tiers).forEach((n) => { levels[n] = UNLOCK_TIERS[tiers[n]]; });
    return { stock: stock, prices: prices, levels: levels };
}

const _BUILT = _build();

function _stockItems(names, npc) {
    const extras = EXTRA_STOCK[npc] || {};
    const out = {};
    names.forEach((n) => {
        if (extras[n]) out[n] = extras[n];
        else out[n] = { price: _BUILT.prices[n], min_level: _BUILT.levels[n] };
    });
    return out;
}

const SHOP_NPCS = {
    "Potion Merchant": {
        class: null,
        note: "Potions for every level.",
        items: (function () {
            const out = {};
            Object.keys(POTION_PRICES).sort(
                (a, b) => POTION_MIN_LEVEL[a] - POTION_MIN_LEVEL[b]).forEach((n) => {
                out[n] = { price: POTION_PRICES[n], min_level: POTION_MIN_LEVEL[n] };
            });
            return out;
        })()
    },
    // Every shield in the game is sold here and nowhere else.
    "Shield Smith": {
        class: null,
        note: "Every shield in the game is sold here and nowhere else.",
        items: _stockItems(_BUILT.stock["Shield Smith"], "Shield Smith")
    }
};

ARMORY_NPCS.forEach(([npc, cls, note]) => {
    SHOP_NPCS[npc] = {
        class: cls,
        note: note,
        items: _stockItems(_BUILT.stock[npc], npc)
    };
});

SHOP_NPCS["Armorer"] = {
    class: null,
    note: "Body armour, light to heavy.",
    items: _stockItems(_BUILT.stock["Armorer"], "Armorer")
};

// Which class an NPC caters to, or null when it serves everybody.
const NPC_CLASS = {};
const NPC_NOTE = {};
Object.keys(SHOP_NPCS).forEach((npc) => {
    NPC_CLASS[npc] = SHOP_NPCS[npc].class;
    NPC_NOTE[npc] = SHOP_NPCS[npc].note;
});

// What an NPC pays for one of these, or null if nobody sells it.
function sellPrice(itemName) {
    const item = createItem(itemName);
    if (!item || isMaterial(item)) return null;
    let cheapest = null;
    Object.keys(SHOP_NPCS).forEach((s) => {
        const entry = SHOP_NPCS[s].items[itemName];
        if (entry && (cheapest === null || entry.price < cheapest)) cheapest = entry.price;
    });
    if (cheapest === null) return null;
    return Math.floor(cheapest * SELL_RATIO);
}