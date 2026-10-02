// items.py - Weapon / Armor / Item definitions, catalog and starting gear.
//
// Every item carries a stats_bonus that is applied when equipped
// (see player.effectiveStats()).

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

const ITEMS = {
    // Weapons (melee)
    "Longsword": new Weapon("Longsword", "1d8", "slashing", ["two-handed", "versatile"], { STR: 1 }),
    "Greatsword": new Weapon("Greatsword", "2d6", "slashing", ["two-handed", "heavy"], { STR: 2 }),
    "Battle Axe": new Weapon("Battle Axe", "1d8", "slashing", ["versatile"], { STR: 1 }),
    "War Hammer": new Weapon("War Hammer", "1d10", "bludgeoning", ["versatile"], { STR: 1 }),
    "Mace": new Weapon("Mace", "1d6", "bludgeoning", ["versatile"], { STR: 1 }),
    "Flail": new Weapon("Flail", "1d8", "bludgeoning", ["versatile"], { STR: 1 }),
    "Spear": new Weapon("Spear", "1d6", "piercing", ["versatile", "thrown"], { STR: 1 }),
    "Rapier": new Weapon("Rapier", "1d8", "piercing", ["finesse"], { DEX: 1 }),
    "Dagger": new Weapon("Dagger", "1d4", "piercing", ["finesse", "light", "thrown"], { DEX: 1 }),
    "Quarterstaff": new Weapon("Quarterstaff", "1d6", "bludgeoning", ["versatile"], { STR: 1 }),

    // Weapons (ranged)
    "Shortbow": new Weapon("Shortbow", "1d6", "piercing", ["two-handed", "ranged"], { DEX: 1 }),
    "Longbow": new Weapon("Longbow", "1d8", "piercing", ["two-handed", "ranged", "heavy"], { DEX: 1 }),
    "Crossbow": new Weapon("Crossbow", "1d10", "piercing", ["two-handed", "ranged", "loading"], { DEX: 1 }),
    "Hand Crossbow": new Weapon("Hand Crossbow", "1d6", "piercing", ["ranged", "light"], { DEX: 1 }),

    // Weapons (magical)
    "Magic Staff": new Weapon("Magic Staff", "1d6", "bludgeoning", ["versatile", "magic"]),
    "Arcane Staff": new Weapon("Arcane Staff", "1d8", "force", ["two-handed", "magic"], { INT: 1 }),
    "Wand": new Weapon("Wand", "1d4", "force", ["magic", "ranged"]),
    "Lampada": new Weapon("Lampada", "1d6", "fire_damage", ["versatile", "magic"]),

    // Armors (light)
    "Leather": new Armor("Leather", 11, "light"),
    "Studded Leather": new Armor("Studded Leather", 12, "light", null, [], { DEX: 1 }),

    // Armors (medium)
    "Hide": new Armor("Hide", 13, "medium", 2),
    "Chainmail": new Armor("Chainmail", 14, "medium", 2),
    "Scale Mail": new Armor("Scale Mail", 14, "medium", 2),
    "Breastplate": new Armor("Breastplate", 14, "medium", 2),
    "Half Plate": new Armor("Half Plate", 15, "medium", 2),

    // Armors (heavy)
    "Ring Mail": new Armor("Ring Mail", 14, "heavy"),
    "Plate": new Armor("Plate", 17, "heavy"),
    "Splint": new Armor("Splint", 17, "heavy"),
    "Titanium": new Armor("Titanium", 18, "heavy"),
    "Dragon Scale": new Armor("Dragon Scale", 19, "heavy", null, [], { CON: 8 }),

    // Shields
    "Shield": new Armor("Shield", 2, "shield"),

    // Special armor
    "Wizard Robe": new Armor("Wizard Robe", 10, "light", null, ["magic"], { INT: 9 }),

    // Items (potions & consumables)
    "Healing Potion": new Item("Healing Potion", "Restores 9 HP", "heal"),
    "Greater Healing Potion": new Item("Greater Healing Potion", "Restores 20 HP", "heal"),
    "Superior Healing Potion": new Item("Superior Healing Potion", "Restores 100 HP. Unlocks at level 15.", "heal"),
    "Grand Healing Potion": new Item("Grand Healing Potion", "Restores 300 HP. Unlocks at level 35.", "heal"),
    "Ultimate Healing Potion": new Item("Ultimate Healing Potion", "Restores 800 HP. Unlocks at level 70.", "heal"),

    // Items (scrolls - future use)
    "Scroll of Fireball": new Item("Scroll of Fireball", "Deals fire damage (future use)", "scroll_fireball"),
    "Scroll of Healing": new Item("Scroll of Healing", "Heals ally (future use)", "scroll_heal"),

    // Items (misc)
    "Arcane Ring": new Item("Arcane Ring", "A ring humming with magic", null, { INT: 1 }),


    // --- Extra weapons (added: 30) ---
    "Shortsword": new Weapon("Shortsword", "1d6", "slashing", ["versatile"], {STR: 1}),
    "Sabre": new Weapon("Sabre", "1d8", "slashing", ["finesse"], {DEX: 1}),
    "Scimitar": new Weapon("Scimitar", "1d8", "slashing", ["finesse", "light"], {DEX: 1}),
    "Claymore": new Weapon("Claymore", "2d6", "slashing", ["two-handed", "heavy"], {STR: 2}),
    "Falchion": new Weapon("Falchion", "2d4", "slashing", ["two-handed", "heavy"], {STR: 2}),
    "Trident": new Weapon("Trident", "1d6", "piercing", ["versatile", "thrown"], {STR: 1}),
    "Glaive": new Weapon("Glaive", "2d6", "slashing", ["two-handed", "heavy"], {STR: 2}),
    "Lucerne Hammer": new Weapon("Lucerne Hammer", "2d6", "piercing", ["two-handed", "heavy"], {STR: 2}),
    "Greataxe": new Weapon("Greataxe", "2d6", "slashing", ["two-handed", "heavy"], {STR: 3}),
    "Maul": new Weapon("Maul", "2d6+2", "bludgeoning", ["two-handed", "heavy"], {STR: 3}),
    "War Sickle": new Weapon("War Sickle", "1d8", "slashing", ["versatile", "light"], {STR: 1}),
    "Kris Dagger": new Weapon("Kris Dagger", "2d4", "piercing", ["finesse", "light", "thrown"], {DEX: 1}),
    "Broadsword": new Weapon("Broadsword", "2d4", "slashing", ["two-handed", "versatile"], {STR: 1}),
    "Cudgel": new Weapon("Cudgel", "1d4", "bludgeoning", ["light"], {STR: 1}),
    "Bone Club": new Weapon("Bone Club", "1d6", "bludgeoning", ["light"], {STR: 1}),
    "Anchor": new Weapon("Anchor", "1d8", "bludgeoning", ["two-handed", "heavy"], {STR: 1}),
    "Executioner's Axe": new Weapon("Executioner's Axe", "1d10", "slashing", ["two-handed", "heavy"], {STR: 2}),
    "Viper Fang": new Weapon("Viper Fang", "1d6", "piercing", ["finesse", "light", "thrown"], {DEX: 2}),
    "Sling": new Weapon("Sling", "1d4", "bludgeoning", ["ranged", "light"], {DEX: 1}),
    "Dart": new Weapon("Dart", "1d4", "piercing", ["ranged", "light", "thrown"], {DEX: 1}),
    "Javelin": new Weapon("Javelin", "1d6", "piercing", ["thrown", "versatile"], {DEX: 1}),
    "Light Crossbow": new Weapon("Light Crossbow", "1d8", "piercing", ["ranged", "light"], {DEX: 1}),
    "Heavy Crossbow": new Weapon("Heavy Crossbow", "1d10", "piercing", ["ranged", "loading", "heavy"], {STR: 1}),
    "Composite Bow": new Weapon("Composite Bow", "1d8", "piercing", ["ranged", "heavy"], {DEX: 2}),
    "Repeating Crossbow": new Weapon("Repeating Crossbow", "1d10", "piercing", ["ranged", "loading"], {DEX: 2}),
    "Ember Blade": new Weapon("Ember Blade", "1d8", "fire_damage", ["versatile", "magic"], {INT: 1}),
    "Frost Staff": new Weapon("Frost Staff", "2d6", "cold", ["two-handed", "magic"], {INT: 2}),
    "Storm Wand": new Weapon("Storm Wand", "1d6", "lightning", ["magic", "ranged"], {DEX: 1}),
    "Bone Wand": new Weapon("Bone Wand", "1d6", "dark", ["magic", "ranged"], {WIS: 1}),
    "Runed Dagger": new Weapon("Runed Dagger", "2d4+2", "force", ["finesse", "light", "magic"], {DEX: 2, INT: 1}),
    "Venom Dagger": new Weapon("Venom Dagger", "2d4+5", "poison", ["finesse", "light", "thrown"], {DEX: 3}),
    "Plasma Wand": new Weapon("Plasma Wand", "1d6", "poison", ["magic", "ranged"], {INT: 1}),

    // --- Extra armour and shields (added: 30) ---
    "Padded Armor": new Armor("Padded Armor", 10, "light", null, [], {CON: 1}),
    "Nomad Leather": new Armor("Nomad Leather", 11, "light", null, [], {DEX: 1}),
    "Doublet": new Armor("Doublet", 12, "light", null, [], {DEX: 1}),
    "Shadowcloth": new Armor("Shadowcloth", 12, "light", null, ["magic"], {DEX: 2}),
    "Wolf Hide Armor": new Armor("Wolf Hide Armor", 12, "light", null, [], {CON: 1, DEX: 1}),
    "Robe of Silk": new Armor("Robe of Silk", 10, "light", null, ["magic"], {INT: 1}),
    "Mithral Leather": new Armor("Mithral Leather", 13, "light", null, ["magic"], {DEX: 1, CON: 1}),
    "Elven Cloak Armor": new Armor("Elven Cloak Armor", 12, "light", null, ["magic"], {DEX: 2}),
    "Riveted Leather": new Armor("Riveted Leather", 13, "medium", 2, [], {CON: 1}),
    "Padded Mail": new Armor("Padded Mail", 13, "medium", 2, [], {DEX: 1}),
    "Ironweave Mail": new Armor("Ironweave Mail", 14, "medium", 2, [], {CON: 1}),
    "Bone Lacquer": new Armor("Bone Lacquer", 14, "medium", 2, ["magic"], {CON: 2}),
    "Goblinforged Mail": new Armor("Goblinforged Mail", 14, "medium", 2, [], {STR: 1, CON: 1}),
    "Enchanted Hide": new Armor("Enchanted Hide", 14, "medium", 2, ["magic"], {CON: 1, WIS: 1}),
    "Lamellar Armor": new Armor("Lamellar Armor", 15, "medium", 2, [], {CON: 1}),
    "Ward Mail": new Armor("Ward Mail", 14, "medium", 2, ["magic"], {DEX: 1}),
    "Banded Mail": new Armor("Banded Mail", 15, "heavy"),
    "Steel Plate": new Armor("Steel Plate", 17, "heavy", null, [], {CON: 1}),
    "Obsidian Plate": new Armor("Obsidian Plate", 17, "heavy", null, ["magic"], {CON: 2}),
    "Mithral Plate": new Armor("Mithral Plate", 18, "heavy", null, ["magic", "light"], {CON: 1, DEX: 1}),
    "Warden Plate": new Armor("Warden Plate", 17, "heavy", null, [], {STR: 1, CON: 1}),
    "Dragonbone Plate": new Armor("Dragonbone Plate", 18, "heavy", null, ["magic"], {CON: 2}),
    "Titanforged Plate": new Armor("Titanforged Plate", 18, "heavy", null, [], {STR: 1, CON: 1}),
    "Barrier Plate": new Armor("Barrier Plate", 19, "heavy", null, ["magic"], {CON: 1}),
    "Ancient Scale Plate": new Armor("Ancient Scale Plate", 19, "heavy", null, ["magic"], {CON: 2}),
    "Buckler": new Armor("Buckler", 1, "shield", null, ["light"], {DEX: 1}),
    "Bronze Shield": new Armor("Bronze Shield", 2, "shield", null, [], {CON: 1}),
    "Runed Shield": new Armor("Runed Shield", 3, "shield", null, ["magic"], {INT: 1, WIS: 1}),
    "Warden's Bulwark": new Armor("Warden's Bulwark", 5, "shield", null, ["two-handed"], {CON: 2}),
    "Bulwark of Dawn": new Armor("Bulwark of Dawn", 6, "shield", null, ["magic"], {STR: 2, CON: 2}),

    // --- Monster drops (quest materials) ---
    "Metal Fragments": new Item("Metal Fragments", "Scrap metal wrenched from a goblin's gear.", "material"),
    "Web String": new Item("Web String", "Silken strand, still faintly sticky.", "material"),
    "Slime Ball": new Item("Slime Ball", "A wobbling blob that refuses to evaporate.", "material"),
    "Rotten Flesh": new Item("Rotten Flesh", "Rank, but some alchemists pay for it.", "material"),
    "Bone": new Item("Bone", "A clean femur. Someone was taller once.", "material"),
    "Fur": new Item("Fur", "Coarse grey pelt, still warm.", "material"),
    "Plasma": new Item("Plasma", "A finger of cold blue light. Handle carefully.", "material"),

    // --- Mirrored from items.py (hand-added shields) ---
    "Iron Shield": new Armor("Iron Shield", 3, "shield", null, [], { "STR": 1, "DEX": 3 }),
    "Tower Shield": new Armor("Tower Shield", 4, "shield", null, [], { "STR": 2, "DEX": 2 }),
    "Magic Shield": new Armor("Magic Shield", 5, "shield", null, [], { "INT": 2, "WIS": 2 }),
    "Dragon Shield": new Armor("Dragon Shield", 6, "shield", null, [], { "STR": 4, "DEX": 4, "CON": 4 }),
    "Aegis Shield": new Armor("Aegis Shield", 7, "shield", null, [], { "STR": 5, "DEX": 5, "CON": 5 }),
};

