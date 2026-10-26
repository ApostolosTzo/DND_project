// enemy.py - Enemy templates, bosses and level scaling.
//
// The tables and the element constants are GENERATED into js/game_data.js from
// enemy.py by tools/gen_js_data.py; the combat behaviour below stays
// hand-written.

const TEMPLATES = GAME_DATA.templates;

const BOSS_NAMES = GAME_DATA.boss_names;

// Damage types each monster is weak or hard against. This is what makes weapon
// damage types matter: the same longsword that barely scratches a Zombie cuts
// a Skeleton open, because skeletons are all bone.
const VULNERABILITIES = GAME_DATA.vulnerabilities;

// How much damage a hit does when the monster is weak / resistant to its type.
const WEAK_MULTIPLIER = GAME_DATA.weak_multiplier;
const RESIST_MULTIPLIER = GAME_DATA.resist_multiplier;

// -----------------------------
// Element effects
// -----------------------------
// Five damage types inflict a lasting effect, and every one of them is *rolled
// for* except dark. That is deliberate: a weapon should be a good investment,
// not a guaranteed effect, so the stat that matters to you decides how often
// the rider actually lands.
//
// Each effect names the stat it scales on, and no two of them share a stat - INT
// drives fire and ice, DEX drives poison, WIS drives lightning and STR drives
// dark. That means your build picks which element you can rely on.
//
//   fire      roll to ignite     20% + 3% per INT, capped at 60%
//   ice       roll to freeze     10% + 1% per 5 INT, capped at 43%
//   poison    roll to poison     20% + 3% per DEX, capped at 60%
//   lightning roll to strike     15% + 1% per 2 WIS, capped at 50%
//   dark      always applies     no chance, but scales on STR instead
//
// Ice is the stingiest on purpose: freezing removes the target's entire turn,
// so a 43% cap keeps it strong rather than overpowered, and +1% per *5* INT
// means only a dedicated caster closes the gap.
//
// The constants are aliased one-for-one from enemy.py, keeping their names, so
// a search for BURN_BASE_CHANCE finds the same identifier in both builds.
const _ER = GAME_DATA.element_rules;

// --- Fire: catches, then burns for two rounds
const BURN_ROUNDS = _ER.BURN_ROUNDS;
const BURN_DIE = _ER.BURN_DIE;
const BURN_BASE_CHANCE = _ER.BURN_BASE_CHANCE;
const BURN_CHANCE_PER_INT = _ER.BURN_CHANCE_PER_INT;
const BURN_MAX_CHANCE = _ER.BURN_MAX_CHANCE;

// --- Ice: no damage at all, but the target loses its whole turn
const FREEZE_BASE_CHANCE = _ER.FREEZE_BASE_CHANCE;
const FREEZE_INT_PER_POINT = _ER.FREEZE_INT_PER_POINT;       // one extra point of chance per this much INT
const FREEZE_CHANCE_PER_INT_BLOCK = _ER.FREEZE_CHANCE_PER_INT_BLOCK;
const FREEZE_MAX_CHANCE = _ER.FREEZE_MAX_CHANCE;
const FREEZE_INT_THRESHOLD = _ER.FREEZE_INT_THRESHOLD;       // at or above this INT, a freeze lasts 2 rounds
const FREEZE_MIN_ROUNDS = _ER.FREEZE_MIN_ROUNDS;
const FREEZE_MAX_ROUNDS = _ER.FREEZE_MAX_ROUNDS;

// --- Poison: the mirror of fire, but on DEX, and it never wears off
const POISON_BASE_CHANCE = _ER.POISON_BASE_CHANCE;
const POISON_CHANCE_PER_DEX = _ER.POISON_CHANCE_PER_DEX;
const POISON_MAX_CHANCE = _ER.POISON_MAX_CHANCE;
// Poison is never "wearing off" - it runs until the creature is dead.
const POISON_MAX_ROUNDS = _ER.POISON_MAX_ROUNDS;

