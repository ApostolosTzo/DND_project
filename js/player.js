// player.py - Character creation, stats, equipment and leveling.

const RACES = {
    "Human": { desc: "Versatile and ambitious", bonuses: { STR: 1, DEX: 1, CON: 1, INT: 1, WIS: 1, CHA: 1 } },
    "Elf": { desc: "Graceful and perceptive", bonuses: { DEX: 2, INT: 1 } },
    "Dwarf": { desc: "Tough and resilient", bonuses: { CON: 2, STR: 1 } },
    "Halfling": { desc: "Lucky and nimble", bonuses: { DEX: 2, CHA: 1 } }
};

const CLASSES = {
    "Fighter": { desc: "Master of martial combat", hp: 15, primary: "STR" },
    "Rogue": { desc: "Sneaky and dextrous", hp: 13, primary: "DEX" },
    "Wizard": { desc: "Wielder of arcane magic", hp: 11, primary: "INT" },
    "Cleric": { desc: "Servant of the divine", hp: 13, primary: "WIS" }
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
    this.shield = null;
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
    [this.weapon, this.armor, this.shield].forEach((item) => {
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
    if (this.shield) {
        ac += this.shield.base_ac;
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

Player.prototype.equip_weapon = function (weapon) {
    this.weapon = weapon;
    this.recalc_hp();
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