// Every class starts with a full pack of healing potions.
const STARTING_POTIONS = Array(15).fill("Healing Potion");

const STARTING_GEAR = {
    "Fighter": { weapon: "Longsword", armor: "Chainmail", items: STARTING_POTIONS.slice() },
    "Rogue": { weapon: "Dagger", armor: "Leather", items: STARTING_POTIONS.slice() },
    "Wizard": { weapon: "Magic Staff", armor: null, items: STARTING_POTIONS.slice() },
    "Cleric": { weapon: "Mace", armor: "Plate", items: STARTING_POTIONS.slice() }
};

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
const MATERIALS = {
    "Metal Fragments": "Goblin",
    "Web String": "Spider",
    "Slime Ball": "Slime",
    "Rotten Flesh": "Zombie",
    "Bone": "Skeleton",
    "Fur": "Wolf",
    "Plasma": "Ghost",
};

// True for quest materials: not craftable, not sellable.
function isMaterial(item) {
    return !!item && Object.prototype.hasOwnProperty.call(MATERIALS, item.name);
}

// -----------------------------
// Healing potions
// -----------------------------
// One table drives every healing value in the game - the shop preview, the
// inventory panel and the actual restore in and out of combat. Adding a tier
// here is all that is needed; nothing hard-codes a potion's strength.
const POTION_HEAL = {
    "Healing Potion": 10,
    "Greater Healing Potion": 55,
    "Superior Healing Potion": 120,
    "Grand Healing Potion": 220,
    "Ultimate Healing Potion": 360
};

