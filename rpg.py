class Character:
    def __init__(self, name, hp=0, attack_power=0, inventory=None):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.inventory = inventory if inventory is not None else []

    def is_alive(self):
        return self.hp > 0

class NPC(Character):
    def __init__(self, name, dialogue, hp=0, attack_power=0, inventory=None):
        super().__init__(name, hp, attack_power, inventory)
        self.dialogue = dialogue

class Monster(Character):
    def __init__(self, name, monster_type, hp, attack_power, drops=None):
        super().__init__(name, hp, attack_power)
        self.monster_type = monster_type
        self.drops = drops if drops is not None else []

class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value

    def use(self, target):
        return f"You can't use {self.name}."

class Potion(Item):
    def __init__(self, name, description, value, heal_amount):
        super().__init__(name, description, value)
        self.heal_amount = heal_amount

    def use(self, target):
        target.hp += self.heal_amount
        return f"{target.name} uses the {self.name} and heals for {self.heal_amount} HP."

class OffensiveItem(Item):
    def __init__(self, name, description, value, damage_amount):
        super().__init__(name, description, value)
        self.damage_amount = damage_amount

    def use(self, target):
        target.hp -= self.damage_amount
        return f"You use the {self.name} on {target.name}, dealing {self.damage_amount} damage!"

class Container(Item):
    def __init__(self, name, description, value, contained_items=None):
        super().__init__(name, description, value)
        self.contained_items = contained_items if contained_items is not None else []

    def use(self, target_player):
        if not self.contained_items:
            return f"You open the {self.name}, but it's empty."

        message = f"You open the {self.name} and find:\n"
        for item in self.contained_items:
            target_player.inventory.append(item)
            message += f"- {item.name}\n"

        self.contained_items = []
        return message

class Location:
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None):
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.npcs = npcs if npcs is not None else []
        self.monsters = monsters if monsters is not None else []
        self.items = items if items is not None else []

    def describe(self, player):
        description = f"**{self.name}**\n"
        description += f"{self.description}\n"
        if self.npcs:
            description += "You see: " + ", ".join(npc.name for npc in self.npcs) + "\n"
        if self.monsters:
            description += "DANGER: " + ", ".join(monster.name for monster in self.monsters) + " is here!\n"
        if self.items:
            description += "On the ground: " + ", ".join(item.name for item in self.items) + "\n"
        return description

class CityLocation(Location):
    pass

class WildernessLocation(Location):
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None, spawn_chance=0.0):
        super().__init__(name, description, exits, npcs, monsters, items)
        self.spawn_chance = spawn_chance

class DungeonLocation(Location):
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None, hazard_description=""):
        super().__init__(name, description, exits, npcs, monsters, items)
        self.hazard_description = hazard_description

    def describe(self, player):
        base_description = super().describe(player)
        return base_description + self.hazard_description + "\n"

class SwampLocation(WildernessLocation):
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None, spawn_chance=0.0, hidden_description=""):
        super().__init__(name, description, exits, npcs, monsters, items, spawn_chance)
        self.hidden_description = hidden_description

    def describe(self, player):
        has_lantern = any(item.name == "Lantern" for item in player.inventory)
        if has_lantern:
            return super().describe(player)
        else:
            return self.hidden_description

class Player(Character):
    def __init__(self, name, current_location, hp=20, attack_power=5):
        super().__init__(name, hp, attack_power)
        self.current_location = current_location
        self.previous_location = current_location

    def move(self, direction):
        if direction in self.current_location.exits:
            self.previous_location = self.current_location
            self.current_location = self.current_location.exits[direction]
            return True
        else:
            return False

    def retreat(self):
        self.current_location = self.previous_location

import os
import platform
import json
import random

