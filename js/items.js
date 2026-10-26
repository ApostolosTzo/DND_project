// items.py - Weapon / Armor / Item definitions, catalog and starting gear.
//
// Every item carries a stats_bonus that is applied when equipped
// (see player.effectiveStats()).
//
// The catalogue itself is GENERATED into js/game_data.js from items.py by
// tools/gen_js_data.py - Python is the single source of truth. This file
// reconstructs the Weapon/Armor/Item instances from that data and keeps the
// hand-written logic (two-handed rule, damage-type aliases, class gating).

function Weapon(name, damage_dice, damage_type, properties, stats_bonus) {
    this.name = name;
    this.damage_dice = damage_dice;
    this.damage_type = damage_type;
    this.properties = properties || [];
    this.stats_bonus = stats_bonus || {};
    this.category = "weapon";
}

function Armor(name, base_ac, armor_type, dex_limit, properties, stats_bonus) {
    this.name = name;
    this.base_ac = base_ac;
    this.armor_type = armor_type;
    this.dex_limit = (dex_limit === undefined) ? null : dex_limit;
    this.properties = properties || [];
    this.stats_bonus = stats_bonus || {};
    this.category = "armor";
}

function Item(name, description, effect, stats_bonus) {
    this.name = name;
    this.description = description;
    this.effect = (effect === undefined) ? null : effect;
    this.stats_bonus = stats_bonus || {};
    this.category = "item";
}

// Rebuild one catalogue entry as a live instance. Each category carries only
// the fields it needs, so the constructor gets exactly its own arguments.
function itemFromData(d) {
    if (d.category === "weapon") {
        return new Weapon(d.name, d.damage_dice, d.damage_type,
            d.properties.slice(), Object.assign({}, d.stats_bonus));
    }
    if (d.category === "armor") {
        return new Armor(d.name, d.base_ac, d.armor_type, d.dex_limit,
            d.properties.slice(), Object.assign({}, d.stats_bonus));
    }
    return new Item(d.name, d.description, d.effect,
        Object.assign({}, d.stats_bonus));
}

const ITEMS = (function () {
    const out = {};
    const src = GAME_DATA.items;
    Object.keys(src).forEach((name) => { out[name] = itemFromData(src[name]); });
    return out;
})();

// Every class starts with a full pack of healing potions.
const STARTING_POTIONS = GAME_DATA.starting_potions.slice();

const STARTING_GEAR = (function () {
    const out = {};
    const src = GAME_DATA.starting_gear;
    Object.keys(src).forEach((c) => {
        out[c] = { weapon: src[c].weapon, armor: src[c].armor, items: src[c].items.slice() };
    });
    return out;
})();

function getItem(name) {
    return ITEMS[name];
}

// Returns a fresh instance so items never share state between each other.
function createItem(name) {
    const item = getItem(name);
    if (!item) return null;
    if (item.category === "weapon") {
        return new Weapon(item.name, item.damage_dice, item.damage_type,
            item.properties.slice(), Object.assign({}, item.stats_bonus));
    }
    if (item.category === "armor") {
        return new Armor(item.name, item.base_ac, item.armor_type, item.dex_limit,
            item.properties.slice(), Object.assign({}, item.stats_bonus));
    }
    if (item.category === "item") {
        return new Item(item.name, item.description, item.effect,
            Object.assign({}, item.stats_bonus));
    }
    return null;
}

// Monster drops used for quests: material -> the monster it comes from.
const MATERIALS = GAME_DATA.materials;

// True for quest materials: not craftable, not sellable.
function isMaterial(item) {
    return !!item && Object.prototype.hasOwnProperty.call(MATERIALS, item.name);
}

// -----------------------------
// Healing potions
// -----------------------------
// One table drives every healing value in the game - the shop preview, the
// inventory panel and the actual restore in and out of combat. Generated from
// items.POTION_HEAL; item descriptions are rewritten from this table too, so
// a shop line can never claim a heal the potion does not do.
const POTION_HEAL = GAME_DATA.potion_heal;

// The level each tier starts appearing in shops. Generated from
// items.POTION_MIN_LEVEL - the game runs to level 200, so the ladder spreads
// over the same range.
const POTION_MIN_LEVEL = GAME_DATA.potion_min_level;

function isPotion(name) {
    return Object.prototype.hasOwnProperty.call(POTION_HEAL, name);
}

