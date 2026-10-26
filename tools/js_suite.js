// Behavioural suite for the PWA build: drives the real game.js state machine
// headlessly (game.js has no DOM/fetch dependencies) through the flows a
// player hits - create, shop, fight, element riders, potions, inventory.
//
//   node tools/js_suite.js [repo-root]
//
// Exit code 0 when every check passes. This suite tests the browser build on
// its own; tools/parity_check.py guarantees the Python build computes the
// same values for the same inputs, so green here + green there = both builds
// behave identically.
//
// Determinism: Math.random is frozen during creation and combat (see
// harness.setRandom). randInt(min,max) reads floor(r*(max-min+1))+min, so 0
// makes every roll its minimum and 0.999999 its maximum - the exact numbers
// asserted below are computed from that rule.

"use strict";
const path = require("path");
const { createGame } = require("./harness");

const root = process.argv[2] || path.join(__dirname, "..");

let passed = 0;
const failures = [];

function check(desc, actual, expected) {
    const ok = JSON.stringify(actual) === JSON.stringify(expected);
    if (ok) {
        passed += 1;
    } else {
        failures.push({ desc, actual, expected });
        console.log("FAIL " + desc);
        console.log("  expected: " + JSON.stringify(expected));
        console.log("  actual:   " + JSON.stringify(actual));
    }
}

// A fresh game frozen at RNG max: 4d6-drop-lowest rolls four 6s, drops one,
// Human adds +1, so every stat is 19. CON 19 -> +4 modifier.
function newGame(cls) {
    const g = createGame(root);
    g.setRandom(0.999999);
    g.call("startGame", {
        name: "Testor",
        race: "Human",
        "class": cls || "Fighter"
    });
    g.clearRandom();
    return g;
}

// --- creation --------------------------------------------------------------
{
    const g = newGame();
    const p = g.eval("gs.player");
    check("create: lands in town", g.eval("gs.screen"), "town");
    check("create: every stat is 19 (frozen RNG)", p.stats,
        { STR: 19, DEX: 19, CON: 19, INT: 19, WIS: 19, CHA: 19 });
    check("create: Fighter HP is class 15 + CON+4", p.max_hp, 19);
    // Chainmail 14 + DEX mod +4, capped by the armour's dex_limit of 2.
    check("create: Fighter AC is 14 + capped DEX", p.ac, 16);
    check("create: starts with a Longsword", p.weapon.name, "Longsword");
    check("create: starts in Chainmail", p.armor.name, "Chainmail");
    check("create: 15 starting potions in the bag",
        p.inventory.filter((i) => i.name === "Healing Potion").length, 15);
    check("create: level 1, no gold", [p.level, p.gold], [1, 0]);
}

// --- shop: buy, class gate, gold gate, sell --------------------------------
{
    const g = newGame();
    g.eval("gs.player.add_gold(500)");

    // Real flow: town -> Visit Shop -> Weaponsmith (index 1 of town's stalls).
    g.call("handleAction", 1);
    check("shop: opens the stall list", g.eval("gs.screen"), "shop_select");
    g.call("handleAction", 1);
    check("shop: standing at the Weaponsmith", g.eval("gs.shop_name"), "Weaponsmith");

    g.call("shopBuy", "Longsword", 1);
    check("shop buy: deducts the listed price", g.eval("gs.player.gold"), 470);
    check("shop buy: a second Longsword lands in the bag",
        g.eval("gs.player.inventory.filter(i => i.name === 'Longsword').length"), 1);
    check("shop buy: says what happened",
        g.eval("gs.log[0]"), "Bought 1 \u00d7 Longsword for 30g!");

    // The Wizard's stall sells Ember Blades - a Wizard-only weapon. A Fighter
    // clicking the greyed-out row gets refused by shopBuy itself, not just UI.
    g.call("handleAction", 1);           // shop -> stall list
    g.call("handleAction", 4);           // index 4 = Wizard
    check("shop: standing at the Wizard", g.eval("gs.shop_name"), "Wizard");
    g.call("shopBuy", "Ember Blade", 1);
    check("shop buy: another class's weapon is refused",
        g.eval("gs.log[0]"),
        "Ember Blade is a Wizard weapon - not your class's weapon.");
    check("shop buy: refusal costs no gold", g.eval("gs.player.gold"), 470);

    // Not enough gold.
    g.eval("gs.player.gold = 5");
    g.call("handleAction", 1);
    g.call("handleAction", 1);           // back to the Weaponsmith
    g.call("shopBuy", "Longsword", 1);
    check("shop buy: broke player hears about it",
        g.eval("gs.log[0]"), "Not enough gold! Need 30g, you have 5g.");
    check("shop buy: still broke", g.eval("gs.player.gold"), 5);

    // Sell: 80% of the listed price, one item at a time.
    g.eval("gs.player.add_item(createItem('Dagger'))");
    g.call("sellItem", "Dagger");
    check("sell: pays 80% of shop price (30 -> 24)", g.eval("gs.player.gold"), 29);
    check("sell: removes the item",
        g.eval("gs.player.inventory.some(i => i.name === 'Dagger')"), false);
    check("sell: says what happened", g.eval("gs.log[0]"), "Sold Dagger for 24g.");
}

