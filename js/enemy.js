// enemy.py - Enemy templates, bosses and level scaling.

const TEMPLATES = {
    "Zombie": { hp: 22, ac: 8, dice: "d6", bonus: 1, xp: 50, gold: 5 },
    "Skeleton": { hp: 13, ac: 13, dice: "d6", bonus: 2, xp: 50, gold: 6 },
    "Spider": { hp: 16, ac: 12, dice: "d4", bonus: 1, xp: 50, gold: 4 },
    "Wolf": { hp: 18, ac: 13, dice: "d6", bonus: 2, xp: 50, gold: 6 },
    "Goblin": { hp: 10, ac: 15, dice: "d4", bonus: 1, xp: 30, gold: 8 },
    "Slime": { hp: 20, ac: 7, dice: "d6", bonus: 0, xp: 40, gold: 3 },
    "Ghost": { hp: 18, ac: 11, dice: "d8", bonus: 2, xp: 80, gold: 10 },
    "Demon Lord": { hp: 60, ac: 15, dice: "d10", bonus: 5, xp: 200, gold: 50 },
    "Elder Dragon": { hp: 75, ac: 18, dice: "d12", bonus: 6, xp: 250, gold: 80 }
};

const BOSS_NAMES = ["Demon Lord", "Elder Dragon"];

// Damage types each monster is weak or hard against. This is what makes weapon
// damage types matter: the same longsword that barely scratches a Zombie cuts
// a Skeleton open, because skeletons are all bone.
const VULNERABILITIES = {
    "Zombie": { weak: ["slashing", "piercing"], resist: ["bludgeoning", "force"] },
    "Skeleton": { weak: ["bludgeoning", "piercing"], resist: ["slashing", "fire"] },
    "Spider": { weak: ["fire", "ice"], resist: ["piercing"] },
    "Wolf": { weak: ["piercing"], resist: ["bludgeoning"] },
    "Goblin": { weak: ["slashing"], resist: ["ice"] },
    "Slime": { weak: ["fire", "ice"], resist: ["bludgeoning", "piercing", "slashing"] },
    "Ghost": { weak: ["force", "ice"], resist: ["piercing", "slashing"] },
    "Demon Lord": { weak: ["ice", "piercing"], resist: ["fire", "dark", "force"] },
    "Elder Dragon": { weak: ["piercing", "poison"], resist: ["fire", "slashing"] }
};

// How much damage a hit does when the monster is weak / resistant to its type.
const WEAK_MULTIPLIER = 1.5;
const RESIST_MULTIPLIER = 0.5;

// -----------------------------
// Status effects
// -----------------------------
// Burn and freeze are short and driven by INT; poison sticks until it kills.
const BURN_ROUNDS = 2;
const BURN_DIE = "1d4";
const FREEZE_INT_THRESHOLD = 15;   // at or above this INT, a freeze lasts 2 rounds
const FREEZE_MIN_ROUNDS = 1;
const FREEZE_MAX_ROUNDS = 2;
const POISON_BASE_CHANCE = 0.20;   // +3% per point of DEX
const POISON_CHANCE_PER_DEX = 0.03;
const POISON_MAX_CHANCE = 0.60;
// Poison is never "wearing off" - it runs until the creature is dead.
const POISON_MAX_ROUNDS = 999;

// Rewards are multiplied by these before being rounded to whole numbers.
const XP_REWARD_MULTIPLIER = 1.4;   // +40% XP
const GOLD_REWARD_MULTIPLIER = 1.6; // +60% gold

// Monster -> the quest material it drops.
// Demon Lord and Elder Dragon deliberately drop nothing yet.
const DROPS = {
    "Goblin": "Metal Fragments",
    "Spider": "Web String",
    "Slime": "Slime Ball",
    "Zombie": "Rotten Flesh",
    "Skeleton": "Bone",
    "Wolf": "Fur",
    "Ghost": "Plasma"
};

// Chance a kill drops anything, and how many pieces it is worth.
const DROP_CHANCE = 0.75;
const DROP_MIN = 1;
const DROP_MAX = 3;

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
        poison_damage: 0
    };
};

// "Burn (3)" / "Frozen (1)" / "Poisoned" / "" - shown in the combat log.
Enemy.prototype.status_text = function () {
    const s = this.status;
    const parts = [];
    if (s.freeze_rounds > 0) parts.push("Frozen (" + s.freeze_rounds + ")");
    if (s.burn_rounds > 0) parts.push("Burning (" + s.burn_rounds + ")");
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
// attacker, because fire/ice scale with INT and poison scales with DEX.
Enemy.prototype.inflict_element = function (element, p) {
    if (!element || !p) return "";
    const s = this.status;

    if (element === "fire") {
        s.burn_rounds = BURN_ROUNDS;
        // INT feeds both how long it burns and how hard each tick bites.
        const int_mod = Math.floor((p.effective_stats().INT - 10) / 2);
        s.burn_damage = Math.max(1, roll(BURN_DIE) + Math.max(0, int_mod));
        return " It catches fire (" + s.burn_damage + "/round for " + BURN_ROUNDS + " rounds)!";
    }

    if (element === "ice") {
        const stats = p.effective_stats();
        const rounds = stats.INT >= FREEZE_INT_THRESHOLD ? FREEZE_MAX_ROUNDS : FREEZE_MIN_ROUNDS;
        s.freeze_rounds = Math.max(s.freeze_rounds, rounds);
        return " It is frozen for " + rounds + " round" + (rounds > 1 ? "s" : "") + "!";
    }

    if (element === "poison") {
        const dex = p.effective_stats().DEX;
        const chance = Math.min(POISON_MAX_CHANCE,
            POISON_BASE_CHANCE + POISON_CHANCE_PER_DEX * dex);
        if (Math.random() >= chance) return " The poison did not take.";
        const dex_mod = Math.floor((dex - 10) / 2);
        s.poison_rounds = POISON_MAX_ROUNDS;
        s.poison_damage = Math.max(1, dex_mod);
        return " It is poisoned (" + s.poison_damage + "/round until it dies)!";
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