def clear_screen():
    """Clears the console screen."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def select_from_menu(prompt, options, display_key='name'):
    """Displays a numbered menu of options and returns the selected option or None."""
    print(prompt)
    for i, option in enumerate(options):
        print(f"  {i + 1}. {getattr(option, display_key)}")
    print(f"  {len(options) + 1}. Cancel")

    while True:
        choice = input("> ")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
            elif choice_index == len(options):
                return None # Cancel
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_menu_and_state(player, message, actions, game_mode):
    """Clears the screen, displays player status, a message, and a numbered action menu."""
    clear_screen()

    print("=" * 40)
    print(f"| {player.name:<10} | HP: {player.hp:<4} | Location: {player.current_location.name:<15} |")
    print("=" * 40)

    if game_mode in ["encounter", "combat"] and player.current_location.monsters:
        print("\nENEMIES:")
        for i, monster in enumerate(player.current_location.monsters):
            print(f"  {i + 1}. {monster.name} (HP: {monster.hp})")

    print(f"\n{message}\n")

    print("-" * 40)
    print("What do you do?")
    for i, action in enumerate(actions):
        print(f"  {i + 1}. {action['text']}")
    print("-" * 40)

def get_available_actions(player, game_mode, menus):
    """Generates a list of available actions for the player based on JSON menu definitions."""
    actions = []
    # The 'encounter' mode is removed, so we only check for 'explore' and 'combat'
    menu_definitions = menus.get(game_mode, []) + menus.get("always", [])

    for definition in menu_definitions:
        # Simple action, no conditions or iterations
        if "iterate" not in definition and "condition" not in definition:
            actions.append(definition.copy())
            continue

        # Check condition for non-iterated actions
        if "condition" in definition and "iterate" not in definition:
            if definition["condition"] == "player.inventory" and not player.inventory:
                continue
            if definition["condition"] == "has_usable_item" and not any(isinstance(item, (Potion, OffensiveItem)) for item in player.inventory):
                continue
            actions.append(definition.copy())

        # Handle iterated actions
        if "iterate" in definition:
            iterator_key = definition["iterate"]
            source_list = []
            if iterator_key == "location.exits":
                source_list = player.current_location.exits.items()
            elif iterator_key == "location.npcs":
                source_list = player.current_location.npcs
            elif iterator_key == "location.items":
                source_list = player.current_location.items
            elif iterator_key == "player.inventory":
                source_list = player.inventory
            elif iterator_key == "location.monsters":
                source_list = player.current_location.monsters

            for it in source_list:
                # Check condition for iterated actions
                if "condition" in definition:
                    if definition["condition"] == "is_potion" and not isinstance(it, Potion):
                        continue

                action = definition.copy()
                if iterator_key == "location.exits":
                    direction, dest = it
                    action['text'] = definition["text"].format(direction=direction, destination=dest)
                    action['command'] = definition["command"].format(direction=direction)
                elif iterator_key == "location.npcs":
                    action['text'] = definition["text"].format(npc=it)
                    action['command'] = definition["command"].format(npc=it)
                elif iterator_key == "location.items":
                    action['text'] = definition["text"].format(item=it)
                    action['command'] = definition["command"].format(item=it)
                elif iterator_key == "player.inventory":
                    action['text'] = definition["text"].format(item=it)
                    action['command'] = definition["command"].format(item=it)
                elif iterator_key == "location.monsters":
                    action['text'] = definition["text"].format(monster=it)
                    action['command'] = definition["command"].format(monster=it)

                actions.append(action)
    return actions

def load_game_data(filepath):
    """Loads game data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_world_from_data(game_data):
    """Creates all game objects from the normalized data and links them."""
    all_items = {}
    for item_id, item_data in game_data.get("items", {}).items():
        item_type = item_data.get("item_type", "Item")
        if item_type == "Potion":
            all_items[item_id] = Potion(item_data["name"], item_data["description"], item_data.get("value", 0), item_data.get("heal_amount", 0))
        elif item_type == "Container":
            all_items[item_id] = Container(item_data["name"], item_data["description"], item_data.get("value", 0))
        elif item_type == "OffensiveItem":
            all_items[item_id] = OffensiveItem(item_data["name"], item_data["description"], item_data.get("value", 0), item_data.get("damage_amount", 0))
        else:
            all_items[item_id] = Item(item_data["name"], item_data["description"], item_data.get("value", 0))

    all_monsters = {}
    for monster_id, monster_data in game_data.get("monsters", {}).items():
        all_monsters[monster_id] = Monster(
            monster_data["name"], monster_data["monster_type"], monster_data["hp"], monster_data["attack_power"]
        )

    all_npcs = {}
    for npc_id, npc_data in game_data.get("npcs", {}).items():
        all_npcs[npc_id] = NPC(npc_data["name"], npc_data["dialogue"], npc_data["hp"], npc_data["attack_power"])

    all_locations = {}
    for loc_id, loc_data in game_data.get("locations", {}).items():
        loc_type = loc_data.get("location_type", "base")
        if loc_type == "City":
            all_locations[loc_id] = CityLocation(
                loc_data["name"], loc_data["description"]
            )
        elif loc_type == "Wilderness":
            all_locations[loc_id] = WildernessLocation(
                loc_data["name"], loc_data["description"],
                spawn_chance=loc_data.get("spawn_chance", 0.0)
            )
        elif loc_type == "Dungeon":
            all_locations[loc_id] = DungeonLocation(
                loc_data["name"], loc_data["description"],
                hazard_description=loc_data.get("hazard_description", "")
            )
        elif loc_type == "Swamp":
            all_locations[loc_id] = SwampLocation(
                loc_data["name"], loc_data["description"],
                spawn_chance=loc_data.get("spawn_chance", 0.0),
                hidden_description=loc_data.get("hidden_description", "")
            )
        else:
            all_locations[loc_id] = Location(
                loc_data["name"], loc_data["description"]
            )

    # --- Linking Pass ---
    for loc_id, loc_data in game_data.get("locations", {}).items():
        location = all_locations[loc_id]
        location.exits = {direction: all_locations[dest_id] for direction, dest_id in loc_data.get("exits", {}).items()}
        location.npcs = [all_npcs[npc_id] for npc_id in loc_data.get("npc_ids", [])]
        location.monsters = [all_monsters[monster_id] for monster_id in loc_data.get("monster_ids", [])]
        location.items = [all_items[item_id] for item_id in loc_data.get("item_ids", [])]

    for monster_id, monster_data in game_data.get("monsters", {}).items():
        monster = all_monsters[monster_id]
        monster.drops = [all_items[item_id] for item_id in monster_data.get("drop_ids", [])]

    for item_id, item_data in game_data.get("items", {}).items():
        if item_data.get("item_type") == "Container":
            container = all_items[item_id]
            container.contained_items = [all_items[i_id] for i_id in item_data.get("contained_item_ids", [])]

    # --- Player Creation ---
    player_data = game_data["player"]
    start_location = all_locations[player_data["start_location_id"]]
    inventory = [all_items[item_id] for item_id in player_data.get("inventory", [])]
    player = Player(
        player_data["name"], start_location, player_data["hp"], player_data["attack_power"]
    )
    player.inventory = inventory

    return player, game_data.get("menus", {})

