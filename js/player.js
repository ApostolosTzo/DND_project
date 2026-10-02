// player.py - Character creation, stats, equipment and leveling.

const RACES = {
    "Human": { desc: "Versatile and ambitious", bonuses: { STR: 1, DEX: 1, CON: 1, INT: 1, WIS: 1, CHA: 1 } },
    "Elf": { desc: "Graceful and perceptive", bonuses: { DEX: 2, INT: 2 } },
    "Dwarf": { desc: "Tough and resilient", bonuses: { CON: 3, STR: 2 } },
    "Halfling": { desc: "Lucky and nimble", bonuses: { DEX: 2, CHA: 1 } }
};

// NOTE: every class declares a `bonuses` key, but nothing reads it yet - not
// makeCharacter() here and not make_character() in player.py. It is mirrored
// from player.py verbatim so the two builds agree, and it is inert in both.
// Wiring it up means adding CLASSES[class_name].bonuses to the stat roll in
// both character factories.
const CLASSES = {
    "Fighter": { desc: "Master of martial combat", hp: 15, primary: "STR", bonuses: { STR: 2 } },
    "Rogue": { desc: "Sneaky and dextrous", hp: 13, primary: "DEX", bonuses: { DEX: 2 } },
    "Wizard": { desc: "Wielder of arcane magic", hp: 11, primary: "INT", bonuses: { INT: 2 } },
    "Cleric": { desc: "Servant of the divine", hp: 13, primary: "WIS", bonuses: { WIS: 2 } }
};

const STAT_ORDER = ["STR", "DEX", "CON", "INT", "WIS", "CHA"];

function Player(name, race, class_name, stats) {
    this.name = name;
    this.race = race;
    this.class_name = class_name;
    this.level = 1;
    this.xp = 0;
    this.stats = stats;
    // Equipment must exist before any calculation reads it.
    this.weapon = null;
    this.armor = null;
    this.offhand = null;
    this.max_hp = CLASSES[class_name].hp + this.modifier("CON");
    this.hp = this.max_hp;
    this.inventory = [];
    this.gold = 0;
    this.current_save = null;
    this.skill_points = 0;
    this.ac = this.calc_ac();
}

Player.prototype.get_equipment_stat_bonus = function () {
    const bonus = {};
    [this.weapon, this.armor, this.offhand].forEach((item) => {
        if (item) {
            for (const stat in item.stats_bonus) {
                bonus[stat] = (bonus[stat] || 0) + item.stats_bonus[stat];
            }
        }
    });
    return bonus;
};

Player.prototype.effective_stats = function () {
    const stats = Object.assign({}, this.stats);
    const bonus = this.get_equipment_stat_bonus();
    for (const stat in bonus) {
        stats[stat] = (stats[stat] || 0) + bonus[stat];
    }
    return stats;
};

Player.prototype.modifier = function (stat) {
    return Math.floor((this.effective_stats()[stat] - 10) / 2);
};

Player.prototype.calc_ac = function () {
    let ac;
    if (this.armor) {
        ac = this.armor.base_ac;
        if (this.armor.armor_type === "light") {
            ac += this.modifier("DEX");
        } else if (this.armor.armor_type === "medium") {
            ac += Math.min(this.modifier("DEX"), 2);
        }
    } else {
        ac = 10 + this.modifier("DEX");
    }
    // Only a shield in the off-hand adds AC. A second weapon is dead weight.
    if (this.offhand && this.offhand.armor_type === "shield") {
        ac += this.offhand.base_ac;
    }
    return ac;
};

Player.prototype.recalc_hp = function () {
    let total = CLASSES[this.class_name].hp;
    for (let lvl = 2; lvl <= this.level; lvl++) {
        total += this.hp_per_level();
    }
    total += this.modifier("CON") * this.level;
    this.max_hp = total;
    if (this.hp > this.max_hp) {
        this.hp = this.max_hp;
    }
};

// True when both hands are already spoken for: either a two-handed weapon is
// equipped, or the off-hand slot is occupied. This is the single check the UI
// and the inventory both ask before handing over a second item.
Player.prototype.hands_full = function () {
    return isTwoHanded(this.weapon) || this.offhand !== null;
};

// Why the off-hand is unavailable, for the UI to explain the refusal.
Player.prototype.offhand_block_reason = function () {
    if (isTwoHanded(this.weapon)) {
        return this.weapon.name + " is two-handed - it needs both hands.";
    }
    if (this.offhand) {
        return "Your off-hand already holds " + this.offhand.name + ".";
    }
    return "";
};

