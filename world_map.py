#=================================
# World Map Data
#=================================
# This file contains the data for the world map, including locations and their connections.


LOCATIONS = {
    
    "town": {
        "name": "Town",
        "x": 80,
        "y": 180,
        "type": "town",
        "connects_to": ["village1", "village2"],
        "shops": ["Potion Merchant", "Weaponsmith", "Armorer", "Archer", "Wizard"],
    },
    "village1": {
        "name": "Village 1",
        "x": 380,
        "y": 310,
        "type": "village",
        "connects_to": ["town", "dungeon"],
        "shops": ["Potion Merchant", "Weaponsmith", "Armorer"],
    },
    "village2": {
        "name": "Village 2",
        "x": 380,
        "y": 50,
        "type": "village",
        "connects_to": ["town"],
        "shops": ["Potion Merchant"],
    },
    "dungeon": {
        "name": "Dungeon",
        "x": 470,
        "y": 310,
        "type": "dungeon",
        "connects_to": ["village1"],
        "shops": [],
    },
}
