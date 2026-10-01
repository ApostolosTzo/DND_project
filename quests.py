# quests.py - Repeatable quest givers (Town only).
#
# Three NPCs, each with a couple of repeatable jobs. Kill the right monsters,
# collect the material, take it back to the same NPC for gold and XP. Quests can
# be handed in again once you have more of the material.
#
# Their names are rolled fresh each time a new run starts, so no two campaigns
# have the same quest givers.

import random

# First names and epithets used to name the NPCs.
FIRST_NAMES = [
    "Aldric", "Bramble", "Corvin", "Dagny", "Edda", "Fennick", "Gerta",
    "Hollis", "Ivor", "Juna", "Kestrel", "Lyra", "Mabon", "Nell",
    "Orin", "Pike", "Quill", "Rowan", "Sable", "Thistle", "Ulric",
    "Vespa", "Wren", "Yarrow", "Zeb",
]
EPITHETS = [
    "the Alchemist", "the Bone Collector", "the Trapper", "the Tanner",
    "the Reagent Broker", "the Pelt Merchant", "the Curio Dealer",
    "the Wandering Scribe", "the Butcher", "the Herbalist",
]

# Each quest: which NPC offers it, the material, how many, and the payout.
QUESTS = [
    {"npc": 0, "material": "Plasma", "amount": 8, "gold": 260, "xp": 140},
    {"npc": 0, "material": "Slime Ball", "amount": 8, "gold": 220, "xp": 120},
    {"npc": 1, "material": "Bone", "amount": 10, "gold": 300, "xp": 160},
    {"npc": 1, "material": "Rotten Flesh", "amount": 8, "gold": 200, "xp": 110},
    {"npc": 2, "material": "Fur", "amount": 10, "gold": 280, "xp": 150},
    {"npc": 2, "material": "Web String", "amount": 8, "gold": 210, "xp": 115},
    {"npc": 2, "material": "Metal Fragments", "amount": 10, "gold": 320, "xp": 170},
]

NPC_COUNT = 3


def roll_quest_npcs():
    """Roll three NPC names, one per quest giver slot."""
    firsts = random.sample(FIRST_NAMES, NPC_COUNT)
    epithets = random.sample(EPITHETS, NPC_COUNT)
    return [{"name": f + " " + e} for f, e in zip(firsts, epithets)]


def quests_for(npc_index):
    """Every quest offered by one NPC, in order."""
    return [dict(q, index=i) for i, q in enumerate(QUESTS) if q["npc"] == npc_index]