// Shields and one-handed weapons are allowed in the off-hand; a two-handed
// weapon never is. A shield is refused outright while a two-handed weapon is
// equipped, which is the rule the player asked for.
Player.prototype.can_equip_offhand = function (item) {
    if (!item) return false;
    if (isTwoHanded(this.weapon)) return false;
    if (isTwoHanded(item)) return false;
    return true;
};

// Stows the current off-hand back in the bag and returns it, or null.
Player.prototype.stow_offhand = function () {
    const old = this.offhand;
    if (old) {
        this.offhand = null;
        this.inventory.push(old);
    }
    this.ac = this.calc_ac();
    return old;
};

// Equipping a two-handed weapon gives the off-hand back automatically rather
// than silently dropping it or leaving an illegal shield equipped.
Player.prototype.equip_weapon = function (weapon) {
    this.weapon = weapon;
    if (isTwoHanded(weapon)) {
        this.stow_offhand();
    } else {
        this.ac = this.calc_ac();
    }
    this.recalc_hp();
};

Player.prototype.equip_offhand = function (item) {
    if (!this.can_equip_offhand(item)) return false;
    this.stow_offhand();
    this.offhand = item;
    this.ac = this.calc_ac();
    this.recalc_hp();
    return true;
};

Player.prototype.equip_armor = function (armor) {
    this.armor = armor;
    this.ac = this.calc_ac();
    this.recalc_hp();
};

Player.prototype.add_item = function (item) {
    this.inventory.push(item);
};

Player.prototype.is_alive = function () {
    return this.hp > 0;
};

Player.prototype.remove_item = function (item) {
    const idx = this.inventory.indexOf(item);
    if (idx !== -1) {
        this.inventory.splice(idx, 1);
    }
};

Player.prototype.add_gold = function (amount) {
    this.gold += amount;
};

Player.prototype.spend_gold = function (amount) {
    if (this.gold >= amount) {
        this.gold -= amount;
        return true;
    }
    return false;
};

Player.prototype.hp_per_level = function () {
    const base = CLASSES[this.class_name].hp;
    if (base >= 10) return 4;
    if (base >= 8) return 3;
    return 2;
};

Player.prototype.xp_to_next = function () {
    return this.level * 100;
};

Player.prototype.sheet = function () {
    const lines = [];
    lines.push("Name:  " + this.name);
    lines.push("Race:  " + this.race);
    lines.push("Class: " + this.class_name + " (Lv." + this.level + ")");
    lines.push("HP:    " + this.hp + "/" + this.max_hp);
    lines.push("AC:    " + this.ac);
    lines.push("Gold:  " + this.gold);
    lines.push("Weapon: " + (this.weapon ? this.weapon.name : "None"));
    lines.push("Armor:  " + (this.armor ? this.armor.name : "None"));
    lines.push("Offhand: " + (this.offhand ? this.offhand.name : "None"));
    lines.push("");
    STAT_ORDER.forEach((s) => {
        const mod = this.modifier(s);
        const sign = mod >= 0 ? "+" : "";
        const val = String(this.stats[s]);
        lines.push("  " + s + ": " + " ".repeat(Math.max(0, 2 - val.length)) + val +
            " (" + sign + mod + ")");
    });
    return lines.join("\n");
};

// Creates a character with rolled stats, race bonuses and starting gear.
function makeCharacter(name, race, class_name) {
    const rawStats = STAT_ORDER.map(() => roll4d6DropLowest());
    const stats = {};

    if (race === "Human") {
        STAT_ORDER.forEach((s, i) => { stats[s] = rawStats[i] + 1; });
    } else {
        STAT_ORDER.forEach((s, i) => { stats[s] = rawStats[i]; });
        const bonuses = RACES[race].bonuses;
        for (const s in bonuses) {
            stats[s] += bonuses[s];
        }
    }

    const player = new Player(name, race, class_name, stats);

    const gear = STARTING_GEAR[class_name];
    if (gear.weapon) player.equip_weapon(createItem(gear.weapon));
    if (gear.armor) player.equip_armor(createItem(gear.armor));
    gear.items.forEach((item_name) => player.add_item(createItem(item_name)));

    return player;
}

// Race/class data for the character creation form.
function createFormData() {
    const races = Object.keys(RACES).map((r) => {
        const bonuses = RACES[r].bonuses;
        const bonus_str = Object.keys(bonuses).map((s) => s + "+" + bonuses[s]).join(", ");
        return [r, r + " - " + RACES[r].desc, bonus_str];
    });
    const classes = Object.keys(CLASSES).map((c) => [
        c, c + " - " + CLASSES[c].desc, CLASSES[c].hp, CLASSES[c].primary
    ]);
    return { races: races, classes: classes };
}