// The level each tier starts appearing in shops.
//
// The game now runs to level 200 (see shop.js UNLOCK_TIERS), so the ladder has
// to spread over the same range or the top tier would be bought at level 70 and
// then never again.
//
// The heal amounts scale with the gate for the same reason. Maximum HP grows
// linearly with level (about 3 per level for the middle classes, 4 for a
// Fighter and 2 for a Wizard), so a fixed 20 HP potion that was a third of a
// level-5 character is a rounding error at level 60. Each tier is tuned to
// roughly 55% of the max HP of an average class at the level it unlocks, which
// lands at about 45% for a Fighter and 90% for a Wizard - so a big potion is
// always worth drinking, never just wasted.
const POTION_MIN_LEVEL = {
    "Healing Potion": 1,
    "Greater Healing Potion": 25,
    "Superior Healing Potion": 60,
    "Grand Healing Potion": 120,
    "Ultimate Healing Potion": 200
};

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
const TWO_HANDED_BONUS = {
    "1d4": 0, "1d6": 0, "1d8": 1, "1d10": 1, "1d12": 1,
    "2d4": 1, "2d6": 1, "2d10": 2, "2d12": 2
};

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
const DAMAGE_TYPE_ALIASES = {
    fire_damage: "fire",
    cold: "ice"
};