def main():
    game_data = load_game_data("game_data.json")
    player, menus = load_world_from_data(game_data)
    game_mode = "explore"
    message = player.current_location.describe(player)
    combat_loot = []

    while player.is_alive():
        # --- State Transition Check ---
        if game_mode == "explore" and player.current_location.monsters:
            game_mode = "combat"
            monster_names = " and a ".join(m.name for m in player.current_location.monsters)
            message = f"You step into the {player.current_location.name}... {monster_names} block(s) your way!"
            combat_loot = [] # Initialize loot for the upcoming battle

        # --- UI and Input ---
        available_actions = get_available_actions(player, game_mode, menus)
        display_menu_and_state(player, message, available_actions, game_mode)

        choice = input("> ")
        try:
            choice_index = int(choice) - 1
            if not (0 <= choice_index < len(available_actions)):
                message = "Invalid choice."
                continue
            command = available_actions[choice_index]['command']
        except ValueError:
            message = "Please enter a number."
            continue

        parts = command.split()
        verb = parts[0]
        message = "" # Reset message each turn
        player_turn_taken = False

        # --- Command Processing ---
        if verb == "quit":
            print("Thanks for playing!")
            break

        # --- EXPLORE MODE ---
        if game_mode == "explore":
            player_turn_taken = True # Most explore actions take a "turn"
            if verb == "look":
                message = player.current_location.describe(player)
            elif verb == "go":
                direction = parts[1]
                if player.move(direction):
                    message = f"You go {direction}."
                else:
                    message = "You can't go that way."
            elif verb == "get":
                item_name = " ".join(parts[1:]).strip("'")
                item = next((i for i in player.current_location.items if i.name.lower() == item_name.lower()), None)
                if item:
                    player.inventory.append(item)
                    player.current_location.items.remove(item)
                    message = f"You pick up the {item.name}."
                else:
                    message = "You don't see that here."
            elif verb == "inventory":
                message = "You are carrying:\n" + "\n".join(f"- {item.name}" for item in player.inventory) if player.inventory else "Your inventory is empty."
            elif verb == "use":
                item = next((i for i in player.inventory if i.name.lower() == " ".join(parts[1:]).strip("'").lower()), None)
                if item:
                    message = item.use(player)
                    if isinstance(item, (Potion, Container)):
                        player.inventory.remove(item)
                else:
                    message = "You don't have that item."

        # --- COMBAT MODE ---
        elif game_mode == "combat":
            active_monsters = player.current_location.monsters

            if verb == "attack":
                target = None
                if len(active_monsters) == 1:
                    target = active_monsters[0]
                else:
                    target = select_from_menu("\nWhich enemy to attack?", active_monsters)

                if target:
                    message = f"You attack the {target.name}, dealing {player.attack_power} damage."
                    target.hp -= player.attack_power
                    player_turn_taken = True
                else:
                    message = "You decided not to attack."

            elif verb == "use":
                usable_items = [item for item in player.inventory if isinstance(item, (Potion, OffensiveItem))]
                if not usable_items:
                    message = "You have no usable items in combat."
                else:
                    item_to_use = select_from_menu("\nWhich item to use?", usable_items)
                    if item_to_use:
                        if isinstance(item_to_use, OffensiveItem):
                            target = select_from_menu(f"\nUse {item_to_use.name} on which enemy?", active_monsters)
                            if target:
                                message = item_to_use.use(target)
                                player.inventory.remove(item_to_use)
                                player_turn_taken = True
                            else:
                                message = "You decided not to use the item."
                        else: # Potion
                            message = item_to_use.use(player)
                            player.inventory.remove(item_to_use)
                            player_turn_taken = True
                    else:
                        message = "You decided not to use an item."

            elif verb == "retreat":
                retreat_message = "You flee from combat!"
                monsters_left_behind = player.current_location.monsters[:]

                for monster in monsters_left_behind:
                    if random.random() < 0.5: # 50% chance
                        player.hp -= monster.attack_power
                        retreat_message += f"\nThe {monster.name} strikes you for {monster.attack_power} damage as you escape!"
                    else:
                        retreat_message += f"\nThe {monster.name} swipes at you but misses!"

                if player.is_alive():
                    # Create summary before moving
                    threat_summary = f"The {player.current_location.name} still harbors danger: " + ", ".join(f"{m.name} ({m.hp} HP)" for m in monsters_left_behind)
                    player.retreat()
                    message = f"{retreat_message}\n\nYou escaped back to {player.current_location.name}.\n\n{threat_summary}"
                else:
                    message = retreat_message # Let the main loop handle death

                game_mode = "explore"
                player_turn_taken = True

            # --- Post-Action Resolution ---
            if player_turn_taken:
                # Check for defeated monsters
                defeated_monsters = [m for m in active_monsters if not m.is_alive()]
                if defeated_monsters:
                    for m in defeated_monsters:
                        message += f"\nYou have defeated the {m.name}!"
                        if m.drops:
                            combat_loot.extend(m.drops)
                    player.current_location.monsters = [m for m in active_monsters if m.is_alive()]

                # Check for victory
                if not player.current_location.monsters:
                    message = f"Victory! You have defeated all enemies in the {player.current_location.name}."
                    if combat_loot:
                        message += "\nYou found:\n" + "\n".join(f"- {item.name}" for item in combat_loot)
                        player.current_location.items.extend(combat_loot)
                    game_mode = "explore"
                # Enemy turn
                elif game_mode == "combat":
                    enemy_turn_message = ""
                    for monster in player.current_location.monsters:
                        player.hp -= monster.attack_power
                        enemy_turn_message += f"\nThe {monster.name} attacks you, dealing {monster.attack_power} damage."
                    message += enemy_turn_message

    if not player.is_alive():
        print(f"\n{message}")
        print("\nYou have been defeated. Game Over.")

if __name__ == "__main__":
    main()
