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
    "Longsword": new Weapon("Longsword", "1d8", "slashing", ["versatile"], { STR: 1 }),
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
    "Greater Healing Potion": new Item("Greater Healing Potion", "Restores 20 HP", "heal_strong"),

    // Items (scrolls - future use)
    "Scroll of Fireball": new Item("Scroll of Fireball", "Deals fire damage (future use)", "scroll_fireball"),
    "Scroll of Healing": new Item("Scroll of Healing", "Heals ally (future use)", "scroll_heal"),

    // Items (misc)
    "Arcane Ring": new Item("Arcane Ring", "A ring humming with magic", null, { INT: 1 })
};

const STARTING_GEAR = {
    "Fighter": { weapon: "Longsword", armor: "Chainmail", items: ["Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion"] },
    "Rogue": { weapon: "Dagger", armor: "Leather", items: ["Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion"] },
    "Wizard": { weapon: "Magic Staff", armor: null, items: ["Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion"] },
    "Cleric": { weapon: "Mace", armor: "Plate", items: ["Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion", "Healing Potion"] }
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