// --- combat: hit maths, weak multiplier, victory rewards -------------------
{
    const g = newGame();
    g.setRandom(0.999999);               // every roll at maximum
    g.call("handleAction", 0);           // Fight
    check("combat: the fight opens", g.eval("gs.screen"), "combat");
    // The generator's pick is random; pin the monster so the maths below is
    // exact. Enemy construction itself is parity-checked elsewhere.
    g.eval("gs.enemy = new Enemy('Zombie', 1)");

    // The Longsword carries STR+1, so effective STR is 20 (+5). Max 1d8 (8)
    // + 5 + 1 two-handed = 14, and the Zombie is weak to slashing: 14 x 1.5
    // = 21. HP 22 -> 1.
    g.call("playerAttack", false);
    check("combat: weak hit lands for 21", g.eval("gs.enemy.hp"), 1);
    check("combat: floating damage number",
        g.eval("gs.last_damage"), { amount: 21, kind: "hit", weak: true });
    check("combat: the log explains the weakness",
        g.eval("gs.log.join(' ')").indexOf("WEAK to slashing") !== -1, true);
    // The Zombie swings back: d20 max 20 + 2 beats AC 16; d6 max 6 + 1 = 7.
    check("combat: the monster retaliates", g.eval("gs.player.hp"), 12);

    // Finish it: rewards are the Zombie's own drops (8 gold, 35 XP). The
    // material drop needs random() < 0.75, so step down from RNG max first.
    g.setRandom(0.5);
    g.eval("gs.enemy.hp = 1");
    g.call("playerAttack", false);
    check("combat: victory clears the enemy", g.eval("gs.enemy"), null);
    check("combat: loots the gold drop", g.eval("gs.player.gold"), 8);
    check("combat: gains the XP reward", g.eval("gs.player.xp"), 35);
    check("combat: collects the quest material",
        g.eval("gs.player.inventory.some(i => i.name === 'Rotten Flesh')"), true);
}

// --- XP curve and level-up maths -------------------------------------------
{
    const g = newGame();
    check("xp: level 1 needs 100", g.eval("gs.player.xp_to_next()"), 100);
    g.eval("gs.player.level = 7");
    check("xp: level 7 needs 700", g.eval("gs.player.xp_to_next()"), 700);
    g.eval("gs.player.level = 1");

    g.eval("grantXp(gs.player, 100)");   // exactly one level
    check("level up: level increments", g.eval("gs.player.level"), 2);
    check("level up: HP grows by hp_per_level (19 + 4)",
        g.eval("gs.player.max_hp"), 23);
    check("level up: HP fully restored", g.eval("gs.player.hp"), 23);
    check("level up: no leftover XP", g.eval("gs.player.xp"), 0);
    check("level up: finds level x 10 gold", g.eval("gs.player.gold"), 20);
    check("level up: earns a skill point", g.eval("gs.player.skill_points"), 1);
}

