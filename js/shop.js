// shop.py - NPC shop definitions (stock, price and level gate).
//
// NPCs pay SELL_RATIO under the cheapest price an item sells for.

const SELL_RATIO = 0.8;

// What an NPC pays for one of these, or null if nobody sells it.
// Quest materials are never sellable - they are only worth turning in.
function sellPrice(itemName) {
    const item = createItem(itemName);
    if (!item || isMaterial(item)) return null;
    let cheapest = null;
    Object.keys(SHOP_NPCS).forEach((s) => {
        const entry = SHOP_NPCS[s].items[itemName];
        if (entry && (cheapest === null || entry.price < cheapest)) cheapest = entry.price;
    });
    if (cheapest === null) return null;
    return Math.floor(cheapest * SELL_RATIO);
}

const SHOP_NPCS = {
    "Potion Merchant": {
        items: {
            "Healing Potion": { price: 15, min_level: 1 },
            "Greater Healing Potion": { price: 50, min_level: 5 }
        }
    },
    "Weaponsmith": {
        items: {
            "Dagger": { price: 10, min_level: 1 },
            "Spear": { price: 15, min_level: 1 },
            "Mace": { price: 20, min_level: 1 },
            "Quarterstaff": { price: 15, min_level: 1 },
            "Longsword": { price: 30, min_level: 1 },
            "Battle Axe": { price: 35, min_level: 1 },
            "War Hammer": { price: 40, min_level: 2 },
            "Flail": { price: 35, min_level: 2 },
            "Greatsword": { price: 60, min_level: 3 },
                   "Shortsword": { price: 25, min_level: 1 },
            "Sabre": { price: 45, min_level: 2 },
            "Scimitar": { price: 50, min_level: 3 },
            "Claymore": { price: 90, min_level: 4 },
            "Falchion": { price: 85, min_level: 4 },
            "Trident": { price: 30, min_level: 2 },
            "Glaive": { price: 95, min_level: 5 },
            "Lucerne Hammer": { price: 110, min_level: 5 },
            "Greataxe": { price: 130, min_level: 6 },
            "Maul": { price: 140, min_level: 7 },
            "War Sickle": { price: 55, min_level: 3 },
            "Kris Dagger": { price: 70, min_level: 4 },
            "Broadsword": { price: 75, min_level: 4 },
            "Cudgel": { price: 12, min_level: 1 },
            "Bone Club": { price: 18, min_level: 1 },
            "Anchor": { price: 60, min_level: 3 },
            "Executioner's Axe": { price: 100, min_level: 5 },
            "Viper Fang": { price: 80, min_level: 4 },
 
}
    },
    "Armorer": {
        items: {
            "Leather": { price: 20, min_level: 1 },
            "Studded Leather": { price: 45, min_level: 2 },
            "Hide": { price: 30, min_level: 1 },
            "Chainmail": { price: 100, min_level: 1 },
            "Scale Mail": { price: 120, min_level: 2 },
            "Breastplate": { price: 150, min_level: 3 },
            "Half Plate": { price: 200, min_level: 4 },
            "Ring Mail": { price: 80, min_level: 1 },
            "Shield": { price: 25, min_level: 1 },
            "Plate": { price: 300, min_level: 4 },
            "Splint": { price: 350, min_level: 5 },
            "Titanium": { price: 500, min_level: 7 },
            "Dragon Scale": { price: 800, min_level: 10 },
                   "Padded Armor": { price: 25, min_level: 1 },
            "Nomad Leather": { price: 40, min_level: 2 },
            "Doublet": { price: 70, min_level: 3 },
            "Shadowcloth": { price: 190, min_level: 6 },
            "Wolf Hide Armor": { price: 95, min_level: 4 },
            "Robe of Silk": { price: 110, min_level: 3 },
            "Mithral Leather": { price: 230, min_level: 7 },
            "Elven Cloak Armor": { price: 210, min_level: 6 },
            "Riveted Leather": { price: 55, min_level: 2 },
            "Padded Mail": { price: 60, min_level: 2 },
            "Ironweave Mail": { price: 165, min_level: 5 },
            "Bone Lacquer": { price: 320, min_level: 8 },
            "Goblinforged Mail": { price: 250, min_level: 6 },
            "Enchanted Hide": { price: 285, min_level: 7 },
            "Lamellar Armor": { price: 260, min_level: 7 },
            "Ward Mail": { price: 240, min_level: 6 },
            "Banded Mail": { price: 190, min_level: 5 },
            "Steel Plate": { price: 390, min_level: 8 },
            "Obsidian Plate": { price: 620, min_level: 9 },
            "Mithral Plate": { price: 700, min_level: 10 },
            "Warden Plate": { price: 520, min_level: 9 },
            "Dragonbone Plate": { price: 760, min_level: 10 },
            "Titanforged Plate": { price: 640, min_level: 9 },
            "Barrier Plate": { price: 900, min_level: 11 },
            "Ancient Scale Plate": { price: 1100, min_level: 12 },
            "Buckler": { price: 20, min_level: 1 },
            "Bronze Shield": { price: 45, min_level: 2 },
            "Runed Shield": { price: 150, min_level: 5 },
            "Warden's Bulwark": { price: 340, min_level: 8 },
            "Bulwark of Dawn": { price: 480, min_level: 10 },
 
}
    },
    "Archer": {
        items: {
            "Shortbow": { price: 25, min_level: 1 },
            "Longbow": { price: 75, min_level: 3 },
            "Crossbow": { price: 100, min_level: 5 },
            "Hand Crossbow": { price: 50, min_level: 2 },
                   "Sling": { price: 15, min_level: 1 },
            "Dart": { price: 20, min_level: 1 },
            "Javelin": { price: 35, min_level: 2 },
            "Light Crossbow": { price: 65, min_level: 3 },
            "Heavy Crossbow": { price: 140, min_level: 6 },
            "Composite Bow": { price: 120, min_level: 5 },
            "Repeating Crossbow": { price: 260, min_level: 9 },
 
}
    },
    "Wizard": {
        items: {
            "Magic Staff": { price: 30, min_level: 1 },
            "Wand": { price: 40, min_level: 1 },
            "Arcane Staff": { price: 120, min_level: 4 },
            "Wizard Robe": { price: 80, min_level: 2 },
            "Arcane Ring": { price: 200, min_level: 5 },
            "Lampada": { price: 50, min_level: 5 },
                   "Ember Blade": { price: 180, min_level: 5 },
            "Frost Staff": { price: 340, min_level: 8 },
            "Storm Wand": { price: 200, min_level: 6 },
            "Bone Wand": { price: 150, min_level: 5 },
            "Runed Dagger": { price: 150, min_level: 5 },
 
}
    }
};
