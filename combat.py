from ui import menu, show, clear_screen, press_any_key
from dice import roll
from inventory import open_inventory
from items import damage_type, element_of, is_potion, heal_amount, two_handed_bonus

def prof_bonus(level):
    return (level - 1) // 4 + 2

# Half damage, rounded down, never less than 1.
OFFHAND_DAMAGE_DIVISOR = 2

def weapon_mod(player, weapon):
    """Which stat an attack with this weapon uses."""
    if weapon and ("finesse" in weapon.properties or "ranged" in weapon.properties):
        return player.modifier("DEX")
    return player.modifier("STR")

def combat_body(player, enemy):
    """The status line above the menu: enemy, its conditions, then the hero."""
    status = enemy.status_text()
    line = enemy.display()
    if status:
        line += f"\n{status}"
    return f"{line}\nLv.{player.level} {player.name}  HP: {player.hp}/{player.max_hp}  AC: {player.ac}\n"


def has_offhand_weapon(player):
    """A weapon in the off-hand gets its own attack this turn.

    A shield is not a weapon, so it contributes no extra swing.
    """
    return bool(player.offhand and player.offhand.category == "weapon")


def combat_options(player):
    """Attack, plus an off-hand swing when one is held, then Use Item and Flee."""
    options = ["Attack"]
    if has_offhand_weapon(player):
        options.append("Off-hand Attack")
    options.append("Use Item")
    options.append("Flee")
    return options


def start_combat(player, enemy):
    while True:
        options = combat_options(player)
        has_off = has_offhand_weapon(player)
        idx_use = 2 if has_off else 1
        idx_flee = idx_use + 1
        choice = menu("COMBAT", options, body=combat_body(player, enemy))

        # Attack / Off-hand Attack - both cost the whole turn.
        if choice == 0 or (has_off and choice == 1):
            if choice == 0:
                player_attack(player, enemy)
            else:
                offhand_attack(player, enemy)
            if enemy.is_alive():
                # Burn and poison bite before the monster gets to swing back.
                tick_status(player, enemy)
                if not player.is_alive():
                    return False
                if enemy.is_alive():
                    enemy_attack(player, enemy)

        elif choice == idx_use:
            open_inventory(player)
            if not enemy.is_alive():
                return True
            tick_status(player, enemy)
            if not player.is_alive():
                return False
            if enemy.is_alive():
                enemy_attack(player, enemy)

        elif choice == idx_flee:
            if roll("1d20") >= 10:
                clear_screen()
                show(f"=== COMBAT ===\n")
                show(combat_body(player, enemy))
                show("You fled successfully!")
                press_any_key()
                return True
            else:
                clear_screen()
                show(f"=== COMBAT ===\n")
                show(combat_body(player, enemy))
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

    attack_mod = weapon_mod(player, player.weapon)

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

def offhand_attack(player, enemy):
    """The off-hand swing: its own hit roll, half damage.

    It is a whole turn of its own, so using it gives up the main-hand attack and
    lets the monster retaliate.
    """
    w = player.offhand
    clear_screen()
    show(f"=== COMBAT ===\n")
    show(combat_body(player, enemy))
    show(f"You swing {w.name} in your off-hand!\n")

    attack_mod = weapon_mod(player, w)
    atk_roll = roll("1d20") + prof_bonus(player.level) + attack_mod
    show(f"d20 + {prof_bonus(player.level)} + {attack_mod} = {atk_roll} vs AC {enemy.ac}")

    if atk_roll >= enemy.ac:
        # Half of (dice + modifier), rounded down, never less than 1. The
        # two-handed bonus is deliberately absent - it cannot be held anyway.
        full = max(roll(w.damage_dice) + attack_mod, 1)
        dmg = max(full // OFFHAND_DAMAGE_DIVISOR, 1)
        total, note = enemy.apply_damage(dmg, damage_type(w.damage_type))
        show(f"HIT! Dealt {total} damage!{note} (half damage) Enemy HP: {enemy.hp}/{enemy.max_hp}")
        effect = enemy.inflict_element(element_of(w), player)
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