// --- element rider: fire catches on a passing chance roll ------------------
{
    // Fire weapons are the Wizard armory's (Ember Blade). INT 19 -> chance
    // 20% + 3% x 19 = 77%, capped at 60%.
    const g = newGame("Wizard");
    g.eval("gs.player.equip_weapon(createItem('Ember Blade'))");
    g.eval("gs.enemy = new Enemy('Zombie', 1)");
    g.setRandom(0.5);                    // d20 reads 11 -> hits; 0.5 < 0.6 -> catch

    g.call("playerAttack", false);
    // The Ember Blade carries INT+1 (effective INT 20). The hit: 1d8 reads 5
    // +4 STR (the blade is no finesse weapon) = 9, fire is neutral on the
    // Zombie -> 22-9 = 13, then the burn ticks at the top of its turn: 1d4
    // reads 3 +5 INT = 8 -> 5.
    check("fire: the hit lands", g.eval("gs.enemy.hp"), 5);
    check("fire: ignites and is recorded", g.eval("gs.enemy.status.burn_rounds"), 1);
    check("fire: burn damage scales on INT", g.eval("gs.enemy.status.burn_damage"), 8);
    check("fire: the log says it caught",
        g.eval("gs.log.join(' ')").indexOf("catches fire") !== -1, true);
    check("fire: burning monster still swings (and misses AC 14)",
        g.eval("gs.player.hp"), 15);
    g.clearRandom();
}

// --- element rider: fire never catches on a failing roll -------------------
{
    const g = newGame("Wizard");
    g.eval("gs.player.equip_weapon(createItem('Ember Blade'))");
    g.eval("gs.enemy = new Enemy('Zombie', 1)");
    g.setRandom(0.999999);               // hits, but 0.999999 >= 0.6 fails the rider

    g.call("playerAttack", false);
    check("fire: failing the chance roll leaves no burn",
        g.eval("gs.enemy.status.burn_rounds"), 0);
    check("fire: the log says so",
        g.eval("gs.log.join(' ')").indexOf("did not catch") !== -1, true);
    g.clearRandom();
}

// --- potions: best-pick, heal, consume -------------------------------------
{
    const g = newGame();
    g.eval("gs.player.hp = 1");
    check("potion: the strongest usable one is offered",
        g.eval("bestUsablePotion(gs.player).name"), "Healing Potion");
    const r = g.call("useItemInCombat", "Healing Potion");
    check("potion: use succeeds", r.ok, true);
    check("potion: heals its listed 10", g.eval("gs.player.hp"), 11);
    check("potion: one is consumed",
        g.eval("gs.player.inventory.filter(i => i.name === 'Healing Potion').length"), 14);

    g.eval("gs.player.hp = gs.player.max_hp");
    check("potion: none offered at full HP",
        g.eval("bestUsablePotion(gs.player)"), null);
}

// --- two-handed weapons lock the off-hand ----------------------------------
{
    const g = newGame();
    // The Longsword needs both hands, so a shield cannot be stowed.
    g.eval("gs.player.equip_offhand(createItem('Shield'))");
    check("two-handed: shield refused while the Longsword is held",
        g.eval("gs.player.offhand"), null);
    check("two-handed: the game says why",
        g.eval("typeof gs.player.offhand_block_reason()"), "string");

    // A one-handed weapon frees the hand...
    g.eval("gs.player.equip_weapon(createItem('Dagger'))");
    g.eval("gs.player.equip_offhand(createItem('Shield'))");
    check("two-handed: shield stows once a hand is free",
        g.eval("gs.player.offhand.name"), "Shield");

    // ...and a two-handed upgrade stows it again into the bag.
    g.eval("gs.player.equip_weapon(createItem('Greatsword'))");
    check("two-handed: the shield is stowed, not lost",
        g.eval("gs.player.offhand"), null);
    check("two-handed: stowed shield goes to the bag",
        g.eval("gs.player.inventory.some(i => i.name === 'Shield')"), true);
    check("two-handed: Greatsword carries its +1 bonus",
        g.eval("twoHandedBonus(gs.player.weapon)"), 1);
}

// --- saving and loading round-trips the run --------------------------------
{
    const g = newGame();
    g.eval("gs.player.add_gold(123); gs.player.hp = 5");
    g.call("save", "suite");
    g.eval("gs.player.gold = 0; gs.player.hp = 1");
    g.call("loadAction", 0);             // the only save in the list
    check("save/load: gold survives", g.eval("gs.player.gold"), 123);
    check("save/load: wounded HP survives", g.eval("gs.player.hp"), 5);
    check("save/load: back in town", g.eval("gs.screen"), "town");
}

// --- report ----------------------------------------------------------------
console.log("");
if (failures.length) {
    console.log("FAILED: " + failures.length + " check(s), " + passed + " passed");
    process.exit(1);
}
console.log("all " + passed + " checks passed");