const DAMAGE_TYPES = ["slashing", "bludgeoning", "piercing", "fire",
    "ice", "lightning", "dark", "force", "poison"];

function damageType(name) {
    const key = String(name || "piercing");
    return DAMAGE_TYPE_ALIASES[key] || key;
}

// Only these three inflict a lasting effect when they land a hit.
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
const ELEMENT_STATUS = {
    fire: "burn",
    ice: "freeze",
    poison: "poison",
    lightning: "strike",
    dark: "drain"
};

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
const ALL_CLASSES = ["Fighter", "Rogue", "Wizard", "Cleric"];

const WEAPON_CLASSES = {
    // --- Fighter: heavy blades, axes and polearms
    "Longsword": ["Fighter"],
    "Greatsword": ["Fighter"],
    "Battle Axe": ["Fighter"],
    "Spear": ["Fighter"],
    "Trident": ["Fighter"],
    "Glaive": ["Fighter"],
    "Lucerne Hammer": ["Fighter"],
    "Executioner's Axe": ["Fighter"],
    "Greataxe": ["Fighter"],
    "Maul": ["Fighter"],
    "Claymore": ["Fighter"],
    "Falchion": ["Fighter"],
    "Broadsword": ["Fighter"],
    "Anchor": ["Fighter"],
    "War Sickle": ["Fighter"],
    "Cudgel": ["Fighter"],

    // --- Rogue: finesse blades and thrown daggers
    "Rapier": ["Rogue"],
    "Dagger": ["Rogue"],
    "Shortsword": ["Rogue"],
    "Sabre": ["Rogue"],
    "Scimitar": ["Rogue"],
    "Kris Dagger": ["Rogue"],
    "Viper Fang": ["Rogue"],
    "Venom Dagger": ["Rogue"],
    "Bone Club": ["Rogue"],
    // A runed dagger is both a rogue's blade and a wizard's focus.
    "Runed Dagger": ["Rogue", "Wizard"],

    // --- Wizard: staves and elemental wands
    "Magic Staff": ["Wizard"],
    "Arcane Staff": ["Wizard"],
    "Lampada": ["Wizard"],
    "Ember Blade": ["Wizard"],
    "Frost Staff": ["Wizard"],
    "Storm Wand": ["Wizard"],
    "Plasma Wand": ["Wizard"],

    // --- Cleric: maces, flails and divine tools
    "Quarterstaff": ["Cleric"],
    "War Hammer": ["Cleric"],
    "Mace": ["Cleric"],
    "Flail": ["Cleric"],
    "Bone Wand": ["Cleric"],

    // --- Universal: ranged kit and the plain Wand
    "Shortbow": ALL_CLASSES,
    "Longbow": ALL_CLASSES,
    "Sling": ALL_CLASSES,
    "Dart": ALL_CLASSES,
    "Javelin": ALL_CLASSES,
    "Hand Crossbow": ALL_CLASSES,
    "Light Crossbow": ALL_CLASSES,
    "Crossbow": ALL_CLASSES,
    "Composite Bow": ALL_CLASSES,
    "Heavy Crossbow": ALL_CLASSES,
    "Repeating Crossbow": ALL_CLASSES,
    "Wand": ALL_CLASSES
};

// Classes that may equip this item. Armour, shields and consumables are open to
// everyone; only weapons carry a class restriction, via WEAPON_CLASSES.
function itemClasses(item) {
    if (!item || item.category !== "weapon") return ALL_CLASSES.slice();
    return WEAPON_CLASSES[item.name] || ALL_CLASSES;
}

function usableBy(item, className) {
    return itemClasses(item).indexOf(className) !== -1;
}