// --- Lightning: the WIS effect, and the hardest-hitting of the short riders
const LIGHTNING_ROUNDS = _ER.LIGHTNING_ROUNDS;
const LIGHTNING_DIE = _ER.LIGHTNING_DIE;
const LIGHTNING_BASE_CHANCE = _ER.LIGHTNING_BASE_CHANCE;
const LIGHTNING_WIS_PER_POINT = _ER.LIGHTNING_WIS_PER_POINT;    // one extra point of chance per this much WIS
const LIGHTNING_CHANCE_PER_WIS_BLOCK = _ER.LIGHTNING_CHANCE_PER_WIS_BLOCK;
const LIGHTNING_MAX_CHANCE = _ER.LIGHTNING_MAX_CHANCE;

// --- Dark: the odd one out. No roll at all, and it scales on STR.
// 1d4 + 1 for every 15 points of STR, so it starts at a flat 1d4 on a 10 STR
// character and only reaches 1d4+2 at STR 30.
const DARK_ROUNDS = _ER.DARK_ROUNDS;
const DARK_DIE = _ER.DARK_DIE;
const DARK_STR_PER_POINT = _ER.DARK_STR_PER_POINT;        // one extra point of damage per this much STR
const DARK_DAMAGE_PER_STR_BLOCK = _ER.DARK_DAMAGE_PER_STR_BLOCK;

// Rewards are multiplied by these before being rounded to whole numbers.
const XP_REWARD_MULTIPLIER = GAME_DATA.xp_reward_multiplier;   // +40% XP
const GOLD_REWARD_MULTIPLIER = GAME_DATA.gold_reward_multiplier; // +60% gold

// Monster -> the quest material it drops.
// Demon Lord and Elder Dragon deliberately drop nothing yet.
const DROPS = GAME_DATA.drops;

// Chance a kill drops anything, and how many pieces it is worth.
const DROP_CHANCE = GAME_DATA.drop_chance;
const DROP_MIN = GAME_DATA.drop_min;
const DROP_MAX = GAME_DATA.drop_max;

function Enemy(name, level) {
    this.name = name;
    this.level = level;
    const t = TEMPLATES[name];

    this.max_hp = t.hp + (level - 1) * 6;
    this.hp = this.max_hp;
    this.ac = t.ac + Math.floor((level - 1) / 3);
    const num_dice = Math.floor((level - 1) / 4) + 1;
    this.damage_dice = num_dice + t.dice;
    this.damage_bonus = t.bonus + Math.floor((level - 1) / 2);
    // Math.floor keeps the reward a whole number - without it floating point
    // would show things like "35.000000000000004 XP" in the log.
    this.xp_reward = Math.floor(t.xp * (level / 2) * XP_REWARD_MULTIPLIER);

    const vuln = VULNERABILITIES[name] || { weak: [], resist: [] };
    this.weak_to = vuln.weak.slice();
    this.resists = vuln.resist.slice();
    this.clear_status();
}

// Resets the status track. Called on spawn and before each new fight so a
// poisoned corpse can never bleed its condition into the next monster.
Enemy.prototype.clear_status = function () {
    this.status = {
        burn_rounds: 0,
        burn_damage: 0,
        freeze_rounds: 0,
        poison_rounds: 0,
        poison_damage: 0,
        strike_rounds: 0,
        strike_damage: 0,
        drain_rounds: 0,
        drain_damage: 0
    };
};

// "Burn (3)" / "Frozen (1)" / "Poisoned" / "" - shown in the combat log.
Enemy.prototype.status_text = function () {
    const s = this.status;
    const parts = [];
    if (s.freeze_rounds > 0) parts.push("Frozen (" + s.freeze_rounds + ")");
    if (s.burn_rounds > 0) parts.push("Burning (" + s.burn_rounds + ")");
    if (s.strike_rounds > 0) parts.push("Struck (" + s.strike_rounds + ")");
    if (s.drain_rounds > 0) parts.push("Draining (" + s.drain_rounds + ")");
    if (s.poison_rounds > 0) parts.push("Poisoned");
    return parts.join(", ");
};

