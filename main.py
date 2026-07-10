from ui import clear_screen, show, menu, prompt, press_any_key
from player import create_character
from inventory import open_inventory
from shop import open_shop, SHOP_NPCS
from enemy import generate_enemy
from combat import start_combat
from save_load import save_game, load_game, list_saves, save_exists

def game_loop(player):
    while True:
        temp = menu("What now?", ["Open Inventory", "Visit Shop", "Fight", "Save Game", "Quit"])
        if temp == 0:
            open_inventory(player)
        elif temp == 1:
            shop_names = list(SHOP_NPCS.keys())
            shop_choice = menu("Which shop?", shop_names + ["(Back)"])
            if shop_choice < len(shop_names):
                open_shop(player, shop_names[shop_choice])
        elif temp == 2:
            if not start_combat(player, generate_enemy(player.level)):
                clear_screen()
                show("You have died...")
                press_any_key()
                break
        elif temp == 3:
            default_name = player.current_save or player.name
            save_name = prompt(f"Save name (default: {default_name})")
            if not save_name:
                save_name = default_name
            if save_exists(save_name):
                confirm = prompt(f"Save '{save_name}' already exists. Overwrite? (y/n)")
                if confirm.lower() != "y":
                    clear_screen()
                    show("Save cancelled.")
                    press_any_key()
                    continue
            save_game(player, save_name)
            player.current_save = save_name
            clear_screen()
            show(f"Game saved as '{save_name}'!")
            press_any_key()
        else:
            break

def main():
    while True:
        clear_screen()
        show("=== DUNGEONS & DRAGONS - TERMINAL EDITION ===\n")
        choice = menu("Main Menu", ["New Game", "Load Game", "Quit"])

        if choice == 0:
            player = create_character()
            clear_screen()
            show("=== CHARACTER CREATED! ===\n")
            show(player.sheet())
            show("")
            game_loop(player)

        elif choice == 1:
            saves = list_saves()
            if not saves:
                clear_screen()
                show("No save files found.")
                press_any_key()
            else:
                save_options = [f"{s[1]} {s[2]} {s[3]} Lv.{s[4]}" for s in saves]
                save_options.append("(Back)")
                idx = menu("Load Game", save_options)
                if idx < len(saves):
                    save_name = saves[idx][0]
                    player = load_game(save_name)
                    player.current_save = save_name
                    clear_screen()
                    show(f"Loaded '{save_name}'!")
                    press_any_key()
                    game_loop(player)

        elif choice == 2:
            clear_screen()
            show("Goodbye!")
            break

if __name__ == "__main__":
    main()
