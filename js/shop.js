// shop.py - NPC shop definitions (stock, price and level gate).

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
            "Greatsword": { price: 60, min_level: 3 }
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
            "Dragon Scale": { price: 800, min_level: 10 }
        }
    },
    "Archer": {
        items: {
            "Shortbow": { price: 25, min_level: 1 },
            "Longbow": { price: 75, min_level: 3 },
            "Crossbow": { price: 100, min_level: 5 },
            "Hand Crossbow": { price: 50, min_level: 2 }
        }
    },
    "Wizard": {
        items: {
            "Magic Staff": { price: 30, min_level: 1 },
            "Wand": { price: 40, min_level: 1 },
            "Arcane Staff": { price: 120, min_level: 4 },
            "Wizard Robe": { price: 80, min_level: 2 },
            "Arcane Ring": { price: 200, min_level: 5 },
            "Lampada": { price: 50, min_level: 5 }
        }
    }
};