Enemy.prototype.is_frozen = function () {
    return this.status.freeze_rounds > 0;
};

// 1.5x weak, 0.5x resistant, 1x otherwise. Always at least 1 so a resisted
// hit still registers as a hit rather than silently doing nothing.
Enemy.prototype.damage_multiplier = function (type) {
    if (!type) return 1;
    if (this.weak_to.indexOf(type) !== -1) return WEAK_MULTIPLIER;
    if (this.resists.indexOf(type) !== -1) return RESIST_MULTIPLIER;
    return 1;
};

// Returns the extra damage and the note for the log, e.g. " - WEAK (x1.5)".
// Plain code means no weakness line at all.
Enemy.prototype.apply_damage = function (amount, type) {
    const mult = this.damage_multiplier(type);
    const total = Math.max(1, Math.round(amount * mult));
    this.take_damage(total);
    let note = "";
    if (mult === WEAK_MULTIPLIER) note = " - WEAK to " + type + " (x1.5)";
    else if (mult === RESIST_MULTIPLIER) note = " - resists " + type + " (x0.5)";
    return { total: total, note: note };
};

// Applies the element carried by a weapon that just landed a hit. `p` is the
// attacker, because every element scales off one of the attacker's stats.
// Each element has its own chance roll; a failed roll costs nothing.
Enemy.prototype.inflict_element = function (element, p) {
    if (!element || !p) return "";
    const s = this.status;
    const stats = p.effective_stats();

    if (element === "fire") {
        const chance = Math.min(BURN_MAX_CHANCE,
            BURN_BASE_CHANCE + BURN_CHANCE_PER_INT * stats.INT);
        if (Math.random() >= chance) return " The fire did not catch.";
        s.burn_rounds = BURN_ROUNDS;
        const int_mod = Math.floor((stats.INT - 10) / 2);
        s.burn_damage = Math.max(1, roll(BURN_DIE) + Math.max(0, int_mod));
        return " It catches fire (" + s.burn_damage + "/round for " + BURN_ROUNDS + " rounds)!";
    }

    if (element === "ice") {
        const chance = Math.min(FREEZE_MAX_CHANCE,
            FREEZE_BASE_CHANCE
            + FREEZE_CHANCE_PER_INT_BLOCK * Math.floor(stats.INT / FREEZE_INT_PER_POINT));
        if (Math.random() >= chance) return " The ice did not freeze it.";
        const rounds = stats.INT >= FREEZE_INT_THRESHOLD ? FREEZE_MAX_ROUNDS : FREEZE_MIN_ROUNDS;
        s.freeze_rounds = Math.max(s.freeze_rounds, rounds);
        return " It is frozen for " + rounds + " round" + (rounds > 1 ? "s" : "") + "!";
    }

    if (element === "poison") {
        const dex = stats.DEX;
        const chance = Math.min(POISON_MAX_CHANCE,
            POISON_BASE_CHANCE + POISON_CHANCE_PER_DEX * dex);
        if (Math.random() >= chance) return " The poison did not take.";
        const dex_mod = Math.floor((dex - 10) / 2);
        s.poison_rounds = POISON_MAX_ROUNDS;
        s.poison_damage = Math.max(1, dex_mod);
        return " It is poisoned (" + s.poison_damage + "/round until it dies)!";
    }

    if (element === "lightning") {
        const chance = Math.min(LIGHTNING_MAX_CHANCE,
            LIGHTNING_BASE_CHANCE
            + LIGHTNING_CHANCE_PER_WIS_BLOCK * Math.floor(stats.WIS / LIGHTNING_WIS_PER_POINT));
        if (Math.random() >= chance) return " The lightning misses.";
        s.strike_rounds = LIGHTNING_ROUNDS;
        const wis_mod = Math.floor((stats.WIS - 10) / 2);
        s.strike_damage = Math.max(1, roll(LIGHTNING_DIE) + Math.max(0, wis_mod));
        return " It is struck by lightning (" + s.strike_damage + "/round for "
            + LIGHTNING_ROUNDS + " rounds)!";
    }

    if (element === "dark") {
        // Dark has no chance roll on purpose - it is the one rider that is
        // guaranteed, and it pays for that by being weak and STR-scaled.
        s.drain_rounds = DARK_ROUNDS;
        s.drain_damage = Math.max(1, roll(DARK_DIE)
            + DARK_DAMAGE_PER_STR_BLOCK * Math.floor(stats.STR / DARK_STR_PER_POINT));
        return " It is drained of life (" + s.drain_damage + "/round for "
            + DARK_ROUNDS + " rounds)!";
    }

    return "";
};