function healAmount(name) {
    return POTION_HEAL[name] || 0;
}

// Potions the player could actually use right now - full HP means no point, and
// the strongest one the player owns is always worth showing first.
function bestUsablePotion(p) {
    let best = null;
    p.inventory.forEach((item) => {
        if (isPotion(item.name) && p.hp < p.max_hp) {
            if (!best || healAmount(item.name) > healAmount(best.name)) best = item;
        }
    });
    return best;
}

// -----------------------------
// Two-handed weapons
// -----------------------------
// A two-handed weapon needs both hands, which is what locks the off-hand (see
// player.js). It also hits harder: the bonus below is added to every hit, and
// is keyed off the damage dice so it always matches the weapon it belongs to.
// The rule, not a lookup table: two dice are worth more than one, and a bigger
// die is worth more than a smaller one. Longsword (1d8) and Greatsword (2d6)
// both land on +1; Maul (2d10) gets +2; a dagger (1d4) gets nothing.
//
// This parses the "NdX+Y" string rather than matching it exactly, so a weapon
// whose dice were rebalanced (Maul became 2d6+2) keeps its bonus instead of
// silently dropping to zero because the key no longer exists.
function twoHandedBonusFor(dice) {
    const m = /^(\d*)d(\d+)/.exec(String(dice).trim());
    if (!m) return 0;
    const count = parseInt(m[1] || "1", 10);
    const sides = parseInt(m[2], 10);
    if (count >= 2) return sides >= 10 ? 2 : 1;
    return sides >= 8 ? 1 : 0;
}

// Reference table for documentation and for the player guide. Kept in sync with
// twoHandedBonusFor() above, which is what the game actually calls.
const TWO_HANDED_BONUS = GAME_DATA.two_handed_bonus;

function isTwoHanded(item) {
    return !!item && Array.isArray(item.properties) && item.properties.indexOf("two-handed") !== -1;
}

function twoHandedBonus(weapon) {
    if (!isTwoHanded(weapon)) return 0;
    return twoHandedBonusFor(weapon.damage_dice);
}

// -----------------------------
// Damage types and elements
// -----------------------------
// damage_type is stored in a few shapes ("fire_damage", "cold"); everything
// downstream uses one canonical name per element.
const DAMAGE_TYPE_ALIASES = GAME_DATA.damage_type_aliases;

const DAMAGE_TYPES = GAME_DATA.damage_types;

function damageType(name) {
    const key = String(name || "piercing");
    return DAMAGE_TYPE_ALIASES[key] || key;
}

// Every one of these five inflicts a lasting effect when the hit lands. Each
// one has its own application chance and its own scaling stat - see enemy.js,
// which is where the numbers actually live.
//
//   fire      rolls to ignite, scales on INT
//   ice       rolls to freeze, scales on INT
//   poison    rolls to poison, scales on DEX, runs until the creature dies
//   lightning rolls to strike, scales on WIS
//   dark      always applies, and hits harder the more STR you have
//
// force, slashing, bludgeoning and piercing deliberately stay out of this table:
// they are plain damage with no rider.
const ELEMENT_STATUS = GAME_DATA.element_status;

function elementOf(weapon) {
    if (!weapon) return null;
    const type = damageType(weapon.damage_type);
    return Object.prototype.hasOwnProperty.call(ELEMENT_STATUS, type) ? type : null;
}


// -----------------------------
// Which class may wield which weapon
// -----------------------------
// Every weapon belongs to one class's armory, or to ALL_CLASSES when anyone can
// pick it up. The four class armories drive shop.js: each class gets its own
// themed NPC, and browsing someone else's stall shows their gear greyed out
// with a "not your class's weapon" note.
//
// Bows, darts, crossbows and the plain Wand are deliberately universal. That is
// what lets a Fighter walk into the Wizard's stall and still buy a bow or a
// wand without anything being in the way.
const ALL_CLASSES = GAME_DATA.all_classes;

const WEAPON_CLASSES = GAME_DATA.weapon_classes;

// Classes that may equip this item. Armour, shields and consumables are open to
// everyone; only weapons carry a class restriction, via WEAPON_CLASSES.
function itemClasses(item) {
    if (!item || item.category !== "weapon") return ALL_CLASSES.slice();
    return WEAPON_CLASSES[item.name] || ALL_CLASSES;
}

function usableBy(item, className) {
    return itemClasses(item).indexOf(className) !== -1;
}
