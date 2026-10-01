// dice.py - Dice rolling engine (NdX+Y notation)
//
//   roll("1d20")        -> 1-20
//   roll("2d6+3")       -> 5-15
//   roll("3d4-1")       -> 2-11
//   roll4d6DropLowest() -> 3-18 (character stats)

function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function roll(diceStr) {
    diceStr = String(diceStr);
    let dicePart, bonus;

    if (diceStr.indexOf("+") !== -1) {
        const parts = diceStr.split("+");
        dicePart = parts[0];
        bonus = parseInt(parts[1], 10);
    } else if (diceStr.indexOf("-") !== -1) {
        const idx = diceStr.indexOf("-");
        dicePart = diceStr.slice(0, idx);
        bonus = -parseInt(diceStr.slice(idx + 1), 10);
    } else {
        dicePart = diceStr;
        bonus = 0;
    }

    const parts = dicePart.split("d");
    const num = parseInt(parts[0], 10);
    const sides = parseInt(parts[1], 10);

    let total = 0;
    for (let i = 0; i < num; i++) {
        total += randInt(1, sides);
    }
    return total + bonus;
}

// D&D stat generation: 4d6, drop the lowest, sum the rest.
function roll4d6DropLowest() {
    const rolls = [0, 1, 2, 3].map(() => randInt(1, 6));
    const min = Math.min.apply(null, rolls);
    rolls.splice(rolls.indexOf(min), 1);
    return rolls.reduce((a, b) => a + b, 0);
}