// One round of damage-over-time and the frozen check. Returns log lines.
Enemy.prototype.tick_status = function () {
    const s = this.status;
    const lines = [];
    if (s.burn_rounds > 0) {
        this.take_damage(s.burn_damage);
        s.burn_rounds -= 1;
        lines.push(this.name + " burns for " + s.burn_damage + " damage.");
    }
    if (s.strike_rounds > 0) {
        this.take_damage(s.strike_damage);
        s.strike_rounds -= 1;
        lines.push(this.name + " is struck for " + s.strike_damage + " damage.");
    }
    if (s.drain_rounds > 0) {
        this.take_damage(s.drain_damage);
        s.drain_rounds -= 1;
        lines.push(this.name + " is drained for " + s.drain_damage + " damage.");
    }
    if (s.poison_rounds > 0) {
        this.take_damage(s.poison_damage);
        s.poison_rounds -= 1;
        lines.push(this.name + " suffers " + s.poison_damage + " poison damage.");
    }
    if (s.freeze_rounds > 0) s.freeze_rounds -= 1;
    return lines;
};

Enemy.prototype.display = function () {
    return "Lv." + this.level + " " + this.name + "  HP: " + this.hp + "/" + this.max_hp + "  AC: " + this.ac;
};

Enemy.prototype.gold_drop = function () {
    return Math.floor(TEMPLATES[this.name].gold * this.level * GOLD_REWARD_MULTIPLIER);
};

Enemy.prototype.attack_damage = function () {
    return roll(this.damage_dice) + this.damage_bonus;
};

Enemy.prototype.is_alive = function () {
    return this.hp > 0;
};

// Quest material dropped on death, or null. Returns [material, count].
Enemy.prototype.roll_drop = function () {
    const material = DROPS[this.name];
    if (!material) return null;
    if (Math.random() >= DROP_CHANCE) return null;
    return [material, randInt(DROP_MIN, DROP_MAX)];
};

Enemy.prototype.take_damage = function (amount) {
    this.hp -= amount;
    if (this.hp < 0) this.hp = 0;
};

function nonBossNames() {
    return Object.keys(TEMPLATES).filter((t) => BOSS_NAMES.indexOf(t) === -1);
}

// Overworld enemies: level is within 2 of the player's level (floor 1-2 -> level 1).
function generateEnemy(player_level) {
    let enemy_level;
    if (player_level <= 2) {
        enemy_level = 1;
    } else {
        enemy_level = randInt(player_level - 2, player_level);
    }
    const names = nonBossNames();
    const name = names[randInt(0, names.length - 1)];
    return new Enemy(name, enemy_level);
}

// Dungeon enemies scale with the floor; floor 10 always spawns a boss.
function generateDungeonEnemy(floor, player_level) {
    let name, enemy_level;
    if (floor === 10) {
        name = BOSS_NAMES[randInt(0, BOSS_NAMES.length - 1)];
        enemy_level = player_level + 2;
    } else {
        const names = nonBossNames();
        name = names[randInt(0, names.length - 1)];
        enemy_level = player_level + Math.floor(floor / 2);
    }
    return new Enemy(name, enemy_level);
}
