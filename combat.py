from ui import menu, show, clear_screen, press_any_key
from dice import roll
from inventory import open_inventory

def prof_bonus(level):
    return (level - 1) // 4 + 2

def start_combat(player, enemy):
    while True:
        body = f"{enemy.display()}\nLv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n"
        choice = menu("COMBAT", ["Attack", "Use Item", "Flee"], body=body)

        if choice == 0:
            player_attack(player, enemy)
            if enemy.is_alive():
                enemy_attack(player, enemy)
        elif choice == 1:
            open_inventory(player)
            if not enemy.is_alive():
                return True
            enemy_attack(player, enemy)
        elif choice == 2:
            if roll("1d20") >= 10:
                clear_screen()
                show(f"=== COMBAT ===\n")
                show(f"{enemy.display()}")
                show(f"Lv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n")
                show("You fled successfully!")
                press_any_key()
                return True
            else:
                clear_screen()
                show(f"=== COMBAT ===\n")
                show(f"{enemy.display()}")
                show(f"Lv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n")
                show("Failed to flee!")
                press_any_key()
                enemy_attack(player, enemy)

        if not player.is_alive():
            return False
        if not enemy.is_alive():
            reward_player(player, enemy)
            return True

def player_attack(player, enemy):
    clear_screen()
    show(f"=== COMBAT ===\n")
    show(f"{enemy.display()}")
    show(f"Lv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n")
    show(f"You attack the {enemy.name}!\n")

    if player.weapon and "finesse" in player.weapon.properties:
        attack_mod = player.modifier("DEX")
    elif player.weapon and "ranged" in player.weapon.properties:
        attack_mod = player.modifier("DEX")
    else:
        attack_mod = player.modifier("STR")

    atk_roll = roll("1d20") + prof_bonus(player.level) + attack_mod
    show(f"d20 + {prof_bonus(player.level)} + {attack_mod} = {atk_roll} vs AC {enemy.ac}")

    if atk_roll >= enemy.ac:
        dmg = 0
        if player.weapon:
            dmg = roll(player.weapon.damage_dice) + attack_mod
            if dmg < 1:
                dmg = 1
        else:
            dmg = 1 + attack_mod
            if dmg < 1:
                dmg = 1
        enemy.take_damage(dmg)
        show(f"HIT! Dealt {dmg} damage! Enemy HP: {enemy.hp}/{enemy.max_hp}")
    else:
        show("MISS!")

    press_any_key()

def enemy_attack(player, enemy):
    clear_screen()
    show(f"=== COMBAT ===\n")
    show(f"{enemy.display()}")
    show(f"Lv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n")
    show(f"The {enemy.name} attacks you!\n")

    enemy_bonus = enemy.level // 2 + 2
    atk_roll = roll("1d20") + enemy_bonus
    show(f"d20 + {enemy_bonus} = {atk_roll} vs your AC {player.ac}")

    if atk_roll >= player.ac:
        dmg = enemy.attack_damage()
        if dmg < 1:
            dmg = 1
        player.hp -= dmg
        if player.hp < 0:
            player.hp = 0
        show(f"HIT! You take {dmg} damage! Your HP: {player.hp}/{player.max_hp}")
    else:
        show("The enemy MISSED!")

    press_any_key()

def reward_player(player, enemy):
    clear_screen()
    show(f"{enemy.name} defeated!\n")
    gold = enemy.gold_drop()
    player.add_gold(gold)
    show(f"Looted {gold} gold!")
    xp = enemy.xp_reward
    show(f"Gained {xp} XP!")
    press_any_key()
    player.add_xp(xp)
