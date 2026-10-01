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
    this.xp_reward = t.xp * (level / 2);
}

Enemy.prototype.display = function () {
    return "Lv." + this.level + " " + this.name + "  HP: " + this.hp + "/" + this.max_hp + "  AC: " + this.ac;
};

Enemy.prototype.gold_drop = function () {
    return TEMPLATES[this.name].gold * this.level;
};

Enemy.prototype.attack_damage = function () {
    return roll(this.damage_dice) + this.damage_bonus;
};

Enemy.prototype.is_alive = function () {
    return this.hp > 0;
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
