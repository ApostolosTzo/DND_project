from ui import menu, show, clear_screen, press_any_key
from dice import roll
from inventory import open_inventory
from items import damage_type, element_of, is_potion, heal_amount, two_handed_bonus

def prof_bonus(level):
    return (level - 1) // 4 + 2

def combat_body(player, enemy):
    """The status line above the menu: enemy, its conditions, then the hero."""
    status = enemy.status_text()
    line = enemy.display()
    if status:
        line += f"\n{status}"
    return f"{line}\nLv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n"


def start_combat(player, enemy):
    while True:
        choice = menu("COMBAT", ["Attack", "Use Item", "Flee"], body=combat_body(player, enemy))

        if choice == 0:
            player_attack(player, enemy)
            if enemy.is_alive():
                # Burn and poison bite before the monster gets to swing back.
                tick_status(player, enemy)
                if not player.is_alive():
                    return False
                if enemy.is_alive():
                    enemy_attack(player, enemy)
        elif choice == 1:
            open_inventory(player)
            if not enemy.is_alive():
                return True
            tick_status(player, enemy)
            if not player.is_alive():
                return False
            if enemy.is_alive():
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
        heavy = two_handed_bonus(player.weapon)
        if player.weapon:
            dmg = roll(player.weapon.damage_dice) + attack_mod + heavy
            if dmg < 1:
                dmg = 1
        else:
            dmg = 1 + attack_mod
            if dmg < 1:
                dmg = 1
        # The weapon's damage type decides how hard this lands: skeletons
        # crumble to bludgeoning, slimes shrug off steel.
        type_name = damage_type(player.weapon.damage_type) if player.weapon else None
        total, note = enemy.apply_damage(dmg, type_name)
        show(f"HIT! Dealt {total} damage!{note} Enemy HP: {enemy.hp}/{enemy.max_hp}")
        effect = enemy.inflict_element(element_of(player.weapon), player)
        if effect:
            show(effect)
    else:
        show("MISS!")

    press_any_key()

def tick_status(player, enemy):
    """Resolves burn/poison damage at the top of the monster's turn."""
    lines = enemy.tick_status()
    if not lines:
        return
    clear_screen()
    show("=== COMBAT ===\n")
    show(combat_body(player, enemy))
    for line in lines:
        show(line)
    press_any_key()


def enemy_attack(player, enemy):
    clear_screen()
    show(f"=== COMBAT ===\n")
    show(combat_body(player, enemy))
    if enemy.is_frozen():
        enemy.status["freeze_rounds"] -= 1
        left = max(0, enemy.status["freeze_rounds"])
        show(f"The {enemy.name} is frozen solid and cannot attack!")
        if left:
            show(f"({left} round{'s' if left > 1 else ''} left)")
        press_any_key()
        return
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